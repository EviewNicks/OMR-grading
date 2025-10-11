"""Morphological Operations Module

Noise removal dan shape enhancement untuk preprocessing pipeline.

Module ini menyediakan morphological operations untuk:
- Noise removal (opening operation)
- Hole filling (closing operation)
- Combined operations untuk comprehensive cleaning

Operations:
    - Opening: Erosion → Dilation (remove small artifacts, preserve edges)
    - Closing: Dilation → Erosion (fill holes, connect lines)
    - Combined: Opening → Closing (comprehensive noise handling)

Example:
    >>> from src.preprocessing.morphological_ops import apply_morphology, MorphologyConfig
    >>> import cv2
    >>> image = cv2.imread("image.jpg")
    >>> config = MorphologyConfig(operations=["opening"], kernel_size=3)
    >>> cleaned = apply_morphology(image, config)
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Literal, Optional


@dataclass
class MorphologyConfig:
    """Configuration untuk morphological operations

    Attributes:
        operations: List of operations to apply in sequence
        kernel_size: Size of morphological kernel (odd numbers recommended)
        kernel_shape: Shape of structuring element
        opening_kernel: Specific kernel size untuk opening (overrides kernel_size)
        closing_kernel: Specific kernel size untuk closing (overrides kernel_size)
    """
    operations: List[Literal["opening", "closing"]] = None
    kernel_size: int = 3
    kernel_shape: Literal["rect", "ellipse", "cross"] = "rect"
    opening_kernel: Optional[int] = None
    closing_kernel: Optional[int] = None

    def __post_init__(self):
        """Validate configuration and set defaults"""
        if self.operations is None:
            self.operations = ["opening"]

        # Validate operations
        valid_ops = {"opening", "closing"}
        for op in self.operations:
            if op not in valid_ops:
                raise ValueError(f"Invalid operation: {op}. Must be 'opening' or 'closing'")

        # Validate kernel sizes
        if self.kernel_size < 1 or self.kernel_size > 15:
            raise ValueError(f"kernel_size must be between 1 and 15, got {self.kernel_size}")

        if self.kernel_size % 2 == 0:
            raise ValueError(f"kernel_size should be odd, got {self.kernel_size}")

        # Validate kernel shape
        if self.kernel_shape not in ["rect", "ellipse", "cross"]:
            raise ValueError(f"Invalid kernel_shape: {self.kernel_shape}")

        # Validate specific kernel sizes
        if self.opening_kernel is not None:
            if self.opening_kernel < 1 or self.opening_kernel > 15 or self.opening_kernel % 2 == 0:
                raise ValueError(f"opening_kernel must be odd and between 1-15, got {self.opening_kernel}")

        if self.closing_kernel is not None:
            if self.closing_kernel < 1 or self.closing_kernel > 15 or self.closing_kernel % 2 == 0:
                raise ValueError(f"closing_kernel must be odd and between 1-15, got {self.closing_kernel}")


def create_kernel(size: int, shape: str = "rect") -> np.ndarray:
    """Create structuring element for morphological operations

    Args:
        size: Kernel size (must be odd)
        shape: Kernel shape ("rect", "ellipse", or "cross")

    Returns:
        Structuring element as numpy array

    Example:
        >>> kernel = create_kernel(5, "ellipse")
    """
    if shape == "rect":
        return np.ones((size, size), np.uint8)
    elif shape == "ellipse":
        return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    elif shape == "cross":
        return cv2.getStructuringElement(cv2.MORPH_CROSS, (size, size))
    else:
        raise ValueError(f"Unknown kernel shape: {shape}")


def apply_opening(
    image: np.ndarray,
    kernel_size: int = 3,
    kernel_shape: str = "rect"
) -> np.ndarray:
    """Apply opening operation (erosion → dilation)

    Opening removes small artifacts and noise while preserving
    larger structures. Best for removing isolated white pixels.

    Args:
        image: Input image (BGR or grayscale)
        kernel_size: Size of structuring element (must be odd)
        kernel_shape: Shape of structuring element

    Returns:
        Processed grayscale image (8-bit)

    Raises:
        ValueError: If image is empty or kernel_size is invalid

    Example:
        >>> cleaned = apply_opening(image, kernel_size=3)

    Note:
        Notebook results untuk kernel_size:
        - kernel=3: Edge preservation 1.005 (best), noise -46%
        - kernel=5: Edge preservation 0.844, noise -60%
        - kernel=7: Edge preservation 0.775, noise -65%

        Recommendation: kernel=3 untuk OMR (preserves bubble edges)
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Create kernel
    kernel = create_kernel(kernel_size, kernel_shape)

    # Apply opening
    opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

    return opened


def apply_closing(
    image: np.ndarray,
    kernel_size: int = 3,
    kernel_shape: str = "rect"
) -> np.ndarray:
    """Apply closing operation (dilation → erosion)

    Closing fills small holes and connects nearby structures.
    Best for filling gaps in bubble markings.

    Args:
        image: Input image (BGR or grayscale)
        kernel_size: Size of structuring element (must be odd)
        kernel_shape: Shape of structuring element

    Returns:
        Processed grayscale image (8-bit)

    Raises:
        ValueError: If image is empty or kernel_size is invalid

    Example:
        >>> filled = apply_closing(image, kernel_size=3)

    Note:
        Notebook results:
        - kernel=3: Noise reduction 87%, edge preservation 0.277
        - kernel=5: Noise reduction 93%, edge preservation 0.104
        - kernel=7: Noise reduction 94%, edge preservation 0.074

        WARNING: Closing aggressively reduces edges. Use sparingly.
        Better untuk combined operations (opening → closing).
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Create kernel
    kernel = create_kernel(kernel_size, kernel_shape)

    # Apply closing
    closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    return closed


def apply_combined_morphology(
    image: np.ndarray,
    opening_kernel: int = 3,
    closing_kernel: int = 3,
    kernel_shape: str = "rect"
) -> np.ndarray:
    """Apply opening then closing for comprehensive cleaning

    Combined operations balance noise removal and hole filling.
    Opening first removes noise, then closing fills remaining holes.

    Args:
        image: Input image (BGR or grayscale)
        opening_kernel: Kernel size untuk opening operation
        closing_kernel: Kernel size untuk closing operation
        kernel_shape: Shape of structuring element

    Returns:
        Processed grayscale image (8-bit)

    Example:
        >>> cleaned = apply_combined_morphology(image, opening_kernel=3, closing_kernel=3)

    Note:
        Notebook results untuk combined operations:
        - open=3, close=3: Edge 0.616, noise -81%, quality 0.693
        - open=5, close=5: Edge 0.576, noise -81%, quality 0.668
        - open=3, close=5: Edge 0.440, noise -87%, quality 0.612

        Trade-off: More noise removal = less edge preservation
        Recommendation: Use opening only untuk OMR (best edge preservation)
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Apply opening first
    opened = apply_opening(gray, opening_kernel, kernel_shape)

    # Then apply closing
    closed = apply_closing(opened, closing_kernel, kernel_shape)

    return closed


def apply_morphology(
    image: np.ndarray,
    config: Optional[MorphologyConfig] = None,
    **kwargs
) -> np.ndarray:
    """Main morphological operations function dengan flexible configuration

    Unified interface untuk all morphological operations.
    Automatically applies operations in sequence based on config.

    Args:
        image: Input image (BGR or grayscale)
        config: MorphologyConfig object (if None, uses default opening)
        **kwargs: Override config parameters

    Returns:
        Processed grayscale image (8-bit)

    Raises:
        ValueError: If image is empty or operation is invalid

    Example:
        >>> # Using config object
        >>> config = MorphologyConfig(operations=["opening"], kernel_size=3)
        >>> cleaned = apply_morphology(image, config)
        >>>
        >>> # Using kwargs
        >>> cleaned = apply_morphology(image, operations=["opening", "closing"], kernel_size=5)
        >>>
        >>> # Default (opening with kernel=3)
        >>> cleaned = apply_morphology(image)

    Recommended Usage:
        For OMR preprocessing:
        - Opening only (kernel=3): Best edge preservation (visual quality 0.789)
        - Combined (open=3, close=3): More aggressive cleaning (quality 0.693)
        - Avoid closing only: Destroys too many edges
    """
    if image is None or image.size == 0:
        raise ValueError("Image is empty or invalid")

    # Use default config if not provided
    if config is None:
        config = MorphologyConfig()

    # Override config with kwargs
    if kwargs:
        operations = kwargs.get('operations', config.operations)
        kernel_size = kwargs.get('kernel_size', config.kernel_size)
        kernel_shape = kwargs.get('kernel_shape', config.kernel_shape)
        opening_kernel = kwargs.get('opening_kernel', config.opening_kernel)
        closing_kernel = kwargs.get('closing_kernel', config.closing_kernel)

        config = MorphologyConfig(
            operations=operations,
            kernel_size=kernel_size,
            kernel_shape=kernel_shape,
            opening_kernel=opening_kernel,
            closing_kernel=closing_kernel
        )

    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Apply operations in sequence
    result = gray.copy()

    for operation in config.operations:
        if operation == "opening":
            kernel_size = config.opening_kernel if config.opening_kernel is not None else config.kernel_size
            result = apply_opening(result, kernel_size, config.kernel_shape)
        elif operation == "closing":
            kernel_size = config.closing_kernel if config.closing_kernel is not None else config.kernel_size
            result = apply_closing(result, kernel_size, config.kernel_shape)

    return result


# Performance benchmarks dari notebook experiments
OPERATION_BENCHMARKS = {
    'opening': {
        'kernel_3': {'edge_preservation': 1.005, 'noise_reduction': 46.4, 'visual_quality': 0.789},
        'kernel_5': {'edge_preservation': 0.844, 'noise_reduction': 60.4, 'visual_quality': 0.748},
        'kernel_7': {'edge_preservation': 0.775, 'noise_reduction': 64.8, 'visual_quality': 0.724},
    },
    'closing': {
        'kernel_3': {'edge_preservation': 0.277, 'noise_reduction': 87.0, 'visual_quality': 0.514},
        'kernel_5': {'edge_preservation': 0.104, 'noise_reduction': 93.2, 'visual_quality': 0.435},
        'kernel_7': {'edge_preservation': 0.074, 'noise_reduction': 93.8, 'visual_quality': 0.419},
    },
    'combined': {
        'open_3_close_3': {'edge_preservation': 0.616, 'noise_reduction': 80.9, 'visual_quality': 0.693},
        'open_5_close_5': {'edge_preservation': 0.576, 'noise_reduction': 80.7, 'visual_quality': 0.668},
        'open_3_close_5': {'edge_preservation': 0.440, 'noise_reduction': 87.0, 'visual_quality': 0.612},
    }
}

# Recommended configurations untuk different scenarios
RECOMMENDED_CONFIGS = {
    'conservative': MorphologyConfig(operations=["opening"], kernel_size=3),
    'balanced': MorphologyConfig(operations=["opening"], kernel_size=5),
    'aggressive': MorphologyConfig(operations=["opening", "closing"], opening_kernel=3, closing_kernel=3),
    'very_aggressive': MorphologyConfig(operations=["opening", "closing"], opening_kernel=5, closing_kernel=5),
}
