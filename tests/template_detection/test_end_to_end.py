#!/usr/bin/env python3
"""
End-to-End Workflow Testing
MVP validation untuk complete detection pipeline
"""

import cv2
import numpy as np
import sys
import json
from pathlib import Path
import time

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector
from template_detector.core.week5_integration import Week5PreprocessingResult, Week5IntegrationManager


def load_image(image_path):
    """Load image dari path"""
    try:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Cannot load image: {image_path}")
        return image
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return None


def test_complete_pipeline(image_path):
    """Test complete detection pipeline"""
    print(f"Testing pipeline with: {image_path.name}")
    print("-" * 50)

    # Step 1: Image loading
    start_time = time.time()
    image = load_image(image_path)
    if image is None:
        return {
            'filename': image_path.name,
            'pipeline_stage': 'image_loading',
            'success': False,
            'error': 'Failed to load image',
            'processing_time': time.time() - start_time
        }

    load_time = time.time() - start_time
    print(f"Image loaded: {image.shape} ({load_time:.3f}s)")

    # Step 2: Week 5 integration (if applicable)
    start_time = time.time()

    # Create mock Week5 result for testing
    mock_week5 = Week5PreprocessingResult(
        filename=image_path.name,
        file_size_kb=image.nbytes / 1024,
        image_shape=image.shape,
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

    # Create integration manager
    manager = Week5IntegrationManager(
        Path("dummy_results.json"),
        Path("dummy_readiness.csv")
    )

    # Get adaptive configuration
    config = manager.create_rotation_robust_config(mock_week5)
    integration_time = time.time() - start_time
    print(f"Week 5 integration: {config.use_rotation_robust} rotation-robust ({integration_time:.3f}s)")

    # Step 3: Detection
    start_time = time.time()
    detector = ContourGridDetector(config)
    result = detector.detect_grid(image)
    detection_time = time.time() - start_time
    print(f"Detection completed: confidence={result.confidence:.3f} ({detection_time:.3f}s)")

    # Step 4: Result validation
    start_time = time.time()

    # Basic validation checks
    validation_checks = []

    # Check result structure
    required_fields = ['grid_coordinates', 'confidence', 'rotation_robust', 'processing_time']
    structure_valid = all(hasattr(result, field) for field in required_fields)
    validation_checks.append(('structure', structure_valid))

    # Check data validity
    confidence_valid = 0.0 <= result.confidence <= 1.0
    validation_checks.append(('confidence', confidence_valid))

    # Check coordinates if detected
    coords_valid = True
    if result.grid_coordinates is not None:
        coords_valid = len(result.grid_coordinates) == 4 and all(isinstance(x, int) for x in result.grid_coordinates)
    validation_checks.append(('coordinates', coords_valid))

    validation_time = time.time() - start_time
    print(f"Validation completed: {sum(1 for v, valid in validation_checks if valid)}/{len(validation_checks)} checks passed ({validation_time:.3f}s)")

    # Overall pipeline success
    pipeline_success = result.confidence > 0.3 and all(valid for _, valid in validation_checks)
    total_time = load_time + integration_time + detection_time + validation_time

    return {
        'filename': image_path.name,
        'pipeline_stage': 'complete',
        'success': pipeline_success,
        'confidence': result.confidence,
        'grid_coordinates': result.grid_coordinates,
        'rotation_robust': result.rotation_robust,
        'angle': result.angle,
        'processing_time': total_time,
        'load_time': load_time,
        'integration_time': integration_time,
        'detection_time': detection_time,
        'validation_time': validation_time,
        'validation_checks': validation_checks,
        'error': result.error_message if not pipeline_success else None
    }


def test_error_handling():
    """Test error handling scenarios"""
    print("\nTest: Error Handling")
    print("-" * 30)

    # Test with invalid image path
    invalid_path = Path("nonexistent_image.jpg")
    result = test_complete_pipeline(invalid_path)

    error_handling_success = not result['success'] and result['error'] is not None
    print(f"Invalid image handling: {'PASS' if error_handling_success else 'FAIL'}")

    # Test with corrupted image (create a tiny image)
    tiny_image = np.zeros((10, 10, 3), dtype=np.uint8)
    tiny_path = Path("tiny_test.jpg")
    cv2.imwrite(str(tiny_path), tiny_image)

    try:
        result = test_complete_pipeline(tiny_path)
        tiny_handling_success = not result['success'] and result['confidence'] == 0.0
        print(f"Tiny image handling: {'PASS' if tiny_handling_success else 'FAIL'}")
    finally:
        if tiny_path.exists():
            tiny_path.unlink()

    return error_handling_success and tiny_handling_success


def test_performance_benchmarks():
    """Test performance benchmarks"""
    print("\nTest: Performance Benchmarks")
    print("-" * 30)

    # Create synthetic test image
    image = np.ones((400, 300, 3), dtype=np.uint8) * 255
    grid_x, grid_y = 50, 40
    grid_width, grid_height = 60, 240
    cv2.rectangle(image, (grid_x, grid_y), (grid_x + grid_width, grid_y + grid_height), 0, -1)

    # Create config
    config = ContourDetectionConfig(
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

    detector = ContourGridDetector(config)

    # Benchmark multiple runs
    run_times = []
    for i in range(5):
        start_time = time.time()
        result = detector.detect_grid(image)
        end_time = time.time()
        run_times.append(end_time - start_time)

    avg_time = np.mean(run_times)
    max_time = np.max(run_times)
    min_time = np.min(run_times)
    std_time = np.std(run_times)

    print(f"Performance Results (5 runs):")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    print(f"  Std Dev: {std_time:.3f}s")

    # Performance criteria
    performance_ok = avg_time < 0.1  # Should be under 100ms for MVP
    print(f"Performance: {'PASS' if performance_ok else 'FAIL'}")

    return performance_ok


def main():
    """Run end-to-end workflow tests"""
    print("End-to-End Workflow Testing - MVP")
    print("=" * 50)

    # Test with real dataset
    dataset_path = Path("datasets/test")
    image_files = list(dataset_path.glob("*.jpg"))[:3]  # Test first 3 images

    if not image_files:
        print("No test images found in dataset")
        return False

    workflow_results = []

    for image_path in image_files:
        result = test_complete_pipeline(image_path)
        workflow_results.append(result)
        print(f"Overall: {'PASS' if result['success'] else 'FAIL'}")
        print()

    # Test error handling
    error_handling_success = test_error_handling()

    # Test performance benchmarks
    performance_success = test_performance_benchmarks()

    # Overall validation
    print("\n" + "=" * 50)
    print("End-to-End Workflow MVP Summary")
    print("=" * 50)

    # Calculate workflow success rate
    workflow_success_count = sum(1 for r in workflow_results if r['success'])
    workflow_success_rate = workflow_success_count / len(workflow_results) * 100 if workflow_results else 0

    # Calculate average processing time
    if workflow_results:
        avg_processing_time = np.mean([r['processing_time'] for r in workflow_results])
        max_processing_time = np.max([r['processing_time'] for r in workflow_results])
    else:
        avg_processing_time = 0
        max_processing_time = 0

    print(f"Workflow Success Rate: {workflow_success_count}/{len(workflow_results)} ({workflow_success_rate:.1f}%)")
    print(f"Average Processing Time: {avg_processing_time:.3f}s")
    print(f"Max Processing Time: {max_processing_time:.3f}s")
    print(f"Error Handling: {'PASS' if error_handling_success else 'FAIL'}")
    print(f"Performance Benchmarks: {'PASS' if performance_success else 'FAIL'}")

    # Overall MVP score
    workflow_weight = 0.5
    error_weight = 0.3
    performance_weight = 0.2

    overall_score = (
        workflow_success_rate * workflow_weight +
        (100 if error_handling_success else 0) * error_weight +
        (100 if performance_success else 0) * performance_weight
    )

    print(f"\nEnd-to-End MVP Score: {overall_score:.1f}%")

    if overall_score >= 70:
        print("End-to-End MVP: PASSED - Complete workflow robust")
    elif overall_score >= 50:
        print("End-to-End MVP: MARGINAL - Some workflow issues")
    else:
        print("End-to-End MVP: FAILED - Significant workflow problems")

    return overall_score >= 50


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)