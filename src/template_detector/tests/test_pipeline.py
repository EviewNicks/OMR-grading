"""
Week 6 - Template Detection & Segmentation
Testing Framework untuk End-to-End Pipeline

Test suite komprehensif untuk validasi implementasi Week 6:
- Unit tests untuk setiap komponen
- Integration tests untuk pipeline
- Performance benchmarking
- Quality assessment validation

Author: Week 6 Implementation
Date: 2024-09-29
Academic Context: Digital Image Processing Course
"""

import pytest
import cv2
import numpy as np
import time
from typing import List, Dict, Any
import logging

# Import semua komponen yang akan ditest
from template_detector import (
    OMRPipeline, OMRProcessingResult,
    ContourGridDetector, HoughLineDetector, TemplateMatchingDetector,
    DetectionFusion, GridNormalizer, CellExtractor, BubbleDetector,
    TemplateDetectionConfig
)

class TestPipelineFramework:
    """
    Comprehensive testing framework untuk Week 6 implementation
    """

    @classmethod
    def setup_class(cls):
        """Setup untuk test class"""
        cls.config = TemplateDetectionConfig()
        cls.pipeline = OMRPipeline(cls.config)
        cls.logger = logging.getLogger(__name__)

        # Create sample test images
        cls.test_images = cls._create_test_images()

    @classmethod
    def _create_test_images(cls) -> List[np.ndarray]:
        """
        Create synthetic test images untuk testing

        Returns:
            List of test images dengan berbagai scenarios
        """
        test_images = []

        # Test Image 1: Perfect grid dengan clear bubbles
        perfect_grid = cls._create_perfect_grid_image()
        test_images.append(perfect_grid)

        # Test Image 2: Slightly rotated grid
        rotated_grid = cls._create_rotated_grid_image(angle=5)
        test_images.append(rotated_grid)

        # Test Image 3: Noisy image dengan distortions
        noisy_grid = cls._create_noisy_grid_image()
        test_images.append(noisy_grid)

        # Test Image 4: Low contrast image
        low_contrast_grid = cls._create_low_contrast_grid_image()
        test_images.append(low_contrast_grid)

        return test_images

    @classmethod
    def _create_perfect_grid_image(cls) -> np.ndarray:
        """Create perfect OMR grid image"""
        # Create white background
        image = np.ones((800, 600), dtype=np.uint8) * 255

        # Draw grid lines untuk 20x3 answer grid
        rows, cols = 20, 3
        cell_width = 180
        cell_height = 35

        start_x, start_y = 50, 50

        # Horizontal lines
        for i in range(rows + 1):
            y = start_y + i * cell_height
            cv2.line(image, (start_x, y), (start_x + cols * cell_width, y), 0, 2)

        # Vertical lines
        for j in range(cols + 1):
            x = start_x + j * cell_width
            cv2.line(image, (x, start_y), (x, start_y + rows * cell_height), 0, 2)

        # Add bubbles dalam setiap cell (5 bubbles per cell untuk A-E)
        bubble_radius = 8
        bubbles_per_cell = 5

        for row in range(rows):
            for col in range(cols):
                cell_x = start_x + col * cell_width
                cell_y = start_y + row * cell_height

                for bubble_idx in range(bubbles_per_cell):
                    bubble_x = cell_x + 20 + bubble_idx * 30
                    bubble_y = cell_y + cell_height // 2

                    # Draw empty bubble
                    cv2.circle(image, (bubble_x, bubble_y), bubble_radius, 0, 2)

                    # Randomly fill some bubbles untuk testing
                    if np.random.random() < 0.2:  # 20% chance filled
                        cv2.circle(image, (bubble_x, bubble_y), bubble_radius-2, 0, -1)

        return image

    @classmethod
    def _create_rotated_grid_image(cls, angle: float) -> np.ndarray:
        """Create rotated grid image"""
        perfect_grid = cls._create_perfect_grid_image()

        # Rotate image
        height, width = perfect_grid.shape
        center = (width // 2, height // 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(perfect_grid, rotation_matrix, (width, height),
                               borderValue=255)

        return rotated

    @classmethod
    def _create_noisy_grid_image(cls) -> np.ndarray:
        """Create noisy grid image dengan distortions"""
        perfect_grid = cls._create_perfect_grid_image()

        # Add Gaussian noise
        noise = np.random.normal(0, 10, perfect_grid.shape)
        noisy = np.clip(perfect_grid.astype(float) + noise, 0, 255).astype(np.uint8)

        # Add some random spots
        for _ in range(50):
            x = np.random.randint(0, noisy.shape[1])
            y = np.random.randint(0, noisy.shape[0])
            cv2.circle(noisy, (x, y), np.random.randint(1, 3), 0, -1)

        return noisy

    @classmethod
    def _create_low_contrast_grid_image(cls) -> np.ndarray:
        """Create low contrast grid image"""
        perfect_grid = cls._create_perfect_grid_image()

        # Reduce contrast
        low_contrast = perfect_grid * 0.7 + 50
        low_contrast = np.clip(low_contrast, 0, 255).astype(np.uint8)

        return low_contrast

    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        assert self.pipeline is not None
        assert self.pipeline.config is not None
        assert hasattr(self.pipeline, 'contour_detector')
        assert hasattr(self.pipeline, 'hough_detector')
        assert hasattr(self.pipeline, 'template_detector')
        assert hasattr(self.pipeline, 'detection_fusion')
        assert hasattr(self.pipeline, 'grid_normalizer')
        assert hasattr(self.pipeline, 'cell_extractor')
        assert hasattr(self.pipeline, 'bubble_detector')

    def test_pipeline_processing_perfect_image(self):
        """Test pipeline dengan perfect grid image"""
        perfect_image = self.test_images[0]
        result = self.pipeline.process_omr_image(perfect_image)

        # Basic validations
        assert isinstance(result, OMRProcessingResult)
        assert result.grid_detection['success'] == True
        assert result.confidence_score > 0.5
        assert result.processing_time > 0
        assert len(result.extracted_cells) > 0
        assert len(result.detected_answers) > 0

        self.logger.info(f"Perfect image - Confidence: {result.confidence_score:.3f}, "
                        f"Cells: {len(result.extracted_cells)}, "
                        f"Answers: {len(result.detected_answers)}")

    def test_pipeline_processing_rotated_image(self):
        """Test pipeline dengan rotated image"""
        rotated_image = self.test_images[1]
        result = self.pipeline.process_omr_image(rotated_image)

        # Should still work reasonably well
        assert isinstance(result, OMRProcessingResult)
        assert result.processing_time > 0

        # Performance might be lower but should be acceptable
        if result.grid_detection['success']:
            assert result.confidence_score > 0.3  # Lower threshold untuk rotated

        self.logger.info(f"Rotated image - Confidence: {result.confidence_score:.3f}, "
                        f"Success: {result.grid_detection['success']}")

    def test_pipeline_processing_noisy_image(self):
        """Test pipeline dengan noisy image"""
        noisy_image = self.test_images[2]
        result = self.pipeline.process_omr_image(noisy_image)

        assert isinstance(result, OMRProcessingResult)
        assert result.processing_time > 0

        self.logger.info(f"Noisy image - Confidence: {result.confidence_score:.3f}, "
                        f"Success: {result.grid_detection['success']}")

    def test_pipeline_processing_low_contrast(self):
        """Test pipeline dengan low contrast image"""
        low_contrast_image = self.test_images[3]
        result = self.pipeline.process_omr_image(low_contrast_image)

        assert isinstance(result, OMRProcessingResult)
        assert result.processing_time > 0

        self.logger.info(f"Low contrast - Confidence: {result.confidence_score:.3f}, "
                        f"Success: {result.grid_detection['success']}")

    def test_individual_detectors(self):
        """Test individual detection methods"""
        test_image = self.test_images[0]

        # Test contour detector
        contour_result = self.pipeline.contour_detector.detect_grid(test_image)
        assert contour_result is not None

        # Test hough detector
        hough_result = self.pipeline.hough_detector.detect_grid(test_image)
        assert hough_result is not None

        # Test template detector
        template_result = self.pipeline.template_detector.detect_grid(test_image)
        assert template_result is not None

        self.logger.info("Individual detectors test passed")

    def test_grid_normalization(self):
        """Test grid normalization dengan sample corners"""
        test_image = self.test_images[0]

        # Create sample grid corners
        sample_corners = np.array([
            [50, 50],      # top-left
            [590, 50],     # top-right
            [590, 750],    # bottom-right
            [50, 750]      # bottom-left
        ], dtype=np.float32)

        normalized = self.pipeline.grid_normalizer.normalize_perspective(
            test_image, sample_corners
        )

        assert normalized is not None
        assert len(normalized.shape) == 2  # Grayscale
        assert normalized.shape[0] > 0 and normalized.shape[1] > 0

        self.logger.info(f"Grid normalization test passed - Shape: {normalized.shape}")

    def test_cell_extraction(self):
        """Test cell extraction dari normalized grid"""
        test_image = self.test_images[0]

        # Use a portion of test image as normalized grid
        normalized_grid = test_image[50:750, 50:590]

        # Test adaptive extraction
        adaptive_result = self.pipeline.cell_extractor.extract_cells_adaptive(normalized_grid)
        assert 'cells' in adaptive_result
        assert 'quality' in adaptive_result

        # Test uniform extraction
        uniform_result = self.pipeline.cell_extractor.extract_cells_uniform(normalized_grid)
        assert 'cells' in uniform_result
        assert 'quality' in uniform_result

        self.logger.info(f"Cell extraction test passed - "
                        f"Adaptive: {len(adaptive_result['cells'])} cells, "
                        f"Uniform: {len(uniform_result['cells'])} cells")

    def test_bubble_detection(self):
        """Test bubble detection dalam extracted cells"""
        # Create sample cell image dengan bubbles
        cell_image = np.ones((35, 180), dtype=np.uint8) * 255

        # Draw 5 bubbles (A-E choices)
        for i in range(5):
            center_x = 20 + i * 30
            center_y = 17
            cv2.circle(cell_image, (center_x, center_y), 8, 0, 2)

            # Fill first bubble (choice A)
            if i == 0:
                cv2.circle(cell_image, (center_x, center_y), 6, 0, -1)

        # Test bubble detection
        result = self.pipeline.bubble_detector.detect_bubbles_in_cell(cell_image)

        assert hasattr(result, 'bubbles')
        assert hasattr(result, 'detection_confidence')
        assert result.processing_time > 0

        # Should detect bubbles
        assert len(result.bubbles) > 0

        self.logger.info(f"Bubble detection test passed - "
                        f"Detected: {len(result.bubbles)} bubbles, "
                        f"Confidence: {result.detection_confidence:.3f}")

    def test_batch_processing(self):
        """Test batch processing multiple images"""
        results = self.pipeline.process_batch(self.test_images)

        assert len(results) == len(self.test_images)
        assert all(isinstance(r, OMRProcessingResult) for r in results)

        # Performance summary
        summary = self.pipeline.get_performance_summary(results)
        assert 'total_images' in summary
        assert 'success_rate' in summary
        assert 'processing_time' in summary

        self.logger.info(f"Batch processing test passed - "
                        f"Images: {summary['total_images']}, "
                        f"Success rate: {summary['success_rate']:.3f}")

    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        test_image = self.test_images[0]

        # Measure processing time
        start_time = time.time()
        result = self.pipeline.process_omr_image(test_image)
        processing_time = time.time() - start_time

        # Performance assertions
        assert processing_time < 10.0  # Should complete within 10 seconds
        assert result.processing_time < 10.0

        # Quality assertions untuk perfect image
        if result.grid_detection['success']:
            assert result.confidence_score > 0.6
            assert result.grid_quality > 0.5

        self.logger.info(f"Performance benchmark - "
                        f"Time: {processing_time:.2f}s, "
                        f"Confidence: {result.confidence_score:.3f}")

    def test_error_handling(self):
        """Test error handling dengan invalid inputs"""
        # Test dengan empty image
        empty_image = np.zeros((100, 100), dtype=np.uint8)
        result = self.pipeline.process_omr_image(empty_image)

        assert isinstance(result, OMRProcessingResult)
        assert result.confidence_score == 0.0

        # Test dengan very small image
        tiny_image = np.ones((10, 10), dtype=np.uint8) * 255
        result = self.pipeline.process_omr_image(tiny_image)

        assert isinstance(result, OMRProcessingResult)

        self.logger.info("Error handling test passed")

    def test_visualization_generation(self):
        """Test visualization generation"""
        test_image = self.test_images[0]

        # Process dengan visualization enabled
        result = self.pipeline.process_omr_image(test_image, visualize=True)

        assert isinstance(result, OMRProcessingResult)

        # Check if visualization files were created (in real implementation)
        self.logger.info("Visualization generation test passed")

def run_comprehensive_tests():
    """
    Run comprehensive test suite untuk Week 6 implementation
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(__name__)
    logger.info("Starting comprehensive Week 6 testing")

    # Create test instance
    test_framework = TestPipelineFramework()
    test_framework.setup_class()

    # Run all tests
    test_methods = [
        'test_pipeline_initialization',
        'test_pipeline_processing_perfect_image',
        'test_pipeline_processing_rotated_image',
        'test_pipeline_processing_noisy_image',
        'test_pipeline_processing_low_contrast',
        'test_individual_detectors',
        'test_grid_normalization',
        'test_cell_extraction',
        'test_bubble_detection',
        'test_batch_processing',
        'test_performance_benchmarks',
        'test_error_handling',
        'test_visualization_generation'
    ]

    results = {}
    total_tests = len(test_methods)
    passed_tests = 0

    for test_method in test_methods:
        try:
            logger.info(f"Running {test_method}...")
            getattr(test_framework, test_method)()
            results[test_method] = 'PASSED'
            passed_tests += 1
            logger.info(f"✅ {test_method} PASSED")
        except Exception as e:
            results[test_method] = f'FAILED: {str(e)}'
            logger.error(f"❌ {test_method} FAILED: {str(e)}")

    # Test summary
    success_rate = (passed_tests / total_tests) * 100
    logger.info(f"\n{'='*50}")
    logger.info(f"WEEK 6 TESTING SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    logger.info(f"{'='*50}")

    return results, success_rate

if __name__ == "__main__":
    results, success_rate = run_comprehensive_tests()
    print(f"\nTesting completed with {success_rate:.1f}% success rate")