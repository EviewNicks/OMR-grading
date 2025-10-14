#!/usr/bin/env python3
"""
Manual synthetic rotation tests runner
MVP validation for rotation invariance
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector


def create_synthetic_grid(rotation_angle=0, noise_level=0.0, size=(400, 300)):
    """Create synthetic OMR grid dengan rotation dan noise"""
    width, height = size

    # Create base image
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Draw main grid rectangle (3x20 OMR grid simulation)
    grid_width, grid_height = int(width * 0.15), int(height * 0.80)
    grid_x = (width - grid_width) // 2
    grid_y = (height - grid_height) // 2

    # Fill grid rectangle
    cv2.rectangle(image, (grid_x, grid_y), (grid_x + grid_width, grid_y + grid_height), 0, -1)

    # Add horizontal lines (20 rows)
    for i in range(1, 20):
        y = grid_y + (grid_height * i // 20)
        cv2.line(image, (grid_x, y), (grid_x + grid_width, y), 255, 1)

    # Add vertical lines (3 columns)
    for i in range(1, 3):
        x = grid_x + (grid_width * i // 3)
        cv2.line(image, (x, grid_y), (x, grid_y + grid_height), 255, 1)

    # Add noise
    if noise_level > 0:
        noise = np.random.randint(0, 256, image.shape, dtype=np.uint8)
        image = cv2.addWeighted(image, 1 - noise_level, noise, noise_level, 0)

    # Apply rotation
    if rotation_angle != 0:
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))

    # Convert to BGR
    image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image_bgr


def main():
    """Run synthetic rotation tests"""
    print("Synthetic Rotation Tests - MVP Validation")
    print("=" * 50)

    # Initialize detector
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

    # Test 1: Rotation invariance
    print("\nTest 1: Rotation Invariance")
    rotation_angles = [0, 15, 30, 45, 60, 90]
    rotation_results = []

    for angle in rotation_angles:
        image = create_synthetic_grid(rotation_angle=angle)
        result = detector.detect_grid(image)

        success = result.confidence > 0.5
        rotation_results.append(success)

        # Angle detection validation
        angle_ok = True
        if result.angle is not None:
            angle_diff = abs(result.angle - angle) % 90
            if angle_diff > 45:
                angle_diff = 90 - angle_diff
            angle_ok = angle_diff <= 15

        angle_str = f"{result.angle:.1f}" if result.angle is not None else "N/A"
        print(f"  {angle:3d}°: Confidence={result.confidence:.3f}, "
              f"Success={'PASS' if success else 'FAIL'}, "
              f"Angle={angle_str}° "
              f"{'OK' if angle_ok else 'BAD'}")

    # Summary
    success_count = sum(rotation_results)
    print(f"\n  Rotation Test Results: {success_count}/{len(rotation_angles)} passed")

    # Test 2: Noise tolerance
    print("\nTest 2: Noise Tolerance")
    noise_levels = [0.0, 0.1, 0.2, 0.3]
    noise_results = []

    for noise in noise_levels:
        image = create_synthetic_grid(rotation_angle=15, noise_level=noise)
        result = detector.detect_grid(image)

        # Different thresholds for different noise levels
        threshold = 0.5 if noise <= 0.1 else 0.3
        success = result.confidence > threshold
        noise_results.append(success)

        print(f"  Noise {noise:.1f}: Confidence={result.confidence:.3f}, "
              f"Success={'PASS' if success else 'FAIL'}")

    # Summary
    success_count = sum(noise_results)
    print(f"\n  Noise Test Results: {success_count}/{len(noise_levels)} passed")

    # Test 3: Grid size variations
    print("\nTest 3: Grid Size Variations")
    sizes = [(300, 200), (400, 300), (600, 400), (800, 600)]
    size_results = []

    for size in sizes:
        image = create_synthetic_grid(rotation_angle=25, size=size)
        result = detector.detect_grid(image)

        success = result.confidence > 0.3
        size_results.append(success)

        print(f"  Size {size}: Confidence={result.confidence:.3f}, "
              f"Success={'PASS' if success else 'FAIL'}")

    # Summary
    success_count = sum(size_results)
    print(f"\n  Size Test Results: {success_count}/{len(sizes)} passed")

    # Overall MVP validation
    print("\n" + "=" * 50)
    print("MVP Validation Summary")
    print("=" * 50)

    total_rotation = sum(rotation_results)
    total_noise = sum(noise_results)
    total_size = sum(size_results)

    max_rotation = len(rotation_results)
    max_noise = len(noise_levels)
    max_size = len(sizes)

    rotation_rate = total_rotation / max_rotation * 100
    noise_rate = total_noise / max_noise * 100
    size_rate = total_size / max_size * 100

    print(f"Rotation Invariance: {total_rotation}/{max_rotation} ({rotation_rate:.1f}%)")
    print(f"Noise Tolerance: {total_noise}/{max_noise} ({noise_rate:.1f}%)")
    print(f"Size Flexibility: {total_size}/{max_size} ({size_rate:.1f}%)")

    overall_score = (rotation_rate + noise_rate + size_rate) / 3
    print(f"\nOverall MVP Score: {overall_score:.1f}%")

    if overall_score >= 70:
        print("MVP VALIDATION: PASSED - Rotation-robust detection ready!")
    elif overall_score >= 50:
        print("MVP VALIDATION: MARGINAL - Some improvements needed")
    else:
        print("MVP VALIDATION: FAILED - Major issues to resolve")

    return overall_score >= 70


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)