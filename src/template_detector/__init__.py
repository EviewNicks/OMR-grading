"""
Template Detector Package untuk OMR Grading System
Week 6: Template Detection & Segmentasi Implementation

Modular package structure untuk robust template detection dengan:
- Contour-based grid detection
- Hough Transform line detection
- Template matching multi-scale
- Detection fusion algorithms
- Grid segmentation pipeline
"""

__version__ = "1.0.0"
__author__ = "OMR Project Team"
__description__ = "Template Detection & Segmentation untuk OMR Grading System"

# Core detection modules
from .core import (
    ContourGridDetector,
    HoughLineDetector,
    TemplateMatchingDetector,
    DetectionFusion
)

# Segmentation modules
from .segmentation import (
    GridNormalizer,
    CellExtractor,
    BubbleDetector
)

# Utility modules
from .utils import (
    VisualizationUtils,
    QualityAssessment,
    PerformanceMonitor
)

# Configuration
from .config import TemplateDetectionConfig

# Main Pipeline
from .pipeline import OMRPipeline, OMRProcessingResult

__all__ = [
    # Main Pipeline
    'OMRPipeline',
    'OMRProcessingResult',

    # Core detection
    'ContourGridDetector',
    'HoughLineDetector',
    'TemplateMatchingDetector',
    'DetectionFusion',

    # Segmentation
    'GridNormalizer',
    'CellExtractor',
    'BubbleDetector',

    # Utils
    'VisualizationUtils',
    'QualityAssessment',
    'PerformanceMonitor',

    # Configuration
    'TemplateDetectionConfig'
]