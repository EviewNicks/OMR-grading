"""Contrast Enhancement Module

Implements proven contrast enhancement techniques untuk preprocessing pipeline.

Module ini menyediakan tiga teknik enhancement:
- CLAHE (Contrast Limited Adaptive Histogram Equalization)
- Histogram Equalization (standard)
- RMS Contrast Normalization

Supported Methods:
    - CLAHE: Terbaik untuk preserving local details
    - HistEq: Highest quality score tapi dapat overenhance
    - RMS Normalization: Target specific contrast values

Example:
    >>> from src.preprocessing.contrast_enhancement import enhance_contrast, ContrastConfig
    >>> import cv2
    >>> image = cv2.imread("image.jpg")
    >>> config = ContrastConfig(method="clahe", clip_limit=2.0)
    >>> enhanced = enhance_contrast(image, config)
    >>> print(f"Enhancement complete")
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Literal, Optional


@dataclass
class ContrastConfig:
    """Configuration untuk contrast enhancement

    Attributes:
        method: Enhancement method ("clahe", "hist_eq", "rms_norm")
        clip_limit: CLAHE clip limit (default: 2.0, range: 1.0-4.0)
        tile_size: CLAHE tile grid size (default: (8, 8))
        target_contrast: RMS normalization target (default: 70.0)
    """
    method: Literal["clahe", "hist_eq", "rms_norm"] = "clahe"
    clip_limit: float = 2.0
    tile_size: Tuple[int, int] = (8, 8)
    target_contrast: float = 70.0

    def __post_init__(self):
        """Validate configuration parameters"""
        if self.method not in ["clahe", "hist_eq", "rms_norm"]:
            raise ValueError(f"Invalid method: {self.method}. Must be 'clahe', 'hist_eq', or 'rms_norm'")

        if self.clip_limit < 1.0 or self.clip_limit > 10.0:
            raise ValueError(f"clip_limit must be between 1.0 and 10.0, got {self.clip_limit}")

        if self.tile_size[0] < 1 or self.tile_size[1] < 1:
            raise ValueError(f"tile_size must be positive, got {self.tile_size}")

        if self.target_contrast < 10.0 or self.target_contrast > 100.0:
            raise ValueError(f"target_contrast must be between 10.0 and 100.0, got {self.target_contrast}")


def apply_clahe(
    image: np.ndarray,
    clip_limit: float = 2.0,
    tile_size: Tuple[int, int] = (8, 8)
) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)

    CLAHE meningkatkan kontras lokal sambil membatasi amplifikasi noise.
    Lebih baik dari histogram equalization untuk preserving details.

    Args:
        image: Input image (BGR or grayscale)
        clip_limit: Contrast limiting threshold (higher = more contrast)
        tile_size: Grid size untuk adaptive equalization

    Returns:
        Enhanced grayscale image (8-bit)

    Raises:
        ValueError: If image is empty or invalid

    Example:
        >>> enhanced = apply_clahe(image, clip_limit=2.0, tile_size=(8, 8))

    Note:
        Based on notebook experiments:
        - clip_limit=2.0: Conservative (6% improvement)
        - clip_limit=3.0-4.0: Aggressive (8-10% improvement)
        - tile_size=(8,8): Best for OMR bubble grid
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)

    # Apply CLAHE
    enhanced = clahe.apply(gray)

    return enhanced


def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """Apply standard histogram equalization

    Global histogram equalization yang mendistribusikan intensitas
    secara merata. Memberikan quality score tertinggi (1.0) tapi
    dapat overenhance di beberapa area.

    Args:
        image: Input image (BGR or grayscale)

    Returns:
        Enhanced grayscale image (8-bit)

    Raises:
        ValueError: If image is empty or invalid

    Example:
        >>> enhanced = apply_histogram_equalization(image)

    Note:
        Notebook results:
        - Average quality score: 1.0 (highest)
        - RMS improvement: +134% (very aggressive)
        - Edge density: 0.14 (may overenhance edges)
        - Best for images dengan very low contrast
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Apply histogram equalization
    enhanced = cv2.equalizeHist(gray)

    return enhanced


def normalize_rms_contrast(
    image: np.ndarray,
    target_contrast: float = 70.0
) -> np.ndarray:
    """Apply RMS contrast normalization

    Normalisasi kontras ke target RMS value tertentu.
    Lebih controlled improvement dibanding histogram equalization.

    Args:
        image: Input image (BGR or grayscale)
        target_contrast: Target RMS contrast value (recommended: 60-80)

    Returns:
        Normalized grayscale image (8-bit)

    Raises:
        ValueError: If image is empty or invalid

    Example:
        >>> enhanced = normalize_rms_contrast(image, target_contrast=70.0)

    Note:
        Notebook results untuk target_contrast:
        - 60: +18% improvement, quality 0.88
        - 70: +24% improvement, quality 0.91 (recommended)
        - 80: +29% improvement, quality 0.92
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Calculate current RMS contrast
    current_rms = float(np.sqrt(np.mean((gray - gray.mean()) ** 2)))

    if current_rms > 0:
        # Calculate scale factor
        scale_factor = target_contrast / current_rms

        # Apply normalization
        normalized = gray.astype(np.float32)
        normalized = (normalized - normalized.mean()) * scale_factor + normalized.mean()

        # Clip to valid range
        normalized = np.clip(normalized, 0, 255).astype(np.uint8)

        return normalized

    # If RMS is 0 (flat image), return original
    return gray


def enhance_contrast(
    image: np.ndarray,
    config: Optional[ContrastConfig] = None,
    **kwargs
) -> np.ndarray:
    """Main contrast enhancement function dengan method routing

    Unified interface untuk semua contrast enhancement techniques.
    Automatically routes to appropriate technique based on config.

    Args:
        image: Input image (BGR or grayscale)
        config: ContrastConfig object (if None, uses default CLAHE)
        **kwargs: Override config parameters

    Returns:
        Enhanced grayscale image (8-bit)

    Raises:
        ValueError: If image is empty or method is invalid

    Example:
        >>> # Using config object
        >>> config = ContrastConfig(method="clahe", clip_limit=2.0)
        >>> enhanced = enhance_contrast(image, config)
        >>>
        >>> # Using kwargs override
        >>> enhanced = enhance_contrast(image, method="hist_eq")
        >>>
        >>> # Default (CLAHE with conservative settings)
        >>> enhanced = enhance_contrast(image)

    Recommended Usage:
        For OMR preprocessing:
        - CLAHE (clip_limit=2.0): Conservative, preserves details
        - HistEq: For very low contrast images only
        - RMS Norm (target=70): For controlled improvement
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Use default config if not provided
    if config is None:
        config = ContrastConfig()

    # Override config with kwargs
    if kwargs:
        method = kwargs.get('method', config.method)
        clip_limit = kwargs.get('clip_limit', config.clip_limit)
        tile_size = kwargs.get('tile_size', config.tile_size)
        target_contrast = kwargs.get('target_contrast', config.target_contrast)

        config = ContrastConfig(
            method=method,
            clip_limit=clip_limit,
            tile_size=tile_size,
            target_contrast=target_contrast
        )

    # Route to appropriate method
    if config.method == "clahe":
        return apply_clahe(image, config.clip_limit, config.tile_size)
    elif config.method == "hist_eq":
        return apply_histogram_equalization(image)
    elif config.method == "rms_norm":
        return normalize_rms_contrast(image, config.target_contrast)
    else:
        raise ValueError(f"Unknown method: {config.method}")


# Performance benchmarks dari notebook experiments
TECHNIQUE_BENCHMARKS = {
    'clahe': {
        'clip_2.0_tile_8x8': {'quality': 0.84, 'rms_improvement': 6.3, 'edges': 0.09},
        'clip_3.0_tile_8x8': {'quality': 0.84, 'rms_improvement': 8.2, 'edges': 0.10},
        'clip_4.0_tile_8x8': {'quality': 0.85, 'rms_improvement': 9.7, 'edges': 0.10},
    },
    'hist_eq': {
        'default': {'quality': 1.00, 'rms_improvement': 134.2, 'edges': 0.14},
    },
    'rms_norm': {
        'target_60': {'quality': 0.88, 'rms_improvement': 17.9, 'edges': 0.09},
        'target_70': {'quality': 0.91, 'rms_improvement': 24.0, 'edges': 0.09},
        'target_80': {'quality': 0.92, 'rms_improvement': 28.6, 'edges': 0.09},
    }
}

# Recommended configurations untuk different scenarios
RECOMMENDED_CONFIGS = {
    'conservative': ContrastConfig(method="clahe", clip_limit=2.0, tile_size=(8, 8)),
    'balanced': ContrastConfig(method="clahe", clip_limit=3.0, tile_size=(8, 8)),
    'aggressive': ContrastConfig(method="hist_eq"),
    'controlled': ContrastConfig(method="rms_norm", target_contrast=70.0),
}
