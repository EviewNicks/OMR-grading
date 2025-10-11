"""Preprocessing Pipeline Module

Complete end-to-end preprocessing pipeline untuk OMR grading system.

Pipeline Steps:
    1. Quality Assessment (baseline metrics)
    2. Contrast Enhancement (CLAHE dengan optimal parameters)
    3. Morphological Operations (opening + closing)
    4. Validation (quality gates dan readiness check)

Example:
    >>> from src.preprocessing.pipeline import preprocess_image, PreprocessConfig
    >>> import cv2
    >>> config = PreprocessConfig()  # Uses optimal parameters
    >>> result = preprocess_image("image.jpg", config)
    >>> print(f"Success: {result.success}, Readiness: {result.quality_after.readiness_score:.2f}")
"""

import cv2
import numpy as np
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Union

# Import modules M1-M3
from .quality_assessment import (
    assess_image_quality,
    QualityMetrics as QA_QualityMetrics
)
from .contrast_enhancement import (
    enhance_contrast,
    ContrastConfig
)
from .morphological_ops import (
    apply_morphology,
    MorphologyConfig
)


@dataclass
class PreprocessConfig:
    """Unified configuration untuk complete preprocessing pipeline

    Attributes:
        contrast: ContrastConfig untuk contrast enhancement step
        morphology: MorphologyConfig untuk morphological operations step
        quality_threshold: Minimum readiness score untuk success (default: 0.8)
        min_rms_contrast: Minimum RMS contrast untuk quality flag (default: 30.0)
        min_edge_density: Minimum edge density untuk quality flag (default: 0.03)

    Note:
        Default configuration uses optimal parameters dari notebook experiments:
        - CLAHE dengan clip_limit=2.0 (conservative, best edge preservation)
        - Opening operation dengan kernel=3 (noise removal, preserves edges)
        - Quality threshold 0.8 (matches datasets/train readiness)
    """
    contrast: ContrastConfig = None
    morphology: MorphologyConfig = None
    quality_threshold: float = 0.8
    min_rms_contrast: float = 30.0
    min_edge_density: float = 0.03

    def __post_init__(self):
        """Initialize with optimal defaults dari notebook experiments"""
        if self.contrast is None:
            # Optimal parameters dari Notebook 2
            self.contrast = ContrastConfig(
                method="clahe",
                clip_limit=2.0,  # Conservative, best for OMR
                tile_size=(8, 8)
            )

        if self.morphology is None:
            # Optimal parameters dari Notebook 3
            self.morphology = MorphologyConfig(
                operations=["opening"],  # Best edge preservation (1.005 ratio)
                kernel_size=3
            )

        # Validate thresholds
        if self.quality_threshold < 0 or self.quality_threshold > 1:
            raise ValueError(f"quality_threshold must be 0-1, got {self.quality_threshold}")

        if self.min_rms_contrast < 0:
            raise ValueError(f"min_rms_contrast must be positive, got {self.min_rms_contrast}")

        if self.min_edge_density < 0 or self.min_edge_density > 1:
            raise ValueError(f"min_edge_density must be 0-1, got {self.min_edge_density}")


@dataclass
class PreprocessResult:
    """Result dari preprocessing pipeline

    Attributes:
        success: Pipeline execution success status
        processed_image: Final processed image (grayscale, 8-bit)
        metrics: Quality metrics after preprocessing
        processing_time: Total processing time in seconds
        quality_flags: Quality validation results
        error_message: Error description (if success=False)
        intermediate_steps: Optional dictionary dengan intermediate images

    Example:
        >>> if result.success:
        ...     print(f"Quality score: {result.metrics.readiness_score:.2f}")
        ...     cv2.imwrite("output.jpg", result.processed_image)
        ... else:
        ...     print(f"Failed: {result.error_message}")
    """
    success: bool
    processed_image: np.ndarray
    metrics: QA_QualityMetrics
    processing_time: float
    quality_flags: dict
    error_message: Optional[str] = None
    intermediate_steps: Optional[dict] = None


def preprocess_image(
    image_path: Union[str, Path],
    config: Optional[PreprocessConfig] = None,
    save_intermediate: bool = False
) -> PreprocessResult:
    """Main preprocessing pipeline function

    Complete preprocessing pipeline yang mengintegrasikan M1-M3:
    1. Load image dan validate
    2. Quality assessment (baseline)
    3. Contrast enhancement (M2)
    4. Morphological operations (M3)
    5. Final quality assessment (M1)
    6. Validation gates

    Args:
        image_path: Path ke input image
        config: PreprocessConfig object (uses optimal defaults if None)
        save_intermediate: If True, save intermediate processing steps

    Returns:
        PreprocessResult dengan complete processing information

    Raises:
        FileNotFoundError: If image file tidak exist
        ValueError: If image invalid atau config invalid

    Example:
        >>> # Using default config
        >>> result = preprocess_image("image.jpg")
        >>> print(f"Success: {result.success}")
        >>>
        >>> # Using custom config
        >>> config = PreprocessConfig(quality_threshold=0.9)
        >>> result = preprocess_image("image.jpg", config)
        >>>
        >>> # Save intermediate steps
        >>> result = preprocess_image("image.jpg", save_intermediate=True)
        >>> contrast_img = result.intermediate_steps['after_contrast']

    Performance:
        Based on notebook experiments (20 images):
        - Average processing time: 0.104 seconds/image
        - Success rate: 100% (quality >= 0.8)
        - Average quality improvement: +4.9% readiness, +21.3% RMS contrast
    """
    start_time = time.time()
    intermediate_steps = {} if save_intermediate else None

    try:
        # Use default config if not provided
        if config is None:
            config = PreprocessConfig()

        # Convert path to Path object
        image_path = Path(image_path)

        # Check file exists
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load image
        original = cv2.imread(str(image_path))
        if original is None:
            raise ValueError(f"Could not load image: {image_path}")

        if save_intermediate:
            intermediate_steps['original'] = original.copy()

        # Step 1: Baseline quality assessment
        # (Not used for processing, only for comparison)
        # quality_before = assess_image_quality(original)

        # Step 2: Contrast enhancement
        contrast_enhanced = enhance_contrast(original, config.contrast)

        if save_intermediate:
            intermediate_steps['after_contrast'] = contrast_enhanced.copy()

        # Step 3: Morphological operations
        final_processed = apply_morphology(contrast_enhanced, config.morphology)

        if save_intermediate:
            intermediate_steps['after_morphology'] = final_processed.copy()

        # Step 4: Final quality assessment
        # Convert to BGR for quality assessment (M1 expects BGR)
        final_bgr = cv2.cvtColor(final_processed, cv2.COLOR_GRAY2BGR)
        metrics = assess_image_quality(final_bgr)

        # Step 5: Validation gates
        quality_flags = {
            'sufficient_contrast': metrics.rms_contrast >= config.min_rms_contrast,
            'sufficient_edges': metrics.edge_density >= config.min_edge_density,
            'meets_readiness': metrics.readiness_score >= config.quality_threshold
        }

        # Determine success
        success = all(quality_flags.values())

        processing_time = time.time() - start_time

        return PreprocessResult(
            success=success,
            processed_image=final_processed,
            metrics=metrics,
            processing_time=processing_time,
            quality_flags=quality_flags,
            error_message=None,
            intermediate_steps=intermediate_steps
        )

    except Exception as e:
        processing_time = time.time() - start_time

        # Return failure result
        return PreprocessResult(
            success=False,
            processed_image=np.zeros((1, 1), dtype=np.uint8),  # Dummy image
            metrics=QA_QualityMetrics(
                laplacian_variance=0.0,
                edge_density=0.0,
                rms_contrast=0.0,
                dynamic_range=0,
                readiness_score=0.0,
                quality_flags={}
            ),
            processing_time=processing_time,
            quality_flags={
                'sufficient_contrast': False,
                'sufficient_edges': False,
                'meets_readiness': False
            },
            error_message=str(e),
            intermediate_steps=None
        )


def batch_preprocess(
    image_paths: List[Union[str, Path]],
    config: Optional[PreprocessConfig] = None,
    show_progress: bool = True
) -> List[PreprocessResult]:
    """Batch preprocessing untuk multiple images

    Process multiple images dengan same configuration.
    Useful untuk processing entire datasets.

    Args:
        image_paths: List of image paths
        config: PreprocessConfig object (uses optimal defaults if None)
        show_progress: If True, print progress updates

    Returns:
        List of PreprocessResult objects

    Example:
        >>> from pathlib import Path
        >>> image_paths = list(Path("datasets/test").glob("*.jpg"))
        >>> results = batch_preprocess(image_paths)
        >>> success_rate = sum(r.success for r in results) / len(results)
        >>> print(f"Success rate: {success_rate:.1%}")

    Performance:
        For 20 images (based on notebook):
        - Total time: ~2.1 seconds
        - Success rate: 100%
        - Average quality: 0.898 readiness score
    """
    if config is None:
        config = PreprocessConfig()

    results = []
    total = len(image_paths)

    for i, img_path in enumerate(image_paths, 1):
        result = preprocess_image(img_path, config, save_intermediate=False)
        results.append(result)

        if show_progress and i % 5 == 0:
            print(f"  Processed {i}/{total} images...")

    if show_progress:
        successful = sum(r.success for r in results)
        success_rate = (successful / total * 100) if total > 0 else 0
        avg_time = sum(r.processing_time for r in results) / total if total > 0 else 0

        print(f"\nBatch processing complete:")
        print(f"  Total: {total} images")
        print(f"  Success: {successful} ({success_rate:.1f}%)")
        print(f"  Avg time: {avg_time:.3f}s per image")

    return results


def validate_preprocessing(result: PreprocessResult, strict: bool = False) -> Tuple[bool, List[str]]:
    """Validate preprocessing result against quality gates

    Additional validation beyond basic success flag.
    Useful untuk quality assurance dan debugging.

    Args:
        result: PreprocessResult to validate
        strict: If True, apply stricter validation criteria

    Returns:
        Tuple of (is_valid, list_of_issues)

    Example:
        >>> result = preprocess_image("image.jpg")
        >>> is_valid, issues = validate_preprocessing(result, strict=True)
        >>> if not is_valid:
        ...     print(f"Issues found: {', '.join(issues)}")

    Validation Criteria:
        Standard:
        - Success flag must be True
        - Processing time must be < 5 seconds
        - Processed image must be valid

        Strict:
        - Processing time must be < 2 seconds
        - Readiness score must be >= 0.9
        - All quality flags must pass
    """
    issues = []

    # Basic checks
    if not result.success:
        issues.append(f"Pipeline failed: {result.error_message}")
        return False, issues

    if result.processed_image is None or result.processed_image.size == 0:
        issues.append("Processed image is invalid")

    # Performance checks
    max_time = 2.0 if strict else 5.0
    if result.processing_time > max_time:
        issues.append(f"Processing too slow: {result.processing_time:.3f}s (max: {max_time}s)")

    # Quality checks
    if strict:
        if result.metrics.readiness_score < 0.9:
            issues.append(f"Readiness below strict threshold: {result.metrics.readiness_score:.3f} < 0.9")

        # Check all quality flags
        for flag_name, flag_value in result.quality_flags.items():
            if not flag_value:
                issues.append(f"Quality flag failed: {flag_name}")

    is_valid = len(issues) == 0
    return is_valid, issues


# Performance benchmarks dari notebook experiment
PERFORMANCE_BENCHMARKS = {
    'notebook_experiment': {
        'total_images': 20,
        'success_rate': 100.0,  # %
        'avg_processing_time': 0.104,  # seconds
        'avg_readiness_before': 0.856,
        'avg_readiness_after': 0.898,
        'avg_readiness_improvement': 0.042,
        'avg_rms_improvement_pct': 21.3
    },
    'targets': {
        'min_success_rate': 90.0,  # %
        'max_processing_time': 2.0,  # seconds
        'min_quality_improvement': 20.0  # %
    }
}

# Optimal configuration dari notebook experiments
OPTIMAL_CONFIG = PreprocessConfig(
    contrast=ContrastConfig(method="clahe", clip_limit=2.0, tile_size=(8, 8)),
    morphology=MorphologyConfig(operations=["opening"], kernel_size=3),
    quality_threshold=0.8,
    min_rms_contrast=30.0,
    min_edge_density=0.03
)
