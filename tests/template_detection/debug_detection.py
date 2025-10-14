#!/usr/bin/env python3
"""
Debug script untuk rotation detection
"""

import cv2
import numpy as np
from pathlib import Path
import sys
import matplotlib.pyplot as plt

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector

def debug_single_image(image_path):
    """Debug single image detection"""
    print(f"\n{'='*60}")
    print(f"DEBUGGING: {image_path.name}")
    print(f"{'='*60}")

    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"ERROR: Cannot load image")
        return

    print(f"Image shape: {image.shape}")
    print(f"Image dtype: {image.dtype}")
    print(f"Image range: {image.min()} - {image.max()}")

    # Create config
    config = ContourDetectionConfig(
        min_area=1000,
        max_area=50000,
        aspect_ratio_min=0.1,
        aspect_ratio_max=2.0,
        rectangularity_threshold=0.6,
        approximation_epsilon=0.02,
        hierarchy_level=2,

        # Rotation-robust parameters
        min_area_ratio=0.05,
        max_area_ratio=0.70,
        min_aspect_ratio=0.05,
        max_aspect_ratio=0.80,
        min_rectangularity=0.60,

        # Control flags
        use_rotation_robust=True,
        use_hybrid_threshold=True
    )

    detector = ContourGridDetector(config)

    # Test rotation-robust detection
    print("\n--- Testing Rotation-Robust Detection ---")
    result = detector.detect_grid(image)

    print(f"Confidence: {result.confidence}")
    print(f"Grid coordinates: {result.grid_coordinates}")
    print(f"Rotation robust: {result.rotation_robust}")
    print(f"Angle: {result.angle}")
    print(f"Error: {result.error_message}")
    print(f"Processing time: {result.processing_time}")

    # Debug preprocessing
    print("\n--- Debug Preprocessing ---")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Test both threshold methods
    binary_inv = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11, C=2
    )

    binary = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=11, C=2
    )

    print(f"Grayscale range: {gray.min()} - {gray.max()}")
    print(f"Binary INV unique values: {np.unique(binary_inv)}")
    print(f"Binary unique values: {np.unique(binary)}")

    # Extract contours
    contours_inv, _ = cv2.findContours(binary_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_binary, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Contours (BINARY_INV): {len(contours_inv)}")
    print(f"Contours (BINARY): {len(contours_binary)}")

    # Test rotation-robust filtering
    if contours_inv:
        filtered_data = detector._filter_contours_rotation_robust(contours_inv, image.shape)
        print(f"Filtered contours (BINARY_INV): {len(filtered_data)}")

        if filtered_data:
            print("Top 5 filtered contours:")
            for i, data in enumerate(filtered_data[:5]):
                print(f"  {i+1}: area={data['area']:.0f}, ratio={data['aspect_ratio']:.3f}, "
                      f"rect={data['rectangularity']:.3f}, angle={data['angle']:.1f}")

    if contours_binary:
        filtered_data_binary = detector._filter_contours_rotation_robust(contours_binary, image.shape)
        print(f"Filtered contours (BINARY): {len(filtered_data_binary)}")

        if filtered_data_binary:
            print("Top 5 filtered contours (BINARY):")
            for i, data in enumerate(filtered_data_binary[:5]):
                print(f"  {i+1}: area={data['area']:.0f}, ratio={data['aspect_ratio']:.3f}, "
                      f"rect={data['rectangularity']:.3f}, angle={data['angle']:.1f}")

    # Create simple visualization
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Original
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    axes[0, 0].imshow(image_rgb)
    axes[0, 0].set_title("Original")
    axes[0, 0].axis('off')

    # Grayscale
    axes[0, 1].imshow(gray, cmap='gray')
    axes[0, 1].set_title("Grayscale")
    axes[0, 1].axis('off')

    # Binary INV
    axes[0, 2].imshow(binary_inv, cmap='gray')
    axes[0, 2].set_title("Binary INV")
    axes[0, 2].axis('off')

    # Binary
    axes[1, 0].imshow(binary, cmap='gray')
    axes[1, 0].set_title("Binary")
    axes[1, 0].axis('off')

    # Contours overlay (BINARY_INV)
    contours_overlay = image_rgb.copy()
    if contours_inv:
        cv2.drawContours(contours_overlay, contours_inv[:10], -1, (0, 255, 0), 2)
    axes[1, 1].imshow(contours_overlay)
    axes[1, 1].set_title(f"Contours INV ({len(contours_inv)} total)")
    axes[1, 1].axis('off')

    # Detection result
    result_overlay = image_rgb.copy()
    if result.grid_coordinates:
        x1, y1, x2, y2 = result.grid_coordinates
        cv2.rectangle(result_overlay, (x1, y1), (x2, y2), (255, 0, 0), 3)
        axes[1, 2].set_title(f"Detected: {result.confidence:.3f}")
    else:
        axes[1, 2].set_title("No Detection")
    axes[1, 2].imshow(result_overlay)
    axes[1, 2].axis('off')

    plt.tight_layout()
    plt.savefig(f"debug_{image_path.stem}.png", dpi=150, bbox_inches='tight')
    plt.show()

def main():
    """Main function"""
    dataset_path = Path("datasets/test")

    # Get first few images
    image_files = list(dataset_path.glob("*.jpg"))[:3]

    for image_path in image_files:
        debug_single_image(image_path)

if __name__ == "__main__":
    main()