"""Pytest fixtures untuk preprocessing tests"""

import pytest
import cv2
import numpy as np
from pathlib import Path


@pytest.fixture
def sample_image_path():
    """Path ke sample image dari datasets/test/"""
    dataset_path = Path(__file__).parent.parent.parent / "datasets" / "test"
    image_files = list(dataset_path.glob("*.jpg"))

    if not image_files:
        pytest.skip("No sample images found in datasets/test/")

    return image_files[0]


@pytest.fixture
def sample_image(sample_image_path):
    """Load sample image dari datasets/test/"""
    image = cv2.imread(str(sample_image_path))

    if image is None:
        pytest.skip(f"Could not load image: {sample_image_path}")

    return image


@pytest.fixture
def low_contrast_image():
    """Generate synthetic low contrast image untuk testing"""
    # Create 100x100 image dengan low contrast (pixel values 100-120)
    image = np.random.randint(100, 120, (100, 100), dtype=np.uint8)
    # Convert to BGR (cv2 format)
    return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)


@pytest.fixture
def high_contrast_image():
    """Generate synthetic high contrast image untuk testing"""
    # Create 100x100 image dengan high contrast (pixel values 0-255)
    image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    # Convert to BGR (cv2 format)
    return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)


@pytest.fixture
def blurry_image(sample_image):
    """Create blurred version of sample image"""
    return cv2.GaussianBlur(sample_image, (15, 15), 5)


@pytest.fixture
def sharp_image():
    """Generate synthetic sharp image dengan clear edges"""
    # Create checkerboard pattern (very sharp edges)
    image = np.zeros((100, 100), dtype=np.uint8)
    image[::20, :] = 255  # Horizontal lines
    image[:, ::20] = 255  # Vertical lines
    return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
