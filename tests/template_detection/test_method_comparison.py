#!/usr/bin/env python3
"""
Method Comparison Framework Tests
MVP validation for Traditional vs Rotation-Robust methods
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector


def create_test_grid(rotation_angle=0, noise_level=0.0, size=(400, 300)):
    """Create test grid image"""
    width, height = size
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Draw grid rectangle
    grid_width, grid_height = int(width * 0.15), int(height * 0.80)
    grid_x = (width - grid_width) // 2
    grid_y = (height - grid_height) // 2

    cv2.rectangle(image, (grid_x, grid_y), (grid_x + grid_width, grid_y + grid_height), 0, -1)

    # Add grid lines
    for i in range(1, 20):
        y = grid_y + (grid_height * i // 20)
        cv2.line(image, (grid_x, y), (grid_x + grid_width, y), 255, 1)

    for i in range(1, 3):
        x = grid_x + (grid_width * i // 3)
        cv2.line(image, (x, grid_y), (x, grid_y + grid_height), 255, 1)

    # Add noise
    if noise_level > 0:
        noise = np.random.randint(-50, 51, image.shape, dtype=np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Apply rotation
    if rotation_angle != 0:
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
        image = cv2.warpAffine(image, rotation_matrix, (width, height))

    # Convert to BGR
    image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image_bgr


def test_rotation_scenarios():
    """Test performance across rotation scenarios"""
    print("Test: Rotation Scenario Comparison")
    print("-" * 40)

    # Create detectors
    traditional_config = ContourDetectionConfig(
        min_area=500,
        max_area=100000,
        aspect_ratio_min=0.05,
        aspect_ratio_max=5.0,
        rectangularity_threshold=0.4,
        approximation_epsilon=0.02,
        hierarchy_level=2,

        # Traditional parameters (no rotation support)
        use_rotation_robust=False,
        use_hybrid_threshold=False
    )

    rotation_config = ContourDetectionConfig(
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

    traditional_detector = ContourGridDetector(traditional_config)
    rotation_detector = ContourGridDetector(rotation_config)

    # Test rotation angles
    rotation_angles = [0, 15, 30, 45, 60, 90]
    comparison_results = []

    for angle in rotation_angles:
        image = create_test_grid(rotation_angle=angle)

        # Test traditional method
        traditional_result = traditional_detector.detect_grid(image)

        # Test rotation-robust method
        rotation_result = rotation_detector.detect_grid(image)

        # Compare results
        traditional_success = traditional_result.confidence > 0.3
        rotation_success = rotation_result.confidence > 0.3

        rotation_better = rotation_result.confidence > traditional_result.confidence
        improvement = rotation_result.confidence - traditional_result.confidence

        comparison_results.append({
            'angle': angle,
            'traditional_confidence': traditional_result.confidence,
            'rotation_confidence': rotation_result.confidence,
            'traditional_success': traditional_success,
            'rotation_success': rotation_success,
            'rotation_better': rotation_better,
            'improvement': improvement
        })

        print(f"  {angle:3d}°:")
        print(f"    Traditional: {traditional_result.confidence:.3f} ({'PASS' if traditional_success else 'FAIL'})")
        print(f"    Rotation:   {rotation_result.confidence:.3f} ({'PASS' if rotation_success else 'FAIL'})")
        print(f"    Advantage: {'ROTATION' if rotation_better else 'TRADITIONAL'} (+{improvement:.3f})")

    # Summary
    rotation_better_count = sum(1 for r in comparison_results if r['rotation_better'])
    print(f"\nRotation Scenario Results: {rotation_better_count}/{len(rotation_angles)} scenarios favor rotation-robust")
    return comparison_results


def test_noise_scenarios():
    """Test performance across noise levels"""
    print("\nTest: Noise Scenario Comparison")
    print("-" * 40)

    # Create detectors
    traditional_config = ContourDetectionConfig(
        min_area=500,
        max_area=100000,
        aspect_ratio_min=0.05,
        aspect_ratio_max=5.0,
        rectangularity_threshold=0.4,
        approximation_epsilon=0.02,
        hierarchy_level=2,

        use_rotation_robust=False,
        use_hybrid_threshold=False
    )

    rotation_config = ContourDetectionConfig(
        min_area=500,
        max_area=100000,
        aspect_ratio_min=0.05,
        aspect_ratio_max=5.0,
        rectangularity_threshold=0.4,
        approximation_epsilon=0.02,
        hierarchy_level=2,

        min_area_ratio=0.01,
        max_area_ratio=0.90,
        min_aspect_ratio=0.01,
        max_aspect_ratio=0.95,
        min_rectangularity=0.30,

        use_rotation_robust=True,
        use_hybrid_threshold=True
    )

    traditional_detector = ContourGridDetector(traditional_config)
    rotation_detector = ContourGridDetector(rotation_config)

    # Test noise levels
    noise_levels = [0.0, 0.1, 0.2, 0.3]
    noise_results = []

    for noise in noise_levels:
        image = create_test_grid(rotation_angle=15, noise_level=noise)

        # Test traditional method
        traditional_result = traditional_detector.detect_grid(image)

        # Test rotation-robust method
        rotation_result = rotation_detector.detect_grid(image)

        # Compare results
        traditional_success = traditional_result.confidence > 0.3
        rotation_success = rotation_result.confidence > 0.3

        rotation_better = rotation_result.confidence > traditional_result.confidence
        improvement = rotation_result.confidence - traditional_result.confidence

        noise_results.append({
            'noise_level': noise,
            'traditional_confidence': traditional_result.confidence,
            'rotation_confidence': rotation_result.confidence,
            'traditional_success': traditional_success,
            'rotation_success': rotation_success,
            'rotation_better': rotation_better,
            'improvement': improvement
        })

        print(f"  Noise {noise:.1f}:")
        print(f"    Traditional: {traditional_result.confidence:.3f} ({'PASS' if traditional_success else 'FAIL'})")
        print(f"    Rotation:   {rotation_result.confidence:.3f} ({'PASS' if rotation_success else 'FAIL'})")
        print(f"    Advantage: {'ROTATION' if rotation_better else 'TRADITIONAL'} (+{improvement:.3f})")

    # Summary
    rotation_better_count = sum(1 for r in noise_results if r['rotation_better'])
    print(f"\nNoise Scenario Results: {rotation_better_count}/{len(noise_levels)} scenarios favor rotation-robust")
    return noise_results


def test_real_dataset():
    """Test with real dataset images"""
    print("\nTest: Real Dataset Comparison")
    print("-" * 40)

    # Create detectors
    traditional_config = ContourDetectionConfig(
        min_area=500,
        max_area=100000,
        aspect_ratio_min=0.05,
        aspect_ratio_max=5.0,
        rectangularity_threshold=0.4,
        approximation_epsilon=0.02,
        hierarchy_level=2,

        use_rotation_robust=False,
        use_hybrid_threshold=False
    )

    rotation_config = ContourDetectionConfig(
        min_area=500,
        max_area=100000,
        aspect_ratio_min=0.05,
        aspect_ratio_max=5.0,
        rectangularity_threshold=0.4,
        approximation_epsilon=0.02,
        hierarchy_level=2,

        min_area_ratio=0.01,
        max_area_ratio=0.90,
        min_aspect_ratio=0.01,
        max_aspect_ratio=0.95,
        min_rectangularity=0.30,

        use_rotation_robust=True,
        use_hybrid_threshold=True
    )

    traditional_detector = ContourGridDetector(traditional_config)
    rotation_detector = ContourGridDetector(rotation_config)

    # Get first few images from test dataset
    dataset_path = Path("datasets/test")
    image_files = list(dataset_path.glob("*.jpg"))[:5]  # Test first 5 images

    if not image_files:
        print("  No real dataset images found")
        return []

    real_results = []

    for image_path in image_files:
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            # Test traditional method
            traditional_result = traditional_detector.detect_grid(image)

            # Test rotation-robust method
            rotation_result = rotation_detector.detect_grid(image)

            # Compare results
            traditional_success = traditional_result.confidence > 0.3
            rotation_success = rotation_result.confidence > 0.3

            rotation_better = rotation_result.confidence > traditional_result.confidence
            improvement = rotation_result.confidence - traditional_result.confidence

            real_results.append({
                'filename': image_path.name,
                'traditional_confidence': traditional_result.confidence,
                'rotation_confidence': rotation_result.confidence,
                'traditional_success': traditional_success,
                'rotation_success': rotation_success,
                'rotation_better': rotation_better,
                'improvement': improvement
            })

            print(f"  {image_path.name}:")
            print(f"    Traditional: {traditional_result.confidence:.3f} ({'PASS' if traditional_success else 'FAIL'})")
            print(f"    Rotation:   {rotation_result.confidence:.3f} ({'PASS' if rotation_success else 'FAIL'})")
            print(f"    Advantage: {'ROTATION' if rotation_better else 'TRADITIONAL'} (+{improvement:.3f})")

        except Exception as e:
            print(f"  {image_path.name}: ERROR - {str(e)}")
            continue

    # Summary
    if real_results:
        rotation_better_count = sum(1 for r in real_results if r['rotation_better'])
        print(f"\nReal Dataset Results: {rotation_better_count}/{len(real_results)} images favor rotation-robust")

        # Calculate average improvements
        avg_improvement = np.mean([r['improvement'] for r in real_results])
        print(f"Average improvement: +{avg_improvement:.3f}")

    return real_results


def main():
    """Run method comparison tests"""
    print("Method Comparison Framework - MVP Validation")
    print("=" * 50)

    # Test rotation scenarios
    rotation_results = test_rotation_scenarios()

    # Test noise scenarios
    noise_results = test_noise_scenarios()

    # Test real dataset
    real_results = test_real_dataset()

    # Overall validation
    print("\n" + "=" * 50)
    print("Method Comparison MVP Summary")
    print("=" * 50)

    # Calculate success metrics
    rotation_wins_rotation = sum(1 for r in rotation_results if r['rotation_better'])
    rotation_wins_noise = sum(1 for r in noise_results if r['rotation_better'])
    rotation_wins_real = sum(1 for r in real_results if r['rotation_better']) if real_results else 0

    total_rotation = len(rotation_results)
    total_noise = len(noise_results)
    total_real = len(real_results) if real_results else 0

    rotation_win_rate = rotation_wins_rotation / total_rotation * 100
    noise_win_rate = rotation_wins_noise / total_noise * 100
    real_win_rate = rotation_wins_real / total_real * 100 if total_real > 0 else 0

    print(f"Rotation Scenarios: {rotation_wins_rotation}/{total_rotation} ({rotation_win_rate:.1f}%) favor rotation-robust")
    print(f"Noise Scenarios: {rotation_wins_noise}/{total_noise} ({noise_win_rate:.1f}%) favor rotation-robust")
    print(f"Real Dataset: {rotation_wins_real}/{total_real} ({real_win_rate:.1f}%) favor rotation-robust")

    # Calculate average improvements
    rotation_improvement = np.mean([r['improvement'] for r in rotation_results])
    noise_improvement = np.mean([r['improvement'] for r in noise_results])
    real_improvement = np.mean([r['improvement'] for r in real_results]) if real_results else 0

    print(f"\nAverage Improvements:")
    print(f"  Rotation scenarios: +{rotation_improvement:.3f}")
    print(f"  Noise scenarios: +{noise_improvement:.3f}")
    print(f"  Real dataset: +{real_improvement:.3f}")

    # Overall score
    if total_real > 0:
        overall_score = (rotation_win_rate + noise_win_rate + real_win_rate) / 3
    else:
        overall_score = (rotation_win_rate + noise_win_rate) / 2

    print(f"\nMethod Comparison MVP Score: {overall_score:.1f}%")

    if overall_score >= 70:
        print("Method Comparison MVP: PASSED - Rotation-robust significantly better")
    elif overall_score >= 50:
        print("Method Comparison MVP: MARGINAL - Rotation-robust moderately better")
    else:
        print("Method Comparison MVP: FAILED - No clear advantage")

    return overall_score >= 50


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)