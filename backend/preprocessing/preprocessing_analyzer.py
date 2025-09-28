"""
Preprocessing Analysis Module untuk OMR Dataset
Menganalisis preprocessing techniques yang sudah diterapkan pada dataset

Author: OMR Grading System Team
Date: 28 September 2025
Academic Milestone: Week 5 - Preprocessing Analysis
"""

import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Union, Tuple, Optional
import json
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass, asdict


@dataclass
class PreprocessingSignature:
    """Data class untuk preprocessing signature analysis"""
    filename: str
    gaussian_blur_detected: bool
    noise_reduction_detected: bool
    contrast_enhancement_detected: bool
    morphological_processing_detected: bool
    preprocessing_confidence: float
    processing_pipeline_estimate: List[str]


@dataclass
class ImageCharacteristics:
    """Data class untuk image characteristics analysis"""
    filename: str
    image_shape: Tuple[int, int, int]
    file_size_kb: float
    mean_intensity: float
    std_intensity: float
    entropy: float
    edge_intensity: float


class PreprocessingSignatureAnalyzer:
    """
    Analyzer untuk detect preprocessing signatures dalam OMR images
    Mengidentifikasi specific preprocessing techniques yang sudah diterapkan
    """

    def __init__(self):
        self.detection_thresholds = {
            'gaussian_blur': {
                'laplacian_var_threshold': 100,
                'edge_softness_threshold': 0.3
            },
            'noise_reduction': {
                'local_variance_threshold': 50,
                'frequency_reduction_threshold': 0.4
            },
            'contrast_enhancement': {
                'rms_contrast_threshold': 40,
                'histogram_separation_threshold': 200
            },
            'morphological': {
                'contour_regularity_threshold': 0.7,
                'boundary_smoothness_threshold': 0.6
            }
        }

    def analyze_gaussian_blur_signature(self, image: np.ndarray) -> Dict[str, Union[bool, float]]:
        """
        Analyze Gaussian blur preprocessing signature

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            Dictionary containing Gaussian blur analysis
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Laplacian variance analysis
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()

        # Edge softness analysis
        edges_50_150 = cv2.Canny(gray, 50, 150)
        edges_100_200 = cv2.Canny(gray, 100, 200)
        edge_softness = 1 - (np.sum(edges_100_200) / max(np.sum(edges_50_150), 1))

        # Frequency domain analysis
        fft = np.fft.fft2(gray)
        fft_magnitude = np.abs(fft)
        h, w = gray.shape

        # High frequency component analysis
        center_h, center_w = h // 2, w // 2
        high_freq_mask = np.zeros_like(fft_magnitude)
        high_freq_mask[center_h - h//4:center_h + h//4, center_w - w//4:center_w + w//4] = 1
        high_freq_energy = np.sum(fft_magnitude * high_freq_mask)
        total_energy = np.sum(fft_magnitude)
        high_freq_ratio = high_freq_energy / total_energy

        # Gaussian blur detection
        gaussian_detected = (
            laplacian_var < self.detection_thresholds['gaussian_blur']['laplacian_var_threshold'] and
            edge_softness > self.detection_thresholds['gaussian_blur']['edge_softness_threshold']
        )

        return {
            'gaussian_blur_detected': gaussian_detected,
            'laplacian_variance': float(laplacian_var),
            'edge_softness': float(edge_softness),
            'high_freq_ratio': float(high_freq_ratio),
            'gaussian_confidence': min(1.0, edge_softness + (1 - min(1, laplacian_var / 200)))
        }

    def analyze_noise_reduction_signature(self, image: np.ndarray) -> Dict[str, Union[bool, float]]:
        """
        Analyze noise reduction preprocessing signature

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            Dictionary containing noise reduction analysis
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Local variance analysis (texture smoothness)
        kernel = cv2.getGaussianKernel(5, 1)
        kernel = kernel @ kernel.T
        smoothed = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        local_variance = np.var(gray.astype(np.float32) - smoothed)

        # Noise estimation using wavelet analysis
        try:
            import pywt
            coeffs = pywt.dwt2(gray, 'db1')
            _, (LH, HL, HH) = coeffs
            noise_estimate = np.median(np.abs(HH)) / 0.6745
        except ImportError:
            # Fallback noise estimation
            kernel_noise = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            noise_response = cv2.filter2D(gray.astype(np.float32), -1, kernel_noise)
            noise_estimate = np.std(noise_response)

        # Frequency domain smoothness
        fft = np.fft.fft2(gray)
        fft_magnitude = np.abs(fft)
        h, w = gray.shape

        # Calculate frequency spectrum smoothness
        freq_profile = np.mean(fft_magnitude, axis=0)
        freq_smoothness = 1 - (np.std(freq_profile) / np.mean(freq_profile))

        # Noise reduction detection
        noise_reduction_detected = (
            local_variance < self.detection_thresholds['noise_reduction']['local_variance_threshold'] and
            freq_smoothness > self.detection_thresholds['noise_reduction']['frequency_reduction_threshold']
        )

        return {
            'noise_reduction_detected': noise_reduction_detected,
            'local_variance': float(local_variance),
            'noise_estimate': float(noise_estimate),
            'frequency_smoothness': float(freq_smoothness),
            'noise_reduction_confidence': min(1.0, freq_smoothness + (1 - min(1, local_variance / 100)))
        }

    def analyze_contrast_enhancement_signature(self, image: np.ndarray) -> Dict[str, Union[bool, float]]:
        """
        Analyze contrast enhancement preprocessing signature

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            Dictionary containing contrast enhancement analysis
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Contrast metrics
        rms_contrast = np.sqrt(np.mean((gray - gray.mean()) ** 2))
        michelson_contrast = (gray.max() - gray.min()) / (gray.max() + gray.min()) if (gray.max() + gray.min()) > 0 else 0

        # Histogram analysis
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist.flatten() / hist.sum()

        # Detect histogram stretching/equalization artifacts
        cumulative_hist = np.cumsum(hist_normalized)
        histogram_uniformity = 1 - np.std(cumulative_hist)

        # Detect bimodal distribution typical of enhanced OMR
        hist_smoothed = cv2.GaussianBlur(hist_normalized.reshape(-1, 1), (5, 1), 0).flatten()
        peaks = []
        for i in range(1, len(hist_smoothed) - 1):
            if hist_smoothed[i] > hist_smoothed[i-1] and hist_smoothed[i] > hist_smoothed[i+1] and hist_smoothed[i] > 0.005:
                peaks.append(i)

        bimodal_score = 1 if len(peaks) >= 2 and (max(peaks) - min(peaks)) > self.detection_thresholds['contrast_enhancement']['histogram_separation_threshold'] else 0

        # Enhancement detection
        enhancement_detected = (
            rms_contrast > self.detection_thresholds['contrast_enhancement']['rms_contrast_threshold'] and
            (bimodal_score > 0 or histogram_uniformity < 0.3)
        )

        return {
            'contrast_enhancement_detected': enhancement_detected,
            'rms_contrast': float(rms_contrast),
            'michelson_contrast': float(michelson_contrast),
            'histogram_uniformity': float(histogram_uniformity),
            'bimodal_score': float(bimodal_score),
            'enhancement_confidence': min(1.0, (rms_contrast / 80) + bimodal_score)
        }

    def analyze_morphological_signature(self, image: np.ndarray) -> Dict[str, Union[bool, float]]:
        """
        Analyze morphological processing signature

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            Dictionary containing morphological processing analysis
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Binary threshold untuk contour analysis
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return {
                'morphological_processing_detected': False,
                'contour_regularity': 0.0,
                'boundary_smoothness': 0.0,
                'morphological_confidence': 0.0
            }

        # Analyze contour regularity (typical of morphological closing/opening)
        regularities = []
        smoothness_scores = []

        for contour in contours[:10]:  # Analyze top 10 largest contours
            if len(contour) < 10:
                continue

            # Contour regularity analysis
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                regularities.append(min(1.0, circularity))

            # Boundary smoothness analysis
            if len(contour) > 5:
                # Calculate contour curvature smoothness
                points = contour.reshape(-1, 2)
                if len(points) > 3:
                    # Calculate local curvature variation
                    curvature_variation = 0
                    for i in range(2, len(points) - 2):
                        p1, p2, p3 = points[i-1], points[i], points[i+1]
                        v1 = p2 - p1
                        v2 = p3 - p2
                        angle_change = np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))
                        curvature_variation += abs(angle_change)

                    smoothness = 1 - min(1, curvature_variation / len(points))
                    smoothness_scores.append(smoothness)

        # Average metrics
        contour_regularity = np.mean(regularities) if regularities else 0
        boundary_smoothness = np.mean(smoothness_scores) if smoothness_scores else 0

        # Morphological processing detection
        morphological_detected = (
            contour_regularity > self.detection_thresholds['morphological']['contour_regularity_threshold'] and
            boundary_smoothness > self.detection_thresholds['morphological']['boundary_smoothness_threshold']
        )

        return {
            'morphological_processing_detected': morphological_detected,
            'contour_regularity': float(contour_regularity),
            'boundary_smoothness': float(boundary_smoothness),
            'morphological_confidence': (contour_regularity + boundary_smoothness) / 2
        }

    def analyze_preprocessing_pipeline(self, image: np.ndarray) -> PreprocessingSignature:
        """
        Comprehensive preprocessing pipeline analysis

        Args:
            image: Input image (BGR atau grayscale)

        Returns:
            PreprocessingSignature object
        """
        # Analyze each preprocessing component
        gaussian_analysis = self.analyze_gaussian_blur_signature(image)
        noise_analysis = self.analyze_noise_reduction_signature(image)
        contrast_analysis = self.analyze_contrast_enhancement_signature(image)
        morphological_analysis = self.analyze_morphological_signature(image)

        # Estimate processing pipeline order
        pipeline_estimate = []
        confidences = {}

        if noise_analysis['noise_reduction_detected']:
            pipeline_estimate.append('noise_reduction')
            confidences['noise_reduction'] = noise_analysis['noise_reduction_confidence']

        if gaussian_analysis['gaussian_blur_detected']:
            pipeline_estimate.append('gaussian_blur')
            confidences['gaussian_blur'] = gaussian_analysis['gaussian_confidence']

        if contrast_analysis['contrast_enhancement_detected']:
            pipeline_estimate.append('contrast_enhancement')
            confidences['contrast_enhancement'] = contrast_analysis['enhancement_confidence']

        if morphological_analysis['morphological_processing_detected']:
            pipeline_estimate.append('morphological_operations')
            confidences['morphological'] = morphological_analysis['morphological_confidence']

        # Calculate overall preprocessing confidence
        if confidences:
            preprocessing_confidence = np.mean(list(confidences.values()))
        else:
            preprocessing_confidence = 0.0

        return PreprocessingSignature(
            filename="",  # Will be set by caller
            gaussian_blur_detected=gaussian_analysis['gaussian_blur_detected'],
            noise_reduction_detected=noise_analysis['noise_reduction_detected'],
            contrast_enhancement_detected=contrast_analysis['contrast_enhancement_detected'],
            morphological_processing_detected=morphological_analysis['morphological_processing_detected'],
            preprocessing_confidence=preprocessing_confidence,
            processing_pipeline_estimate=pipeline_estimate
        )


class DatasetPreprocessingAnalyzer:
    """
    Comprehensive analyzer untuk dataset preprocessing analysis
    Menganalisis preprocessing patterns across dataset
    """

    def __init__(self):
        self.signature_analyzer = PreprocessingSignatureAnalyzer()

    def analyze_image_characteristics(self, image_path: Union[str, Path]) -> ImageCharacteristics:
        """
        Analyze basic image characteristics

        Args:
            image_path: Path ke image file

        Returns:
            ImageCharacteristics object
        """
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Basic characteristics
        file_size_kb = Path(image_path).stat().st_size / 1024
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)

        # Calculate entropy
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist.flatten() / hist.sum()
        entropy = -np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))

        # Edge intensity
        edges = cv2.Canny(gray, 50, 150)
        edge_intensity = np.sum(edges > 0) / edges.size

        return ImageCharacteristics(
            filename=Path(image_path).name,
            image_shape=image.shape,
            file_size_kb=file_size_kb,
            mean_intensity=mean_intensity,
            std_intensity=std_intensity,
            entropy=entropy,
            edge_intensity=edge_intensity
        )

    def batch_analyze_dataset(self, image_paths: List[Union[str, Path]]) -> Tuple[List[PreprocessingSignature], List[ImageCharacteristics]]:
        """
        Batch analysis dataset preprocessing

        Args:
            image_paths: List of paths ke image files

        Returns:
            Tuple of (preprocessing signatures, image characteristics)
        """
        preprocessing_signatures = []
        image_characteristics = []

        for image_path in image_paths:
            try:
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    continue

                # Analyze preprocessing signature
                signature = self.signature_analyzer.analyze_preprocessing_pipeline(image)
                signature.filename = Path(image_path).name
                preprocessing_signatures.append(signature)

                # Analyze image characteristics
                characteristics = self.analyze_image_characteristics(image_path)
                image_characteristics.append(characteristics)

            except Exception as e:
                print(f"Error analyzing {image_path}: {e}")
                continue

        return preprocessing_signatures, image_characteristics

    def generate_dataset_report(self, preprocessing_signatures: List[PreprocessingSignature],
                              image_characteristics: List[ImageCharacteristics]) -> Dict:
        """
        Generate comprehensive dataset preprocessing report

        Args:
            preprocessing_signatures: List of preprocessing signatures
            image_characteristics: List of image characteristics

        Returns:
            Comprehensive dataset report
        """
        if not preprocessing_signatures:
            return {'error': 'No valid preprocessing signatures'}

        # Convert ke DataFrames untuk analysis
        df_signatures = pd.DataFrame([asdict(sig) for sig in preprocessing_signatures])
        df_characteristics = pd.DataFrame([asdict(char) for char in image_characteristics])

        # Preprocessing detection statistics
        preprocessing_stats = {
            'total_images': len(preprocessing_signatures),
            'gaussian_blur_detection_rate': df_signatures['gaussian_blur_detected'].mean(),
            'noise_reduction_detection_rate': df_signatures['noise_reduction_detected'].mean(),
            'contrast_enhancement_detection_rate': df_signatures['contrast_enhancement_detected'].mean(),
            'morphological_processing_detection_rate': df_signatures['morphological_processing_detected'].mean(),
            'average_preprocessing_confidence': df_signatures['preprocessing_confidence'].mean(),
            'preprocessing_confidence_std': df_signatures['preprocessing_confidence'].std()
        }

        # Pipeline analysis
        all_pipelines = df_signatures['processing_pipeline_estimate'].tolist()
        pipeline_patterns = {}
        for pipeline in all_pipelines:
            pipeline_str = ' -> '.join(pipeline) if pipeline else 'no_preprocessing'
            pipeline_patterns[pipeline_str] = pipeline_patterns.get(pipeline_str, 0) + 1

        # Image characteristics summary
        characteristics_summary = {
            'average_file_size_kb': df_characteristics['file_size_kb'].mean(),
            'average_mean_intensity': df_characteristics['mean_intensity'].mean(),
            'average_std_intensity': df_characteristics['std_intensity'].mean(),
            'average_entropy': df_characteristics['entropy'].mean(),
            'average_edge_intensity': df_characteristics['edge_intensity'].mean()
        }

        return {
            'analysis_summary': preprocessing_stats,
            'pipeline_patterns': pipeline_patterns,
            'image_characteristics': characteristics_summary,
            'dataset_metadata': {
                'total_images_analyzed': len(preprocessing_signatures),
                'analysis_date': pd.Timestamp.now().isoformat(),
                'most_common_pipeline': max(pipeline_patterns.items(), key=lambda x: x[1])[0] if pipeline_patterns else 'unknown'
            }
        }


def main():
    """
    Example usage and testing
    """
    analyzer = DatasetPreprocessingAnalyzer()

    # Test dengan sample images
    sample_path = Path('../datasets/samples/development')
    if sample_path.exists():
        sample_files = list(sample_path.glob('*.jpg'))[:10]
        if sample_files:
            print(f"Analyzing preprocessing signatures untuk {len(sample_files)} sample images...")

            signatures, characteristics = analyzer.batch_analyze_dataset(sample_files)
            report = analyzer.generate_dataset_report(signatures, characteristics)

            print("Dataset Preprocessing Analysis Report:")
            print(json.dumps(report, indent=2))
        else:
            print("No sample images found untuk testing")
    else:
        print(f"Sample path tidak ditemukan: {sample_path}")


if __name__ == "__main__":
    main()