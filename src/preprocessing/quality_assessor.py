"""
Quality Assessment Module untuk Preprocessed OMR Images
Menganalisis quality preprocessed images dan assess readiness untuk template detection

Author: OMR Grading System Team
Date: 28 September 2025
Academic Milestone: Week 5 - Preprocessing Analysis
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Union, Tuple
import json
from dataclasses import dataclass


@dataclass
class QualityMetrics:
    """Data class untuk quality assessment metrics"""
    laplacian_variance: float
    edge_density: float
    rms_contrast: float
    dynamic_range: float
    local_variance: float
    high_freq_ratio: float
    blur_intensity: float
    smoothness_score: float
    contrast_score: float


@dataclass
class ReadinessAssessment:
    """Data class untuk template detection readiness assessment"""
    overall_readiness: float
    quality_score: float
    recommendation: str
    quality_flags: Dict[str, bool]
    readiness_components: Dict[str, float]


class PreprocessingArtifactDetector:
    """
    Detector untuk preprocessing artifacts dalam OMR images
    Mengidentifikasi Gaussian blur, noise reduction, dan contrast enhancement
    """

    def __init__(self):
        self.blur_threshold = 100
        self.noise_threshold = 50
        self.contrast_threshold = 40

    def detect_gaussian_blur_artifacts(self, image: np.ndarray) -> Dict[str, float]:
        """
        Deteksi artifacts dari Gaussian blur processing

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            Dictionary containing blur analysis metrics
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Calculate edge sharpness menggunakan Laplacian
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Calculate edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Detect blur artifacts
        blur_evidence = {
            'laplacian_variance': float(laplacian_var),
            'edge_density': float(edge_density),
            'blur_detected': laplacian_var < self.blur_threshold,
            'blur_intensity': max(0, 1 - (laplacian_var / 200))
        }

        return blur_evidence

    def detect_noise_reduction_artifacts(self, image: np.ndarray) -> Dict[str, float]:
        """
        Deteksi artifacts dari noise reduction processing

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            Dictionary containing noise reduction analysis metrics
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Calculate local variance (texture analysis)
        kernel = np.ones((5,5), np.float32) / 25
        smoothed = cv2.filter2D(gray, -1, kernel)
        variance_map = (gray.astype(np.float32) - smoothed.astype(np.float32)) ** 2
        local_variance = np.mean(variance_map)

        # FFT analysis untuk detect frequency reduction
        fft = np.fft.fft2(gray)
        fft_magnitude = np.abs(fft)
        h, w = gray.shape
        high_freq_energy = np.sum(fft_magnitude[h//4:3*h//4, w//4:3*w//4])
        total_energy = np.sum(fft_magnitude)
        high_freq_ratio = high_freq_energy / total_energy if total_energy > 0 else 0

        noise_evidence = {
            'local_variance': float(local_variance),
            'high_freq_ratio': float(high_freq_ratio),
            'noise_reduction_detected': local_variance < self.noise_threshold,
            'smoothness_score': 1 - min(1, local_variance / 100)
        }

        return noise_evidence

    def detect_contrast_enhancement_artifacts(self, image: np.ndarray) -> Dict[str, float]:
        """
        Deteksi artifacts dari contrast enhancement

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            Dictionary containing contrast enhancement analysis metrics
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Calculate contrast metrics
        rms_contrast = np.sqrt(np.mean((gray - gray.mean()) ** 2))
        dynamic_range = float(gray.max() - gray.min())

        # Histogram analysis untuk detect enhancement
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist.flatten() / hist.sum()

        # Detect bimodal distribution (typical of enhanced OMR images)
        hist_peaks = np.where(hist_normalized > 0.01)[0]
        bimodal_score = 1 if len(hist_peaks) > 0 and (hist_peaks[-1] - hist_peaks[0]) > 200 else 0

        contrast_evidence = {
            'rms_contrast': float(rms_contrast),
            'dynamic_range': dynamic_range,
            'bimodal_score': float(bimodal_score),
            'enhancement_detected': rms_contrast > self.contrast_threshold and dynamic_range > 200,
            'contrast_score': min(1, rms_contrast / 80)
        }

        return contrast_evidence


class PreprocessedQualityAssessor:
    """
    Quality assessment framework untuk preprocessed OMR images
    Focus pada readiness untuk template detection (Week 6)
    """

    def __init__(self):
        self.artifact_detector = PreprocessingArtifactDetector()

        # Quality thresholds untuk template detection readiness
        self.thresholds = {
            'min_contrast': 30,        # Minimum RMS contrast
            'max_blur_intensity': 0.8,  # Maximum acceptable blur
            'min_edge_density': 0.01,   # Minimum edge content
            'min_dynamic_range': 150    # Minimum pixel value range
        }

        # Readiness scoring weights
        self.readiness_weights = {
            'contrast': 0.4,
            'sharpness': 0.35,
            'edges': 0.25
        }

    def extract_quality_metrics(self, image: np.ndarray) -> QualityMetrics:
        """
        Extract comprehensive quality metrics dari image

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            QualityMetrics object containing all metrics
        """
        blur_analysis = self.artifact_detector.detect_gaussian_blur_artifacts(image)
        noise_analysis = self.artifact_detector.detect_noise_reduction_artifacts(image)
        contrast_analysis = self.artifact_detector.detect_contrast_enhancement_artifacts(image)

        return QualityMetrics(
            laplacian_variance=blur_analysis['laplacian_variance'],
            edge_density=blur_analysis['edge_density'],
            rms_contrast=contrast_analysis['rms_contrast'],
            dynamic_range=contrast_analysis['dynamic_range'],
            local_variance=noise_analysis['local_variance'],
            high_freq_ratio=noise_analysis['high_freq_ratio'],
            blur_intensity=blur_analysis['blur_intensity'],
            smoothness_score=noise_analysis['smoothness_score'],
            contrast_score=contrast_analysis['contrast_score']
        )

    def assess_template_readiness(self, image_path: Union[str, Path]) -> ReadinessAssessment:
        """
        Comprehensive assessment untuk template detection readiness

        Args:
            image_path: Path ke image file

        Returns:
            ReadinessAssessment object
        """
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

        # Get preprocessing analysis
        blur_analysis = self.artifact_detector.detect_gaussian_blur_artifacts(image)
        noise_analysis = self.artifact_detector.detect_noise_reduction_artifacts(image)
        contrast_analysis = self.artifact_detector.detect_contrast_enhancement_artifacts(image)

        # Calculate readiness component scores
        contrast_readiness = min(1.0, contrast_analysis['rms_contrast'] / 60)
        sharpness_readiness = min(1.0, blur_analysis['laplacian_variance'] / 150)
        edge_readiness = min(1.0, blur_analysis['edge_density'] / 0.05)

        # Overall readiness score
        overall_readiness = (
            contrast_readiness * self.readiness_weights['contrast'] +
            sharpness_readiness * self.readiness_weights['sharpness'] +
            edge_readiness * self.readiness_weights['edges']
        )

        # Quality flags
        quality_flags = {
            'sufficient_contrast': contrast_analysis['rms_contrast'] >= self.thresholds['min_contrast'],
            'acceptable_blur': blur_analysis['blur_intensity'] <= self.thresholds['max_blur_intensity'],
            'sufficient_edges': blur_analysis['edge_density'] >= self.thresholds['min_edge_density'],
            'good_dynamic_range': contrast_analysis['dynamic_range'] >= self.thresholds['min_dynamic_range']
        }

        # Calculate overall quality score
        quality_score = sum(quality_flags.values()) / len(quality_flags)

        # Generate recommendation
        if overall_readiness >= 0.8 and quality_score >= 0.75:
            recommendation = "EXCELLENT - Ready for template detection"
        elif overall_readiness >= 0.6 and quality_score >= 0.5:
            recommendation = "GOOD - Suitable for template detection"
        elif overall_readiness >= 0.4:
            recommendation = "FAIR - May require additional preprocessing"
        else:
            recommendation = "POOR - Not suitable for template detection"

        return ReadinessAssessment(
            overall_readiness=overall_readiness,
            quality_score=quality_score,
            recommendation=recommendation,
            quality_flags=quality_flags,
            readiness_components={
                'contrast_readiness': contrast_readiness,
                'sharpness_readiness': sharpness_readiness,
                'edge_readiness': edge_readiness
            }
        )

    def batch_assessment(self, image_paths: List[Union[str, Path]]) -> List[Dict]:
        """
        Batch assessment multiple images

        Args:
            image_paths: List of paths ke image files

        Returns:
            List of assessment results
        """
        results = []
        for path in image_paths:
            try:
                assessment = self.assess_template_readiness(path)
                result = {
                    'filename': Path(path).name,
                    'file_path': str(path),
                    'overall_readiness': assessment.overall_readiness,
                    'quality_score': assessment.quality_score,
                    'recommendation': assessment.recommendation,
                    'quality_flags': assessment.quality_flags,
                    'readiness_components': assessment.readiness_components
                }
                results.append(result)
            except Exception as e:
                results.append({
                    'filename': Path(path).name,
                    'file_path': str(path),
                    'error': str(e)
                })

        return results

    def generate_assessment_report(self, assessment_results: List[Dict]) -> Dict:
        """
        Generate comprehensive assessment report

        Args:
            assessment_results: Results dari batch_assessment

        Returns:
            Comprehensive assessment report
        """
        valid_results = [r for r in assessment_results if 'error' not in r]

        if not valid_results:
            return {'error': 'No valid assessment results'}

        # Calculate summary statistics
        overall_readiness_scores = [r['overall_readiness'] for r in valid_results]
        quality_scores = [r['quality_score'] for r in valid_results]

        # Count recommendations
        recommendations = [r['recommendation'] for r in valid_results]
        recommendation_counts = {}
        for rec in recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1

        # Quality flags summary
        flag_names = ['sufficient_contrast', 'acceptable_blur', 'sufficient_edges', 'good_dynamic_range']
        flag_summary = {}
        for flag in flag_names:
            flag_summary[flag] = sum(1 for r in valid_results if r['quality_flags'].get(flag, False))

        return {
            'total_images': len(assessment_results),
            'valid_assessments': len(valid_results),
            'failed_assessments': len(assessment_results) - len(valid_results),
            'overall_readiness': {
                'mean': np.mean(overall_readiness_scores),
                'std': np.std(overall_readiness_scores),
                'min': np.min(overall_readiness_scores),
                'max': np.max(overall_readiness_scores)
            },
            'quality_scores': {
                'mean': np.mean(quality_scores),
                'std': np.std(quality_scores),
                'min': np.min(quality_scores),
                'max': np.max(quality_scores)
            },
            'recommendations': recommendation_counts,
            'quality_flags': flag_summary,
            'readiness_percentage': len([r for r in valid_results
                                       if 'EXCELLENT' in r['recommendation'] or 'GOOD' in r['recommendation']]) / len(valid_results) * 100
        }


def main():
    """
    Example usage and testing
    """
    assessor = PreprocessedQualityAssessor()

    # Test dengan sample images
    sample_path = Path('../datasets/samples/development')
    if sample_path.exists():
        sample_files = list(sample_path.glob('*.jpg'))[:5]
        if sample_files:
            print(f"Testing quality assessment pada {len(sample_files)} sample images...")

            results = assessor.batch_assessment(sample_files)
            report = assessor.generate_assessment_report(results)

            print("Assessment Report:")
            print(json.dumps(report, indent=2))
        else:
            print("No sample images found untuk testing")
    else:
        print(f"Sample path tidak ditemukan: {sample_path}")


if __name__ == "__main__":
    main()