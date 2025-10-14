#!/usr/bin/env python3
"""
Simple debug script tanpa matplotlib
"""

import cv2
import numpy as np
from pathlib import Path
import sys

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector

def debug_one_image():
    """Debug one image"""
    image_path = Path("datasets/test/009-Copy-2-_jpg.rf.71634524a2c9f00df3609418ff12e12c.jpg")

    print(f"Loading: {image_path.name}")
    image = cv2.imread(str(image_path))

    if image is None:
        print("ERROR: Cannot load image")
        return

    print(f"Image shape: {image.shape}")
    print(f"Image range: {image.min()} - {image.max()}")

    # Simple preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Test threshold methods
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
    print(f"Binary INV white pixels: {np.sum(binary_inv == 255)}")
    print(f"Binary white pixels: {np.sum(binary == 255)}")

    # Extract contours
    contours_inv, _ = cv2.findContours(binary_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_binary, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Contours (BINARY_INV): {len(contours_inv)}")
    print(f"Contours (BINARY): {len(contours_binary)}")

    # Create rotation detector
    config = ContourDetectionConfig(
        min_area=500,
        max_area=100000,
        aspect_ratio_min=0.05,
        aspect_ratio_max=5.0,
        rectangularity_threshold=0.4,
        approximation_epsilon=0.02,
        hierarchy_level=2,

        # Ultra-relaxed parameters
        min_area_ratio=0.01,
        max_area_ratio=0.90,
        min_aspect_ratio=0.01,
        max_aspect_ratio=0.95,
        min_rectangularity=0.30,

        use_rotation_robust=True,
        use_hybrid_threshold=True
    )

    detector = ContourGridDetector(config)

    # Test detection
    result = detector.detect_grid(image)

    print(f"\nDetection Results:")
    print(f"Confidence: {result.confidence}")
    print(f"Grid coordinates: {result.grid_coordinates}")
    print(f"Rotation robust: {result.rotation_robust}")
    print(f"Angle: {result.angle}")
    print(f"Error: {result.error_message}")
    print(f"Processing time: {result.processing_time}")

    # Test rotation-robust filtering manually
    if contours_inv:
        print(f"\nTesting rotation-robust filtering with {len(contours_inv)} contours...")
        filtered_data = detector._filter_contours_rotation_robust(contours_inv, image.shape)
        print(f"Filtered to {len(filtered_data)} contours")

        if filtered_data:
            print("Top 3 contours:")
            for i, data in enumerate(filtered_data[:3]):
                print(f"  {i+1}: area={data['area']:.0f}, ratio={data['aspect_ratio']:.3f}, "
                      f"rect={data['rectangularity']:.3f}, angle={data['angle']:.1f}")
        else:
            print("No contours passed filtering!")

            # Debug why no contours passed
            print("\nDebug filtering criteria:")
            h, w = image.shape[:2]
            image_area = h * w
            print(f"Image area: {image_area}")

            for i, contour in enumerate(contours_inv[:5]):
                props = detector._calculate_rotation_robust_properties(contour)
                area_ratio = props['area'] / image_area

                print(f"Contour {i+1}:")
                print(f"  Area: {props['area']:.0f} (ratio: {area_ratio:.3f})")
                print(f"  Aspect ratio: {props['aspect_ratio']:.3f}")
                print(f"  Rectangularity: {props['rectangularity']:.3f}")
                print(f"  Angle: {props['angle']:.1f}")

                # Check which filters fail
                fail_reasons = []
                if not (config.min_area_ratio <= area_ratio <= config.max_area_ratio):
                    fail_reasons.append(f"area_ratio {area_ratio:.3f} not in [{config.min_area_ratio}, {config.max_area_ratio}]")
                if not (config.min_aspect_ratio <= props['aspect_ratio'] <= config.max_aspect_ratio):
                    fail_reasons.append(f"aspect_ratio {props['aspect_ratio']:.3f} not in [{config.min_aspect_ratio}, {config.max_aspect_ratio}]")
                if props['rectangularity'] < config.min_rectangularity:
                    fail_reasons.append(f"rectangularity {props['rectangularity']:.3f} < {config.min_rectangularity}")

                if fail_reasons:
                    print(f"  FAILED: {'; '.join(fail_reasons)}")
                else:
                    print(f"  PASSED all filters!")

if __name__ == "__main__":
    debug_one_image()