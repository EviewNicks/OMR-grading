"""Preprocessing Module - OMR Grading System

Production-ready preprocessing pipeline untuk optical mark recognition.

Modules:
    quality_assessment: Image quality metrics dan readiness scoring
    contrast_enhancement: CLAHE dan histogram equalization
    morphological_ops: Noise removal dengan edge preservation
    pipeline: Complete end-to-end preprocessing pipeline

Quick Start:
    >>> from src.preprocessing import preprocess_image
    >>> result = preprocess_image("answer_sheet.jpg")
    >>> if result.success:
    ...     cv2.imwrite("processed.jpg", result.processed_image)

Performance (based on 20 image experiment):
    - Success rate: 100%
    - Processing time: 0.104s per image
    - Quality improvement: +21.3% RMS contrast
"""

# Main pipeline functions
from .pipeline import (
    preprocess_image,
    batch_preprocess,
    validate_preprocessing,
    PreprocessConfig,
    PreprocessResult,
    OPTIMAL_CONFIG,
    PERFORMANCE_BENCHMARKS
)

# Module-specific exports
from .quality_assessment import (
    assess_image_quality,
    QualityMetrics,
    THRESHOLDS as QUALITY_THRESHOLDS
)

from .contrast_enhancement import (
    enhance_contrast,
    ContrastConfig,
    RECOMMENDED_CONFIGS as CONTRAST_CONFIGS
)

from .morphological_ops import (
    apply_morphology,
    MorphologyConfig,
    RECOMMENDED_CONFIGS as MORPHOLOGY_CONFIGS
)

__all__ = [
    # Pipeline (main interface)
    'preprocess_image',
    'batch_preprocess',
    'validate_preprocessing',
    'PreprocessConfig',
    'PreprocessResult',
    'OPTIMAL_CONFIG',
    'PERFORMANCE_BENCHMARKS',

    # Quality Assessment
    'assess_image_quality',
    'QualityMetrics',
    'QUALITY_THRESHOLDS',

    # Contrast Enhancement
    'enhance_contrast',
    'ContrastConfig',
    'CONTRAST_CONFIGS',

    # Morphological Operations
    'apply_morphology',
    'MorphologyConfig',
    'MORPHOLOGY_CONFIGS',
]

__version__ = "1.0.0"
