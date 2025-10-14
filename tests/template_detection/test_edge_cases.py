#!/usr/bin/env python3
"""
Edge Case Testing untuk Rotation-Robust Contour Detection
MVP validation untuk challenging scenarios
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector


def create_low_contrast_grid(rotation_angle=0, contrast_level=0.3, size=(400, 300)):
    """Create low contrast grid image"""
    width, height = size

    # Create base image with reduced contrast
    background = int(255 * (1 - contrast_level/2))
    foreground = int(255 * contrast_level/2)

    image = np.ones((height, width), dtype=np.uint8) * background

    # Draw grid rectangle
    grid_width, grid_height = int(width * 0.15), int(height * 0.80)
    grid_x = (width - grid_width) // 2
    grid_y = (height - grid_height) // 2

    cv2.rectangle(image, (grid_x, grid_y), (grid_x + grid_width, grid_y + grid_height), foreground, -1)

    # Add some grid lines
    for i in range(1, 20):
        y = grid_y + (grid_height * i // 20)
        cv2.line(image, (grid_x, y), (grid_x + grid_width, y), background, 1)

    for i in range(1, 3):
        x = grid_x + (grid_width * i // 3)
        cv2.line(image, (x, grid_y), (x, grid_y + grid_height), background, 1)

    # Apply rotation
    if rotation_angle != 0:
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))

    # Convert to BGR
    image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image_bgr


def create_partial_grid(rotation_angle=0, visibility=0.5, size=(400, 300)):
    """Create partially visible grid image"""
    width, height = size
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Draw grid rectangle
    grid_width, grid_height = int(width * 0.15), int(height * 0.80)
    grid_x = (width - grid_width) // 2
    grid_y = (height - grid_height) // 2

    cv2.rectangle(image, (grid_x, grid_y), (grid_x + grid_width, grid_y + grid_height), 0, -1)

    # Create occlusion (simulate partial visibility)
    occlusion_width = int(grid_width * (1 - visibility))
    occlusion_x = grid_x + grid_width - occlusion_width
    cv2.rectangle(image, (occlusion_x, grid_y), (grid_x + grid_width, grid_y + grid_height), 255, -1)

    # Apply rotation
    if rotation_angle != 0:
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))

    # Convert to BGR
    image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image_bgr


def create_extreme_aspect_grid(aspect_ratio=0.1, rotation_angle=0, size=(400, 300)):
    """Create grid with extreme aspect ratio"""
    width, height = size
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Calculate grid dimensions based on aspect ratio
    if aspect_ratio < 1:
        # Tall grid
        grid_height = int(height * 0.6)
        grid_width = int(grid_height * aspect_ratio)
    else:
        # Wide grid
        grid_width = int(width * 0.6)
        grid_height = int(grid_width / aspect_ratio)

    grid_x = (width - grid_width) // 2
    grid_y = (height - grid_height) // 2

    cv2.rectangle(image, (grid_x, grid_y), (grid_x + grid_width, grid_y + grid_height), 0, -1)

    # Apply rotation
    if rotation_angle != 0:
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))

    # Convert to BGR
    image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image_bgr


def main():
    """Run edge case tests"""
    print("Edge Case Tests - MVP Validation")
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

        # Ultra-relaxed parameters for edge cases
        min_area_ratio=0.01,
        max_area_ratio=0.90,
        min_aspect_ratio=0.01,
        max_aspect_ratio=0.95,
        min_rectangularity=0.30,

        use_rotation_robust=True,
        use_hybrid_threshold=True
    )
    detector = ContourGridDetector(config)

    # Test 1: Low contrast scenarios
    print("\nTest 1: Low Contrast Scenarios")
    contrast_levels = [0.1, 0.2, 0.3, 0.4]
    contrast_results = []

    for contrast in contrast_levels:
        image = create_low_contrast_grid(rotation_angle=20, contrast_level=contrast)
        result = detector.detect_grid(image)

        success = result.confidence > 0.3  # Lower threshold for edge cases
        contrast_results.append(success)

        print(f"  Contrast {contrast:.1f}: Confidence={result.confidence:.3f}, "
              f"Success={'PASS' if success else 'FAIL'}")

    # Summary
    success_count = sum(contrast_results)
    print(f"\n  Contrast Test Results: {success_count}/{len(contrast_levels)} passed")

    # Test 2: Partial visibility scenarios
    print("\nTest 2: Partial Visibility Scenarios")
    visibility_levels = [0.8, 0.6, 0.4, 0.2]
    visibility_results = []

    for visibility in visibility_levels:
        image = create_partial_grid(rotation_angle=15, visibility=visibility)
        result = detector.detect_grid(image)

        success = result.confidence > 0.3
        visibility_results.append(success)

        print(f"  Visibility {visibility:.1f}: Confidence={result.confidence:.3f}, "
              f"Success={'PASS' if success else 'FAIL'}")

    # Summary
    success_count = sum(visibility_results)
    print(f"\n  Visibility Test Results: {success_count}/{len(visibility_levels)} passed")

    # Test 3: Extreme aspect ratios
    print("\nTest 3: Extreme Aspect Ratios")
    aspect_ratios = [0.1, 0.2, 0.5, 2.0, 5.0, 10.0]
    aspect_results = []

    for ratio in aspect_ratios:
        image = create_extreme_aspect_grid(aspect_ratio=ratio, rotation_angle=10)
        result = detector.detect_grid(image)

        success = result.confidence > 0.3
        aspect_results.append(success)

        print(f"  Aspect {ratio:.1f}: Confidence={result.confidence:.3f}, "
              f"Success={'PASS' if success else 'FAIL'}")

    # Summary
    success_count = sum(aspect_results)
    print(f"\n  Aspect Ratio Test Results: {success_count}/{len(aspect_ratios)} passed")

    # Overall edge case validation
    print("\n" + "=" * 50)
    print("Edge Case MVP Validation Summary")
    print("=" * 50)

    total_contrast = sum(contrast_results)
    total_visibility = sum(visibility_results)
    total_aspect = sum(aspect_results)

    max_contrast = len(contrast_levels)
    max_visibility = len(visibility_levels)
    max_aspect = len(aspect_ratios)

    contrast_rate = total_contrast / max_contrast * 100
    visibility_rate = total_visibility / max_visibility * 100
    aspect_rate = total_aspect / max_aspect * 100

    print(f"Low Contrast Handling: {total_contrast}/{max_contrast} ({contrast_rate:.1f}%)")
    print(f"Partial Visibility: {total_visibility}/{max_visibility} ({visibility_rate:.1f}%)")
    print(f"Extreme Aspect Ratios: {total_aspect}/{max_aspect} ({aspect_rate:.1f}%)")

    overall_score = (contrast_rate + visibility_rate + aspect_rate) / 3
    print(f"\nEdge Case MVP Score: {overall_score:.1f}%")

    if overall_score >= 60:
        print("Edge Case MVP: PASSED - Good robustness for edge cases")
    elif overall_score >= 40:
        print("Edge Case MVP: MARGINAL - Some edge cases challenging")
    else:
        print("Edge Case MVP: FAILED - Significant edge case issues")

    return overall_score >= 60


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)