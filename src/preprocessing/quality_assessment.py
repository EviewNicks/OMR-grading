"""Quality Assessment Module

Provides image quality metrics dan readiness scoring untuk preprocessing pipeline.

Module ini mengukur kualitas gambar berdasarkan:
- Laplacian variance (ketajaman)
- Edge density (kepadatan tepi)
- RMS contrast (kontras gambar)
- Dynamic range (rentang intensitas)

Functions:
    assess_image_quality: Calculate comprehensive quality metrics
    calculate_readiness_score: Generate weighted readiness score
    generate_quality_flags: Binary quality indicators

Example:
    >>> from src.preprocessing.quality_assessment import assess_image_quality, calculate_readiness_score
    >>> import cv2
    >>> image = cv2.imread("image.jpg")
    >>> metrics = assess_image_quality(image)
    >>> print(f"RMS Contrast: {metrics.rms_contrast:.2f}")
    >>> print(f"Readiness: {metrics.readiness_score:.2f}")
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path


@dataclass
class QualityMetrics:
    """Container untuk image quality metrics

    Attributes:
        laplacian_variance: Measure of image sharpness (higher = sharper)
        edge_density: Ratio of edge pixels to total pixels
        rms_contrast: Root Mean Square contrast value
        dynamic_range: Difference between max and min pixel intensity
        readiness_score: Overall readiness score (0-1)
        quality_flags: Binary indicators untuk quality thresholds
    """
    laplacian_variance: float
    edge_density: float
    rms_contrast: float
    dynamic_range: int
    readiness_score: float
    quality_flags: Dict[str, bool]


def calculate_laplacian_variance(image: np.ndarray) -> float:
    """Calculate Laplacian variance (sharpness measure)

    Laplacian variance mengukur ketajaman gambar dengan mendeteksi
    perubahan intensitas yang cepat (edges). Nilai tinggi = gambar tajam.

    Args:
        image: Input image (BGR format)

    Returns:
        Laplacian variance value (typically 100-10000)

    Raises:
        ValueError: If image is empty or invalid format
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return float(laplacian.var())


def calculate_edge_density(image: np.ndarray) -> float:
    """Calculate edge density using Canny edge detection

    Edge density mengukur proporsi pixel yang merupakan edge.
    Nilai tinggi = banyak detail/struktur dalam gambar.

    Args:
        image: Input image (BGR format)

    Returns:
        Edge density ratio (0-1)

    Raises:
        ValueError: If image is empty or invalid format
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return float(np.sum(edges > 0) / edges.size)


def calculate_rms_contrast(image: np.ndarray) -> float:
    """Calculate RMS (Root Mean Square) contrast

    RMS contrast mengukur variasi intensitas pixel dari mean.
    Nilai tinggi = kontras tinggi, nilai rendah = kontras rendah.

    Args:
        image: Input image (BGR format)

    Returns:
        RMS contrast value (typically 20-80)

    Raises:
        ValueError: If image is empty or invalid format
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(np.sqrt(np.mean((gray - gray.mean()) ** 2)))


def calculate_dynamic_range(image: np.ndarray) -> int:
    """Calculate dynamic range (max - min pixel intensity)

    Dynamic range mengukur rentang intensitas pixel.
    Nilai 255 = full range (0-255), nilai rendah = limited range.

    Args:
        image: Input image (BGR format)

    Returns:
        Dynamic range value (0-255)

    Raises:
        ValueError: If image is empty or invalid format
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return int(gray.max() - gray.min())


def calculate_readiness_score(metrics: QualityMetrics) -> float:
    """Calculate overall readiness score with weighted components

    Readiness score menggabungkan multiple metrics dengan bobot:
    - Contrast readiness: 40% (paling penting untuk OMR)
    - Sharpness readiness: 35% (ketajaman bubble detection)
    - Edge readiness: 25% (structure detection)

    Args:
        metrics: QualityMetrics object dengan calculated metrics

    Returns:
        Overall readiness score (0-1)

    Note:
        Target readiness: >= 0.8 untuk template detection
    """
    # Component readiness (normalized to 0-1)
    contrast_readiness = min(1.0, metrics.rms_contrast / 60)
    sharpness_readiness = min(1.0, metrics.laplacian_variance / 150)
    edge_readiness = min(1.0, metrics.edge_density / 0.05)

    # Weighted overall readiness
    overall_readiness = (
        contrast_readiness * 0.4 +
        sharpness_readiness * 0.35 +
        edge_readiness * 0.25
    )

    return float(overall_readiness)


def generate_quality_flags(metrics: QualityMetrics) -> Dict[str, bool]:
    """Generate quality flags based on thresholds

    Quality flags memberikan binary indicators untuk quick assessment:
    - sufficient_contrast: RMS contrast > 40 (minimum untuk OMR)
    - acceptable_blur: Laplacian variance > 100 (cukup tajam)
    - sufficient_edges: Edge density > 0.03 (cukup struktur)

    Args:
        metrics: QualityMetrics object dengan calculated metrics

    Returns:
        Dictionary of quality flags
    """
    return {
        'sufficient_contrast': metrics.rms_contrast > 40,
        'acceptable_blur': metrics.laplacian_variance > 100,
        'sufficient_edges': metrics.edge_density > 0.03
    }


def assess_image_quality(
    image: np.ndarray,
    image_path: Optional[Path] = None
) -> QualityMetrics:
    """Assess overall image quality with multiple metrics

    Main function untuk quality assessment. Menghitung semua metrics
    dan menghasilkan readiness score.

    Args:
        image: Input image (BGR format from cv2.imread)
        image_path: Optional path untuk logging/debugging

    Returns:
        QualityMetrics object dengan all metrics dan readiness score

    Raises:
        ValueError: If image is empty or invalid format

    Example:
        >>> image = cv2.imread("test.jpg")
        >>> metrics = assess_image_quality(image)
        >>> print(f"Readiness: {metrics.readiness_score:.2f}")
        >>> if metrics.quality_flags['sufficient_contrast']:
        ...     print("Image has sufficient contrast")
    """
    if image is None or image.size == 0:
        raise ValueError(f"Invalid image{f' at {image_path}' if image_path else ''}")

    # Calculate individual metrics
    laplacian_var = calculate_laplacian_variance(image)
    edge_dens = calculate_edge_density(image)
    rms_cont = calculate_rms_contrast(image)
    dyn_range = calculate_dynamic_range(image)

    # Create preliminary metrics object (without readiness score)
    preliminary_metrics = QualityMetrics(
        laplacian_variance=laplacian_var,
        edge_density=edge_dens,
        rms_contrast=rms_cont,
        dynamic_range=dyn_range,
        readiness_score=0.0,  # Will be calculated
        quality_flags={}  # Will be generated
    )

    # Calculate readiness score
    readiness = calculate_readiness_score(preliminary_metrics)

    # Generate quality flags
    preliminary_metrics.readiness_score = readiness
    flags = generate_quality_flags(preliminary_metrics)

    # Create final metrics object
    final_metrics = QualityMetrics(
        laplacian_variance=laplacian_var,
        edge_density=edge_dens,
        rms_contrast=rms_cont,
        dynamic_range=dyn_range,
        readiness_score=readiness,
        quality_flags=flags
    )

    return final_metrics


# Threshold constants untuk reference
THRESHOLDS = {
    'MIN_CONTRAST': 40.0,
    'MIN_SHARPNESS': 100.0,
    'MIN_EDGE_DENSITY': 0.03,
    'TARGET_READINESS': 0.8,
    'OPTIMAL_CONTRAST': 60.0,
    'OPTIMAL_SHARPNESS': 150.0,
    'OPTIMAL_EDGE_DENSITY': 0.05
}
