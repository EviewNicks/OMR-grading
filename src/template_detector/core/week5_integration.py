"""
Week 5 Preprocessing Pipeline Integration
Seamless integration dengan Week 5 preprocessing results untuk Template Detection
"""

import numpy as np
import pandas as pd
import json
import cv2
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Week5PreprocessingResult:
    """Data structure untuk Week 5 preprocessing results"""
    filename: str
    file_size_kb: float
    image_shape: Tuple[int, int, int]
    laplacian_variance: float
    edge_density: float
    blur_detected: bool
    blur_intensity: float
    local_variance: float
    high_freq_ratio: float
    noise_reduction_detected: bool
    smoothness_score: float
    rms_contrast: float
    dynamic_range: int
    low_light_detected: bool
    histogram_uniformity: float
    contrast_enhanced: bool
    contrast_enhancement_intensity: float

    # Quality metrics
    overall_readiness: float
    quality_score: float
    recommendation: str
    contrast_readiness: float
    sharpness_readiness: float
    edge_readiness: float

    # Quality flags
    sufficient_contrast: bool
    acceptable_blur: bool
    sufficient_edges: bool
    good_dynamic_range: bool


class Week5IntegrationManager:
    """Manager untuk integrating Week 5 preprocessing results dengan Week 6 template detection"""

    def __init__(self, week5_results_path: Union[str, Path], week5_readiness_path: Union[str, Path]):
        """
        Initialize integration manager dengan Week 5 results

        Args:
            week5_results_path: Path ke Week 5 preprocessing analysis results JSON
            week5_readiness_path: Path ke Week 5 readiness assessment CSV
        """
        self.week5_results_path = Path(week5_results_path)
        self.week5_readiness_path = Path(week5_readiness_path)

        self.preprocessing_results = {}
        self.readiness_assessment = None

        self._load_week5_data()

    def _load_week5_data(self) -> None:
        """Load Week 5 preprocessing data"""
        try:
            # Load preprocessing analysis results
            if self.week5_results_path.exists():
                with open(self.week5_results_path, 'r') as f:
                    week5_data = json.load(f)

                for result in week5_data.get('preprocessing_analysis', []):
                    filename = result['filename']
                    self.preprocessing_results[filename] = result

                logger.info(f"Loaded {len(self.preprocessing_results)} preprocessing results")
            else:
                logger.warning(f"Week 5 results file not found: {self.week5_results_path}")

            # Load readiness assessment
            if self.week5_readiness_path.exists():
                self.readiness_assessment = pd.read_csv(self.week5_readiness_path)
                logger.info(f"Loaded readiness assessment for {len(self.readiness_assessment)} images")
            else:
                logger.warning(f"Week 5 readiness file not found: {self.week5_readiness_path}")

        except Exception as e:
            logger.error(f"Error loading Week 5 data: {str(e)}")

    def get_preprocessing_result(self, filename: str) -> Optional[Week5PreprocessingResult]:
        """
        Get preprocessing result untuk specific image

        Args:
            filename: Image filename

        Returns:
            Week5PreprocessingResult or None if not found
        """
        if filename not in self.preprocessing_results:
            logger.warning(f"Preprocessing result not found untuk {filename}")
            return None

        result_data = self.preprocessing_results[filename]

        # Get readiness data
        readiness_data = None
        if self.readiness_assessment is not None:
            readiness_row = self.readiness_assessment[
                self.readiness_assessment['filename'] == filename
            ]
            if not readiness_row.empty:
                readiness_data = readiness_row.iloc[0].to_dict()

        # Combine preprocessing dan readiness data
        try:
            return Week5PreprocessingResult(
                filename=result_data['filename'],
                file_size_kb=result_data['file_size_kb'],
                image_shape=tuple(result_data['image_shape']),
                laplacian_variance=result_data['laplacian_variance'],
                edge_density=result_data['edge_density'],
                blur_detected=result_data['blur_detected'],
                blur_intensity=result_data['blur_intensity'],
                local_variance=result_data['local_variance'],
                high_freq_ratio=result_data['high_freq_ratio'],
                noise_reduction_detected=result_data['noise_reduction_detected'],
                smoothness_score=result_data['smoothness_score'],
                rms_contrast=result_data['rms_contrast'],
                dynamic_range=result_data['dynamic_range'],
                low_light_detected=result_data['low_light_detected'],
                histogram_uniformity=result_data['histogram_uniformity'],
                contrast_enhanced=result_data['contrast_enhanced'],
                contrast_enhancement_intensity=result_data['contrast_enhancement_intensity'],

                # Readiness data (with defaults if not available)
                overall_readiness=readiness_data.get('overall_readiness', 0.5) if readiness_data else 0.5,
                quality_score=readiness_data.get('quality_score', 0.5) if readiness_data else 0.5,
                recommendation=readiness_data.get('recommendation', 'Unknown') if readiness_data else 'Unknown',
                contrast_readiness=readiness_data.get('contrast_readiness', 0.5) if readiness_data else 0.5,
                sharpness_readiness=readiness_data.get('sharpness_readiness', 0.5) if readiness_data else 0.5,
                edge_readiness=readiness_data.get('edge_readiness', 0.5) if readiness_data else 0.5,
                sufficient_contrast=readiness_data.get('sufficient_contrast', False) if readiness_data else False,
                acceptable_blur=readiness_data.get('acceptable_blur', False) if readiness_data else False,
                sufficient_edges=readiness_data.get('sufficient_edges', False) if readiness_data else False,
                good_dynamic_range=readiness_data.get('good_dynamic_range', False) if readiness_data else False
            )
        except KeyError as e:
            logger.error(f"Missing key in preprocessing data untuk {filename}: {str(e)}")
            return None

    def get_adaptive_detection_parameters(self, preprocessing_result: Week5PreprocessingResult) -> Dict:
        """
        Generate adaptive detection parameters berdasarkan Week 5 quality assessment

        Args:
            preprocessing_result: Week 5 preprocessing result

        Returns:
            Dictionary dengan adaptive parameters untuk template detection
        """
        params = {}

        # NEW: Rotation-robust contour parameters berdasarkan edge quality
        if preprocessing_result.edge_readiness >= 0.9:
            # High edge quality - use stricter rotation-robust parameters
            params['min_area_ratio'] = 0.08
            params['max_area_ratio'] = 0.60
            params['min_aspect_ratio'] = 0.08
            params['max_aspect_ratio'] = 0.70
            params['min_rectangularity'] = 0.70
        elif preprocessing_result.edge_readiness >= 0.7:
            # Medium edge quality - use standard rotation-robust parameters
            params['min_area_ratio'] = 0.05
            params['max_area_ratio'] = 0.70
            params['min_aspect_ratio'] = 0.05
            params['max_aspect_ratio'] = 0.80
            params['min_rectangularity'] = 0.60
        else:
            # Low edge quality - use ultra-relaxed rotation-robust parameters
            params['min_area_ratio'] = 0.03
            params['max_area_ratio'] = 0.80
            params['min_aspect_ratio'] = 0.03
            params['max_aspect_ratio'] = 0.90
            params['min_rectangularity'] = 0.50

        # Traditional contour parameters (fallback)
        if preprocessing_result.edge_readiness >= 0.9:
            # High edge quality - use stricter contour parameters
            params['contour_min_area'] = 8000
            params['contour_rectangularity_threshold'] = 0.8
        elif preprocessing_result.edge_readiness >= 0.7:
            # Medium edge quality - use standard parameters
            params['contour_min_area'] = 5000
            params['contour_rectangularity_threshold'] = 0.7
        else:
            # Low edge quality - use relaxed parameters
            params['contour_min_area'] = 3000
            params['contour_rectangularity_threshold'] = 0.6

        # NEW: Enable rotation-robust detection untuk low quality images
        params['use_rotation_robust'] = preprocessing_result.edge_readiness < 0.8
        params['use_hybrid_threshold'] = preprocessing_result.overall_readiness < 0.85

        # Adaptive Hough parameters berdasarkan edge density
        if preprocessing_result.edge_density >= 0.2:
            # High edge density - use higher threshold
            params['hough_threshold'] = 150
            params['hough_min_line_length'] = 60
        elif preprocessing_result.edge_density >= 0.1:
            # Medium edge density - use standard threshold
            params['hough_threshold'] = 100
            params['hough_min_line_length'] = 50
        else:
            # Low edge density - use lower threshold
            params['hough_threshold'] = 70
            params['hough_min_line_length'] = 40

        # Adaptive template matching berdasarkan overall quality
        if preprocessing_result.overall_readiness >= 0.9:
            # High quality - use strict matching
            params['template_match_threshold'] = 0.8
            params['template_scale_step'] = 0.05
        elif preprocessing_result.overall_readiness >= 0.7:
            # Medium quality - use standard matching
            params['template_match_threshold'] = 0.7
            params['template_scale_step'] = 0.1
        else:
            # Low quality - use relaxed matching
            params['template_match_threshold'] = 0.6
            params['template_scale_step'] = 0.15

        # Adaptive fusion weights berdasarkan readiness scores
        # Enhanced weights untuk rotation-robust detection
        contour_weight = min(0.6, preprocessing_result.edge_readiness)

        # Boost contour weight jika rotation-robust is enabled
        if params.get('use_rotation_robust', False):
            contour_weight = min(0.5, contour_weight * 1.2)  # 20% boost

        hough_weight = min(0.4, preprocessing_result.edge_readiness * 0.8)
        template_weight = min(0.4, preprocessing_result.overall_readiness * 0.6)

        # Normalize weights
        total_weight = contour_weight + hough_weight + template_weight
        if total_weight > 0:
            params['fusion_weights'] = {
                'contour': contour_weight / total_weight,
                'hough': hough_weight / total_weight,
                'template': template_weight / total_weight
            }
        else:
            params['fusion_weights'] = {'contour': 0.4, 'hough': 0.3, 'template': 0.3}

        logger.info(f"Generated adaptive parameters untuk {preprocessing_result.filename}: {params}")
        return params

    def create_rotation_robust_config(self, preprocessing_result: Week5PreprocessingResult) -> 'ContourDetectionConfig':
        """
        Create ContourDetectionConfig dengan rotation-robust parameters

        Args:
            preprocessing_result: Week 5 preprocessing result

        Returns:
            ContourDetectionConfig instance dengan rotation-robust settings
        """
        from ..config import ContourDetectionConfig

        params = self.get_adaptive_detection_parameters(preprocessing_result)

        return ContourDetectionConfig(
            # Traditional parameters
            min_area=params.get('contour_min_area', 5000),
            max_area=200000,
            aspect_ratio_min=0.3,
            aspect_ratio_max=3.0,
            rectangularity_threshold=params.get('contour_rectangularity_threshold', 0.7),
            approximation_epsilon=0.02,
            hierarchy_level=2,

            # NEW: Rotation-robust parameters
            min_area_ratio=params.get('min_area_ratio', 0.05),
            max_area_ratio=params.get('max_area_ratio', 0.70),
            min_aspect_ratio=params.get('min_aspect_ratio', 0.05),
            max_aspect_ratio=params.get('max_aspect_ratio', 0.80),
            min_rectangularity=params.get('min_rectangularity', 0.60),

            # NEW: Control flags
            use_rotation_robust=params.get('use_rotation_robust', True),
            use_hybrid_threshold=params.get('use_hybrid_threshold', True)
        )

    def get_quality_category_images(self, min_count: int = 3) -> Dict[str, List[str]]:
        """
        Get images categorized by quality untuk testing

        Args:
            min_count: Minimum number of images per category

        Returns:
            Dictionary dengan quality categories dan corresponding filenames
        """
        categories = {
            'high_quality': [],
            'medium_quality': [],
            'low_quality': []
        }

        if self.readiness_assessment is None:
            return categories

        # Categorize berdasarkan overall readiness score
        for _, row in self.readiness_assessment.iterrows():
            filename = row['filename']
            readiness = row['overall_readiness']

            if readiness >= 0.9:
                categories['high_quality'].append(filename)
            elif readiness >= 0.7:
                categories['medium_quality'].append(filename)
            else:
                categories['low_quality'].append(filename)

        # Ensure minimum count per category
        for category, filenames in categories.items():
            if len(filenames) < min_count:
                logger.warning(f"Category {category} has only {len(filenames)} images (minimum: {min_count})")

        return categories

    def get_statistics(self) -> Dict:
        """Get statistics tentang Week 5 preprocessing results"""
        if self.readiness_assessment is None:
            return {}

        stats = {
            'total_images': len(self.readiness_assessment),
            'average_readiness': self.readiness_assessment['overall_readiness'].mean(),
            'readiness_std': self.readiness_assessment['overall_readiness'].std(),
            'high_quality_count': (self.readiness_assessment['overall_readiness'] >= 0.9).sum(),
            'medium_quality_count': (
                (self.readiness_assessment['overall_readiness'] >= 0.7) &
                (self.readiness_assessment['overall_readiness'] < 0.9)
            ).sum(),
            'low_quality_count': (self.readiness_assessment['overall_readiness'] < 0.7).sum(),
            'contrast_ready_count': self.readiness_assessment['sufficient_contrast'].sum(),
            'blur_acceptable_count': self.readiness_assessment['acceptable_blur'].sum(),
            'edges_sufficient_count': self.readiness_assessment['sufficient_edges'].sum()
        }

        return stats