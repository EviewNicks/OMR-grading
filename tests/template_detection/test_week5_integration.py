#!/usr/bin/env python3
"""
Week 5 Integration Validation Tests
MVP validation untuk quality-based parameter adaptation
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector
from template_detector.core.week5_integration import Week5PreprocessingResult, Week5IntegrationManager


def create_quality_image(quality_level="high", rotation_angle=0, size=(400, 300)):
    """Create image with specified quality characteristics - using working synthetic grid"""
    width, height = size

    # Create working synthetic grid (based on previous successful tests)
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

    # Apply quality-specific modifications
    if quality_level == "high":
        # High quality: minimal changes
        pass
    elif quality_level == "medium":
        # Medium quality: add some blur
        image = cv2.GaussianBlur(image, (5, 5), 0)
        noise = np.random.randint(-20, 21, image.shape, dtype=np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    else:  # low quality
        # Low quality: heavier blur and noise
        image = cv2.GaussianBlur(image, (9, 9), 0)
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


def create_mock_week5_result(quality_level="high"):
    """Create mock Week5PreprocessingResult"""
    if quality_level == "high":
        return Week5PreprocessingResult(
            filename=f"high_quality_test.jpg",
            file_size_kb=100.0,
            image_shape=(300, 400, 3),
            laplacian_variance=150.0,
            edge_density=0.3,
            blur_detected=False,
            blur_intensity=0.05,
            local_variance=80.0,
            high_freq_ratio=0.4,
            noise_reduction_detected=False,
            smoothness_score=0.9,
            rms_contrast=0.7,
            dynamic_range=250,
            low_light_detected=False,
            histogram_uniformity=0.8,
            contrast_enhanced=False,
            contrast_enhancement_intensity=0.0,
            overall_readiness=0.95,
            quality_score=0.9,
            recommendation="Excellent",
            contrast_readiness=0.95,
            sharpness_readiness=0.9,
            edge_readiness=0.95,
            sufficient_contrast=True,
            acceptable_blur=True,
            sufficient_edges=True,
            good_dynamic_range=True
        )
    elif quality_level == "medium":
        return Week5PreprocessingResult(
            filename=f"medium_quality_test.jpg",
            file_size_kb=100.0,
            image_shape=(300, 400, 3),
            laplacian_variance=100.0,
            edge_density=0.2,
            blur_detected=False,
            blur_intensity=0.1,
            local_variance=50.0,
            high_freq_ratio=0.3,
            noise_reduction_detected=False,
            smoothness_score=0.7,
            rms_contrast=0.5,
            dynamic_range=200,
            low_light_detected=False,
            histogram_uniformity=0.6,
            contrast_enhanced=False,
            contrast_enhancement_intensity=0.0,
            overall_readiness=0.75,
            quality_score=0.7,
            recommendation="Good",
            contrast_readiness=0.7,
            sharpness_readiness=0.6,
            edge_readiness=0.7,
            sufficient_contrast=True,
            acceptable_blur=True,
            sufficient_edges=True,
            good_dynamic_range=True
        )
    else:  # low quality
        return Week5PreprocessingResult(
            filename=f"low_quality_test.jpg",
            file_size_kb=100.0,
            image_shape=(300, 400, 3),
            laplacian_variance=50.0,
            edge_density=0.05,
            blur_detected=True,
            blur_intensity=0.3,
            local_variance=20.0,
            high_freq_ratio=0.1,
            noise_reduction_detected=True,
            smoothness_score=0.4,
            rms_contrast=0.3,
            dynamic_range=100,
            low_light_detected=True,
            histogram_uniformity=0.4,
            contrast_enhanced=True,
            contrast_enhancement_intensity=0.5,
            overall_readiness=0.4,
            quality_score=0.3,
            recommendation="Poor",
            contrast_readiness=0.3,
            sharpness_readiness=0.2,
            edge_readiness=0.4,
            sufficient_contrast=False,
            acceptable_blur=False,
            sufficient_edges=False,
            good_dynamic_range=False
        )


def test_parameter_adaptation():
    """Test parameter adaptation based on quality levels"""
    print("Test: Quality-Based Parameter Adaptation")
    print("-" * 40)

    quality_levels = ["high", "medium", "low"]
    adaptation_results = []

    for quality in quality_levels:
        # Create mock Week5 result
        week5_result = create_mock_week5_result(quality)

        # Create integration manager (mock files not needed for this test)
        manager = Week5IntegrationManager(
            Path("dummy_results.json"),
            Path("dummy_readiness.csv")
        )

        # Test parameter generation
        params = manager.get_adaptive_detection_parameters(week5_result)

        # Test config creation
        config = manager.create_rotation_robust_config(week5_result)

        # Validate adaptation
        if quality == "high":
            # High quality should use stricter parameters
            expected_rotation_robust = False
            expected_min_rect = 0.70
        elif quality == "medium":
            # Medium quality should use standard parameters
            expected_rotation_robust = True
            expected_min_rect = 0.60
        else:
            # Low quality should use relaxed parameters
            expected_rotation_robust = True
            expected_min_rect = 0.50

        # Test results
        rotation_correct = config.use_rotation_robust == expected_rotation_robust
        rect_correct = abs(config.min_rectangularity - expected_min_rect) < 0.01

        adaptation_correct = rotation_correct and rect_correct
        adaptation_results.append(adaptation_correct)

        print(f"  {quality.capitalize()} Quality:")
        print(f"    Rotation-robust: {config.use_rotation_robust} (expected: {expected_rotation_robust})")
        print(f"    Min rectangularity: {config.min_rectangularity:.2f} (expected: ~{expected_min_rect:.2f})")
        print(f"    Adaptation: {'PASS' if adaptation_correct else 'FAIL'}")

    # Summary
    success_count = sum(adaptation_results)
    print(f"\nParameter Adaptation Results: {success_count}/{len(quality_levels)} passed")
    return adaptation_results


def test_quality_based_detection():
    """Test detection with quality-based configuration"""
    print("\nTest: Quality-Based Detection")
    print("-" * 40)

    quality_levels = ["high", "medium", "low"]
    detection_results = []

    for quality in quality_levels:
        # Create image with corresponding quality
        image = create_quality_image(quality_level=quality, rotation_angle=15)

        # Create appropriate config
        week5_result = create_mock_week5_result(quality)
        manager = Week5IntegrationManager(
            Path("dummy_results.json"),
            Path("dummy_readiness.csv")
        )
        config = manager.create_rotation_robust_config(week5_result)

        # Test detection
        detector = ContourGridDetector(config)
        result = detector.detect_grid(image)

        # Validate detection
        # Use same threshold for all quality levels to test parameter adaptation
        threshold = 0.3

        success = result.confidence > threshold
        detection_results.append(success)

        print(f"  {quality.capitalize()} Quality:")
        print(f"    Confidence: {result.confidence:.3f}")
        print(f"    Rotation-robust: {result.rotation_robust}")
        print(f"    Detection: {'PASS' if success else 'FAIL'}")

    # Summary
    success_count = sum(detection_results)
    print(f"\nQuality-Based Detection Results: {success_count}/{len(quality_levels)} passed")
    return detection_results


def test_configuration_consistency():
    """Test configuration consistency across quality levels"""
    print("\nTest: Configuration Consistency")
    print("-" * 40)

    # Test that configuration follows expected patterns
    manager = Week5IntegrationManager(
        Path("dummy_results.json"),
        Path("dummy_readiness.csv")
    )

    quality_configs = {}
    for quality in ["high", "medium", "low"]:
        week5_result = create_mock_week5_result(quality)
        config = manager.create_rotation_robust_config(week5_result)
        quality_configs[quality] = config

    # Validate progression (should get more relaxed for lower quality)
    consistency_checks = []

    # Check rectangularity progression (should decrease for lower quality)
    high_rect = quality_configs["high"].min_rectangularity
    medium_rect = quality_configs["medium"].min_rectangularity
    low_rect = quality_configs["low"].min_rectangularity

    rect_progression = high_rect >= medium_rect >= low_rect
    consistency_checks.append(rect_progression)

    print(f"Rectangularity progression: High={high_rect:.2f}, Medium={medium_rect:.2f}, Low={low_rect:.2f}")
    print(f"  Consistent: {'PASS' if rect_progression else 'FAIL'}")

    # Check area ratio progression (should get more relaxed for lower quality)
    high_min_ratio = quality_configs["high"].min_area_ratio
    medium_min_ratio = quality_configs["medium"].min_area_ratio
    low_min_ratio = quality_configs["low"].min_area_ratio

    area_progression = high_min_ratio >= medium_min_ratio >= low_min_ratio
    consistency_checks.append(area_progression)

    print(f"Area ratio progression: High={high_min_ratio:.2f}, Medium={medium_min_ratio:.2f}, Low={low_min_ratio:.2f}")
    print(f"  Consistent: {'PASS' if area_progression else 'FAIL'}")

    # Check rotation-robust flag progression (should be enabled for lower quality)
    high_rotation = quality_configs["high"].use_rotation_robust
    medium_rotation = quality_configs["medium"].use_rotation_robust
    low_rotation = quality_configs["low"].use_rotation_robust

    rotation_progression = not high_rotation and medium_rotation and low_rotation
    consistency_checks.append(rotation_progression)

    print(f"Rotation-robust progression: High={high_rotation}, Medium={medium_rotation}, Low={low_rotation}")
    print(f"  Consistent: {'PASS' if rotation_progression else 'FAIL'}")

    # Summary
    success_count = sum(consistency_checks)
    print(f"\nConfiguration Consistency Results: {success_count}/{len(consistency_checks)} passed")
    return consistency_checks


def main():
    """Run Week 5 integration tests"""
    print("Week 5 Integration Validation - MVP")
    print("=" * 50)

    # Test parameter adaptation
    adaptation_results = test_parameter_adaptation()

    # Test quality-based detection
    detection_results = test_quality_based_detection()

    # Test configuration consistency
    consistency_results = test_configuration_consistency()

    # Overall validation
    print("\n" + "=" * 50)
    print("Week 5 Integration MVP Summary")
    print("=" * 50)

    total_adaptation = sum(adaptation_results)
    total_detection = sum(detection_results)
    total_consistency = sum(consistency_results)

    max_adaptation = len(adaptation_results)
    max_detection = len(detection_results)
    max_consistency = len(consistency_results)

    adaptation_rate = total_adaptation / max_adaptation * 100
    detection_rate = total_detection / max_detection * 100
    consistency_rate = total_consistency / max_consistency * 100

    print(f"Parameter Adaptation: {total_adaptation}/{max_adaptation} ({adaptation_rate:.1f}%)")
    print(f"Quality-Based Detection: {total_detection}/{max_detection} ({detection_rate:.1f}%)")
    print(f"Configuration Consistency: {total_consistency}/{max_consistency} ({consistency_rate:.1f}%)")

    overall_score = (adaptation_rate + detection_rate + consistency_rate) / 3
    print(f"\nWeek 5 Integration MVP Score: {overall_score:.1f}%")

    if overall_score >= 80:
        print("Week 5 Integration MVP: PASSED - Excellent quality adaptation")
    elif overall_score >= 60:
        print("Week 5 Integration MVP: MARGINAL - Some adaptation issues")
    else:
        print("Week 5 Integration MVP: FAILED - Major integration problems")

    return overall_score >= 60


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)