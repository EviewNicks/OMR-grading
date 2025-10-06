"""
Backend Preprocessing Module untuk OMR Grading System

Module ini menyediakan tools untuk:
1. Quality assessment preprocessed OMR images
2. Preprocessing artifact detection dan analysis
3. Template detection readiness assessment
4. Academic documentation generation

Author: OMR Grading System Team
Date: 28 September 2025
Academic Milestone: Week 5 - Preprocessing Analysis
"""

from .quality_assessor import (
    PreprocessedQualityAssessor,
    PreprocessingArtifactDetector,
    QualityMetrics,
    ReadinessAssessment
)

from .preprocessing_analyzer import (
    DatasetPreprocessingAnalyzer,
    PreprocessingSignatureAnalyzer,
    PreprocessingSignature,
    ImageCharacteristics
)

__version__ = "1.0.0"
__author__ = "OMR Grading System Team"

__all__ = [
    # Quality Assessment Classes
    'PreprocessedQualityAssessor',
    'PreprocessingArtifactDetector',
    'QualityMetrics',
    'ReadinessAssessment',

    # Preprocessing Analysis Classes
    'DatasetPreprocessingAnalyzer',
    'PreprocessingSignatureAnalyzer',
    'PreprocessingSignature',
    'ImageCharacteristics'
]


def get_default_quality_assessor():
    """
    Get default configured quality assessor untuk standard OMR processing

    Returns:
        PreprocessedQualityAssessor: Configured assessor instance
    """
    return PreprocessedQualityAssessor()


def get_default_preprocessing_analyzer():
    """
    Get default configured preprocessing analyzer untuk dataset analysis

    Returns:
        DatasetPreprocessingAnalyzer: Configured analyzer instance
    """
    return DatasetPreprocessingAnalyzer()


# Quick access functions untuk common operations
def assess_image_quality(image_path):
    """
    Quick quality assessment untuk single image

    Args:
        image_path: Path ke image file

    Returns:
        ReadinessAssessment: Assessment results
    """
    assessor = get_default_quality_assessor()
    return assessor.assess_template_readiness(image_path)


def analyze_preprocessing_signature(image_path):
    """
    Quick preprocessing signature analysis untuk single image

    Args:
        image_path: Path ke image file

    Returns:
        PreprocessingSignature: Signature analysis results
    """
    import cv2
    analyzer = get_default_preprocessing_analyzer()
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    signature = analyzer.signature_analyzer.analyze_preprocessing_pipeline(image)
    signature.filename = str(image_path)
    return signature


# Module configuration
MODULE_CONFIG = {
    'version': __version__,
    'description': 'Preprocessing analysis tools untuk OMR grading system',
    'academic_milestone': 'Week 5 - Preprocessing Analysis',
    'dependencies': ['opencv-python', 'numpy', 'pandas', 'matplotlib', 'seaborn'],
    'usage': 'Backend modules untuk preprocessing analysis dan quality assessment'
}


def get_module_info():
    """
    Get module information dan configuration

    Returns:
        dict: Module configuration information
    """
    return MODULE_CONFIG.copy()