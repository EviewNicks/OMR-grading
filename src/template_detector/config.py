"""
Configuration module untuk Template Detection system
Centralized parameter management dengan type hints dan validation
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Union
import numpy as np
import json
from pathlib import Path


@dataclass
class ContourDetectionConfig:
    """Configuration untuk Contour-based grid detection"""
    min_area: int = 5000
    max_area: int = 200000
    aspect_ratio_min: float = 0.3
    aspect_ratio_max: float = 3.0
    rectangularity_threshold: float = 0.7
    approximation_epsilon: float = 0.02
    hierarchy_level: int = 2


@dataclass
class HoughTransformConfig:
    """Configuration untuk Hough Transform line detection"""
    rho_resolution: float = 1.0
    theta_resolution: float = np.pi/180
    threshold: int = 100
    min_line_length: int = 50
    max_line_gap: int = 10
    canny_low_threshold: int = 50
    canny_high_threshold: int = 150
    parallel_tolerance_angle: float = 5.0  # degrees


@dataclass
class TemplateMatchingConfig:
    """Configuration untuk Template matching multi-scale"""
    scale_range: Tuple[float, float] = (0.7, 1.3)
    scale_step: float = 0.1
    rotation_range: Tuple[int, int] = (-20, 20)
    rotation_step: int = 5
    match_threshold: float = 0.7
    correlation_method: str = 'TM_CCOEFF_NORMED'
    template_types: Tuple[str, ...] = ('3x20', '4x15', '5x12')


@dataclass
class DetectionFusionConfig:
    """Configuration untuk Detection fusion algorithm"""
    confidence_threshold: float = 0.6
    geometric_tolerance: float = 0.1
    consensus_weights: Dict[str, float] = field(default_factory=lambda: {
        'contour': 0.4,
        'hough': 0.3,
        'template': 0.3
    })
    outlier_rejection_method: str = 'RANSAC'
    min_consensus_count: int = 2


@dataclass
class SegmentationConfig:
    """Configuration untuk Grid segmentation pipeline"""
    perspective_correction_enabled: bool = True
    cell_padding: int = 2
    min_cell_area: int = 100
    max_cell_area: int = 5000
    grid_regularity_threshold: float = 0.8
    interpolation_method: str = 'INTER_LINEAR'


@dataclass
class QualityAssessmentConfig:
    """Configuration untuk Quality assessment system"""
    min_quality_threshold: float = 0.5
    confidence_interval: float = 0.95
    outlier_threshold: float = 2.0
    processing_timeout: int = 30
    max_detection_attempts: int = 3


@dataclass
class ProcessingConfig:
    """Configuration untuk bubble detection dan processing parameters"""
    detection: Dict[str, Union[int, float]] = field(default_factory=lambda: {
        'min_bubble_radius': 8,
        'max_bubble_radius': 25,
        'filled_threshold': 0.3,
        'confidence_threshold': 0.6
    })

    # Quality assessment parameters
    quality_threshold: float = 0.7
    processing_timeout: int = 30

    # Visualization settings
    debug_visualization: bool = False
    save_debug_images: bool = False


@dataclass
class TemplateDetectionConfig:
    """Main configuration class yang menggabungkan semua sub-configurations"""

    contour: ContourDetectionConfig = field(default_factory=ContourDetectionConfig)
    hough: HoughTransformConfig = field(default_factory=HoughTransformConfig)
    template: TemplateMatchingConfig = field(default_factory=TemplateMatchingConfig)
    fusion: DetectionFusionConfig = field(default_factory=DetectionFusionConfig)
    segmentation: SegmentationConfig = field(default_factory=SegmentationConfig)
    quality: QualityAssessmentConfig = field(default_factory=QualityAssessmentConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)

    # Global settings
    debug_mode: bool = False
    save_intermediate_results: bool = True
    log_level: str = 'INFO'

    def save_to_file(self, filepath: Union[str, Path]) -> None:
        """Save configuration ke JSON file"""
        config_dict = {
            'contour': {
                'min_area': self.contour.min_area,
                'max_area': self.contour.max_area,
                'aspect_ratio_min': self.contour.aspect_ratio_min,
                'aspect_ratio_max': self.contour.aspect_ratio_max,
                'rectangularity_threshold': self.contour.rectangularity_threshold,
                'approximation_epsilon': self.contour.approximation_epsilon,
                'hierarchy_level': self.contour.hierarchy_level
            },
            'hough': {
                'rho_resolution': self.hough.rho_resolution,
                'theta_resolution': float(self.hough.theta_resolution),
                'threshold': self.hough.threshold,
                'min_line_length': self.hough.min_line_length,
                'max_line_gap': self.hough.max_line_gap,
                'canny_low_threshold': self.hough.canny_low_threshold,
                'canny_high_threshold': self.hough.canny_high_threshold,
                'parallel_tolerance_angle': self.hough.parallel_tolerance_angle
            },
            'template': {
                'scale_range': self.template.scale_range,
                'scale_step': self.template.scale_step,
                'rotation_range': self.template.rotation_range,
                'rotation_step': self.template.rotation_step,
                'match_threshold': self.template.match_threshold,
                'correlation_method': self.template.correlation_method,
                'template_types': self.template.template_types
            },
            'fusion': {
                'confidence_threshold': self.fusion.confidence_threshold,
                'geometric_tolerance': self.fusion.geometric_tolerance,
                'consensus_weights': self.fusion.consensus_weights,
                'outlier_rejection_method': self.fusion.outlier_rejection_method,
                'min_consensus_count': self.fusion.min_consensus_count
            },
            'segmentation': {
                'perspective_correction_enabled': self.segmentation.perspective_correction_enabled,
                'cell_padding': self.segmentation.cell_padding,
                'min_cell_area': self.segmentation.min_cell_area,
                'max_cell_area': self.segmentation.max_cell_area,
                'grid_regularity_threshold': self.segmentation.grid_regularity_threshold,
                'interpolation_method': self.segmentation.interpolation_method
            },
            'quality': {
                'min_quality_threshold': self.quality.min_quality_threshold,
                'confidence_interval': self.quality.confidence_interval,
                'outlier_threshold': self.quality.outlier_threshold,
                'processing_timeout': self.quality.processing_timeout,
                'max_detection_attempts': self.quality.max_detection_attempts
            },
            'global': {
                'debug_mode': self.debug_mode,
                'save_intermediate_results': self.save_intermediate_results,
                'log_level': self.log_level
            }
        }

        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: Union[str, Path]) -> 'TemplateDetectionConfig':
        """Load configuration dari JSON file"""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)

        # Create config dengan loaded parameters
        config = cls()

        # Update contour config
        if 'contour' in config_dict:
            c_cfg = config_dict['contour']
            config.contour = ContourDetectionConfig(
                min_area=c_cfg.get('min_area', 5000),
                max_area=c_cfg.get('max_area', 200000),
                aspect_ratio_min=c_cfg.get('aspect_ratio_min', 0.3),
                aspect_ratio_max=c_cfg.get('aspect_ratio_max', 3.0),
                rectangularity_threshold=c_cfg.get('rectangularity_threshold', 0.7),
                approximation_epsilon=c_cfg.get('approximation_epsilon', 0.02),
                hierarchy_level=c_cfg.get('hierarchy_level', 2)
            )

        # Update hough config
        if 'hough' in config_dict:
            h_cfg = config_dict['hough']
            config.hough = HoughTransformConfig(
                rho_resolution=h_cfg.get('rho_resolution', 1.0),
                theta_resolution=h_cfg.get('theta_resolution', np.pi/180),
                threshold=h_cfg.get('threshold', 100),
                min_line_length=h_cfg.get('min_line_length', 50),
                max_line_gap=h_cfg.get('max_line_gap', 10),
                canny_low_threshold=h_cfg.get('canny_low_threshold', 50),
                canny_high_threshold=h_cfg.get('canny_high_threshold', 150),
                parallel_tolerance_angle=h_cfg.get('parallel_tolerance_angle', 5.0)
            )

        # Update template config
        if 'template' in config_dict:
            t_cfg = config_dict['template']
            config.template = TemplateMatchingConfig(
                scale_range=tuple(t_cfg.get('scale_range', (0.7, 1.3))),
                scale_step=t_cfg.get('scale_step', 0.1),
                rotation_range=tuple(t_cfg.get('rotation_range', (-20, 20))),
                rotation_step=t_cfg.get('rotation_step', 5),
                match_threshold=t_cfg.get('match_threshold', 0.7),
                correlation_method=t_cfg.get('correlation_method', 'TM_CCOEFF_NORMED'),
                template_types=tuple(t_cfg.get('template_types', ('3x20', '4x15', '5x12')))
            )

        # Update fusion config
        if 'fusion' in config_dict:
            f_cfg = config_dict['fusion']
            config.fusion = DetectionFusionConfig(
                confidence_threshold=f_cfg.get('confidence_threshold', 0.6),
                geometric_tolerance=f_cfg.get('geometric_tolerance', 0.1),
                consensus_weights=f_cfg.get('consensus_weights', {
                    'contour': 0.4, 'hough': 0.3, 'template': 0.3
                }),
                outlier_rejection_method=f_cfg.get('outlier_rejection_method', 'RANSAC'),
                min_consensus_count=f_cfg.get('min_consensus_count', 2)
            )

        # Update segmentation config
        if 'segmentation' in config_dict:
            s_cfg = config_dict['segmentation']
            config.segmentation = SegmentationConfig(
                perspective_correction_enabled=s_cfg.get('perspective_correction_enabled', True),
                cell_padding=s_cfg.get('cell_padding', 2),
                min_cell_area=s_cfg.get('min_cell_area', 100),
                max_cell_area=s_cfg.get('max_cell_area', 5000),
                grid_regularity_threshold=s_cfg.get('grid_regularity_threshold', 0.8),
                interpolation_method=s_cfg.get('interpolation_method', 'INTER_LINEAR')
            )

        # Update quality config
        if 'quality' in config_dict:
            q_cfg = config_dict['quality']
            config.quality = QualityAssessmentConfig(
                min_quality_threshold=q_cfg.get('min_quality_threshold', 0.5),
                confidence_interval=q_cfg.get('confidence_interval', 0.95),
                outlier_threshold=q_cfg.get('outlier_threshold', 2.0),
                processing_timeout=q_cfg.get('processing_timeout', 30),
                max_detection_attempts=q_cfg.get('max_detection_attempts', 3)
            )

        # Update global settings
        if 'global' in config_dict:
            g_cfg = config_dict['global']
            config.debug_mode = g_cfg.get('debug_mode', False)
            config.save_intermediate_results = g_cfg.get('save_intermediate_results', True)
            config.log_level = g_cfg.get('log_level', 'INFO')

        return config

    def validate(self) -> bool:
        """Validate configuration parameters"""
        try:
            # Validate contour parameters
            assert 0 < self.contour.min_area < self.contour.max_area
            assert 0 < self.contour.aspect_ratio_min < self.contour.aspect_ratio_max
            assert 0 < self.contour.rectangularity_threshold <= 1.0

            # Validate hough parameters
            assert self.hough.rho_resolution > 0
            assert 0 < self.hough.theta_resolution < np.pi
            assert self.hough.threshold > 0

            # Validate template parameters
            assert 0 < self.template.scale_range[0] < self.template.scale_range[1]
            assert 0 < self.template.scale_step < 1.0
            assert 0 <= self.template.match_threshold <= 1.0

            # Validate fusion parameters
            assert 0 <= self.fusion.confidence_threshold <= 1.0
            assert sum(self.fusion.consensus_weights.values()) == 1.0

            return True
        except AssertionError:
            return False


# Default configuration instance
default_config = TemplateDetectionConfig()