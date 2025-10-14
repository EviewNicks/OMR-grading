#!/usr/bin/env python3
"""
Rotation-Robust Detection Test Runner
Test script untuk comprehensive rotation detection testing dengan real dataset
"""

import cv2
import numpy as np
import json
import time
from pathlib import Path
import sys
import logging
from typing import Dict, List, Tuple, Optional
import pandas as pd

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig, TemplateDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector, ContourDetectionResult

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RotationDetectionTester:
    """Comprehensive tester untuk rotation-robust contour detection"""

    def __init__(self, dataset_path: str, output_dir: str = "test_results"):
        """
        Initialize tester

        Args:
            dataset_path: Path ke test dataset
            output_dir: Directory untuk saving results
        """
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize detectors dengan ultra-relaxed parameters
        self.rotation_config = ContourDetectionConfig(
            min_area=500,
            max_area=100000,
            aspect_ratio_min=0.05,
            aspect_ratio_max=5.0,
            rectangularity_threshold=0.4,
            approximation_epsilon=0.02,
            hierarchy_level=2,

            # Ultra-relaxed rotation-robust parameters
            min_area_ratio=0.01,
            max_area_ratio=0.90,
            min_aspect_ratio=0.01,
            max_aspect_ratio=0.95,
            min_rectangularity=0.30,

            # Control flags
            use_rotation_robust=True,
            use_hybrid_threshold=True
        )

        self.traditional_config = ContourDetectionConfig(
            min_area=500,
            max_area=100000,
            aspect_ratio_min=0.05,
            aspect_ratio_max=5.0,
            rectangularity_threshold=0.4,
            approximation_epsilon=0.02,
            hierarchy_level=2,

            # Traditional parameters (relaxed)
            use_rotation_robust=False,
            use_hybrid_threshold=False
        )

        self.rotation_detector = ContourGridDetector(self.rotation_config)
        self.traditional_detector = ContourGridDetector(self.traditional_config)

    def load_image(self, image_path: Path) -> Optional[np.ndarray]:
        """Load image dari path"""
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Cannot load image: {image_path}")
                return None
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {str(e)}")
            return None

    def test_single_image(self, image_path: Path) -> Dict:
        """
        Test single image dengan both traditional dan rotation-robust methods

        Args:
            image_path: Path ke image

        Returns:
            Dictionary dengan test results
        """
        image = self.load_image(image_path)
        if image is None:
            return {
                'filename': image_path.name,
                'error': 'Cannot load image',
                'traditional_confidence': 0.0,
                'rotation_confidence': 0.0,
                'traditional_time': 0.0,
                'rotation_time': 0.0
            }

        # Test traditional method
        start_time = time.time()
        traditional_result = self.traditional_detector.detect_grid(image)
        traditional_time = time.time() - start_time

        # Test rotation-robust method
        start_time = time.time()
        rotation_result = self.rotation_detector.detect_grid(image)
        rotation_time = time.time() - start_time

        return {
            'filename': image_path.name,
            'traditional_confidence': traditional_result.confidence,
            'rotation_confidence': rotation_result.confidence,
            'traditional_time': traditional_time,
            'rotation_time': rotation_time,
            'traditional_success': traditional_result.confidence > 0.5,
            'rotation_success': rotation_result.confidence > 0.5,
            'rotation_angle': rotation_result.angle,
            'rotation_corners': rotation_result.grid_corners,
            'traditional_coords': traditional_result.grid_coordinates,
            'rotation_coords': rotation_result.grid_coordinates,
            'improvement': rotation_result.confidence - traditional_result.confidence,
            'time_improvement': traditional_time - rotation_time
        }

    def test_dataset(self, max_images: Optional[int] = None) -> List[Dict]:
        """
        Test entire dataset

        Args:
            max_images: Maximum number of images to test (None = all)

        Returns:
            List of test results
        """
        if not self.dataset_path.exists():
            logger.error(f"Dataset path not found: {self.dataset_path}")
            return []

        # Get image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        for ext in image_extensions:
            image_files.extend(self.dataset_path.glob(f"*{ext}"))
            image_files.extend(self.dataset_path.glob(f"*{ext.upper()}"))

        image_files = sorted(image_files)

        if max_images:
            image_files = image_files[:max_images]

        logger.info(f"Testing {len(image_files)} images from {self.dataset_path}")

        results = []
        for i, image_path in enumerate(image_files, 1):
            logger.info(f"Testing {i}/{len(image_files)}: {image_path.name}")

            result = self.test_single_image(image_path)
            results.append(result)

            # Log progress
            if i % 5 == 0:
                traditional_success = sum(1 for r in results if r['traditional_success'])
                rotation_success = sum(1 for r in results if r['rotation_success'])
                logger.info(f"Progress: {i} images tested")
                logger.info(f"Traditional success: {traditional_success}/{i} ({traditional_success/i*100:.1f}%)")
                logger.info(f"Rotation-robust success: {rotation_success}/{i} ({rotation_success/i*100:.1f}%)")

        return results

    def analyze_results(self, results: List[Dict]) -> Dict:
        """
        Analyze test results

        Args:
            results: List of test results

        Returns:
            Dictionary dengan analysis results
        """
        if not results:
            return {}

        total_images = len(results)
        traditional_success = sum(1 for r in results if r['traditional_success'])
        rotation_success = sum(1 for r in results if r['rotation_success'])

        traditional_confidences = [r['traditional_confidence'] for r in results]
        rotation_confidences = [r['rotation_confidence'] for r in results]

        improvements = [r['improvement'] for r in results]
        time_improvements = [r['time_improvement'] for r in results]

        analysis = {
            'total_images': total_images,
            'traditional_success_count': traditional_success,
            'rotation_success_count': rotation_success,
            'traditional_success_rate': traditional_success / total_images,
            'rotation_success_rate': rotation_success / total_images,
            'success_rate_improvement': (rotation_success - traditional_success) / total_images,

            # Confidence statistics
            'traditional_avg_confidence': np.mean(traditional_confidences),
            'rotation_avg_confidence': np.mean(rotation_confidences),
            'confidence_improvement': np.mean(improvements),
            'max_confidence_improvement': max(improvements),
            'min_confidence_improvement': min(improvements),

            # Performance statistics
            'traditional_avg_time': np.mean([r['traditional_time'] for r in results]),
            'rotation_avg_time': np.mean([r['rotation_time'] for r in results]),
            'avg_time_improvement': np.mean(time_improvements),

            # Success categories
            'both_failed': sum(1 for r in results if not r['traditional_success'] and not r['rotation_success']),
            'traditional_only': sum(1 for r in results if r['traditional_success'] and not r['rotation_success']),
            'rotation_only': sum(1 for r in results if not r['traditional_success'] and r['rotation_success']),
            'both_success': sum(1 for r in results if r['traditional_success'] and r['rotation_success']),

            # Rotation detection
            'rotation_detected_count': sum(1 for r in results if r['rotation_angle'] is not None),
            'avg_detected_angle': np.mean([r['rotation_angle'] for r in results if r['rotation_angle'] is not None])
        }

        return analysis

    def save_results(self, results: List[Dict], analysis: Dict) -> None:
        """
        Save test results ke files

        Args:
            results: List of test results
            analysis: Analysis results
        """
        # Save detailed results
        results_file = self.output_dir / "rotation_detection_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Detailed results saved to: {results_file}")

        # Save analysis
        analysis_file = self.output_dir / "rotation_detection_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        logger.info(f"Analysis saved to: {analysis_file}")

        # Save CSV
        df = pd.DataFrame(results)
        csv_file = self.output_dir / "rotation_detection_results.csv"
        df.to_csv(csv_file, index=False)
        logger.info(f"CSV results saved to: {csv_file}")

        # Create summary report
        self.create_summary_report(analysis)

    def create_summary_report(self, analysis: Dict) -> None:
        """
        Create summary report

        Args:
            analysis: Analysis results
        """
        report_file = self.output_dir / "summary_report.md"

        with open(report_file, 'w') as f:
            f.write("# Rotation-Robust Contour Detection Test Results\n\n")
            f.write(f"**Dataset**: {self.dataset_path}\n")
            f.write(f"**Total Images**: {analysis['total_images']}\n")
            f.write(f"**Test Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Success Rate Comparison\n\n")
            f.write("| Method | Success Count | Success Rate |\n")
            f.write("|--------|---------------|-------------|\n")
            f.write(f"| Traditional | {analysis['traditional_success_count']} | {analysis['traditional_success_rate']*100:.1f}% |\n")
            f.write(f"| Rotation-Robust | {analysis['rotation_success_count']} | {analysis['rotation_success_rate']*100:.1f}% |\n")
            f.write(f"| **Improvement** | **+{analysis['success_rate_improvement']*100:.1f}%** | **{analysis['success_rate_improvement']*100:.1f}%** |\n\n")

            f.write("## Performance Comparison\n\n")
            f.write("| Metric | Traditional | Rotation-Robust | Improvement |\n")
            f.write("|--------|-------------|-----------------|-------------|\n")
            f.write(f"| Avg Confidence | {analysis['traditional_avg_confidence']:.3f} | {analysis['rotation_avg_confidence']:.3f} | {analysis['confidence_improvement']:+.3f} |\n")
            f.write(f"| Avg Processing Time | {analysis['traditional_avg_time']:.3f}s | {analysis['rotation_avg_time']:.3f}s | {analysis['avg_time_improvement']:+.3f}s |\n\n")

            f.write("## Success Categories\n\n")
            f.write(f"- **Both Failed**: {analysis['both_failed']} images\n")
            f.write(f"- **Traditional Only**: {analysis['traditional_only']} images\n")
            f.write(f"- **Rotation-Robust Only**: {analysis['rotation_only']} images\n")
            f.write(f"- **Both Success**: {analysis['both_success']} images\n\n")

            f.write("## Rotation Detection\n\n")
            if analysis['rotation_detected_count'] > 0:
                f.write(f"- Images with detected rotation: {analysis['rotation_detected_count']}/{analysis['total_images']}\n")
                f.write(f"- Average detected angle: {analysis['avg_detected_angle']:.1f}°\n\n")
            else:
                f.write("- No rotation angles detected\n\n")

            f.write("## Conclusion\n\n")
            if analysis['success_rate_improvement'] > 0:
                f.write(f"✅ **Rotation-robust detection shows {analysis['success_rate_improvement']*100:.1f}% improvement in success rate**\n")
            else:
                f.write(f"⚠️ **Rotation-robust detection shows {abs(analysis['success_rate_improvement'])*100:.1f}% decrease in success rate**\n")

            if analysis['confidence_improvement'] > 0:
                f.write(f"✅ **Average confidence improved by {analysis['confidence_improvement']:.3f}**\n")
            else:
                f.write(f"⚠️ **Average confidence decreased by {abs(analysis['confidence_improvement']):.3f}**\n")

        logger.info(f"Summary report saved to: {report_file}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test rotation-robust contour detection")
    parser.add_argument("--dataset", "-d", required=True, help="Path ke test dataset")
    parser.add_argument("--output", "-o", default="test_results", help="Output directory")
    parser.add_argument("--max-images", "-n", type=int, help="Maximum number of images to test")

    args = parser.parse_args()

    # Initialize tester
    tester = RotationDetectionTester(args.dataset, args.output)

    # Run tests
    logger.info("Starting rotation-robust detection tests...")
    results = tester.test_dataset(args.max_images)

    if not results:
        logger.error("No results generated. Check dataset path.")
        return

    # Analyze results
    logger.info("Analyzing results...")
    analysis = tester.analyze_results(results)

    # Save results
    logger.info("Saving results...")
    tester.save_results(results, analysis)

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    logger.info(f"Total images tested: {analysis['total_images']}")
    logger.info(f"Traditional success rate: {analysis['traditional_success_rate']*100:.1f}%")
    logger.info(f"Rotation-robust success rate: {analysis['rotation_success_rate']*100:.1f}%")
    logger.info(f"Success rate improvement: {analysis['success_rate_improvement']*100:.1f}%")
    logger.info(f"Confidence improvement: {analysis['confidence_improvement']:+.3f}")
    logger.info(f"Results saved to: {args.output}")
    logger.info("="*80)


if __name__ == "__main__":
    main()