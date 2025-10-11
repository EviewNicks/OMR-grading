"""Unit tests untuk morphological_ops module"""

import pytest
import cv2
import numpy as np
from src.preprocessing.morphological_ops import (
    create_kernel,
    apply_opening,
    apply_closing,
    apply_combined_morphology,
    apply_morphology,
    MorphologyConfig,
    OPERATION_BENCHMARKS,
    RECOMMENDED_CONFIGS
)


def calculate_edge_density(image: np.ndarray) -> float:
    """Helper: Calculate edge density untuk testing"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    edges = cv2.Canny(gray, 50, 150)
    return float(np.sum(edges > 0) / edges.size)


class TestMorphologyConfig:
    """Tests untuk MorphologyConfig dataclass"""

    def test_default_config(self):
        """Default config should use opening dengan kernel=3"""
        config = MorphologyConfig()
        assert config.operations == ["opening"]
        assert config.kernel_size == 3
        assert config.kernel_shape == "rect"

    def test_custom_config(self):
        """Custom config should accept all parameters"""
        config = MorphologyConfig(
            operations=["opening", "closing"],
            kernel_size=5,
            kernel_shape="ellipse",
            opening_kernel=3,
            closing_kernel=7
        )
        assert config.operations == ["opening", "closing"]
        assert config.kernel_size == 5
        assert config.kernel_shape == "ellipse"
        assert config.opening_kernel == 3
        assert config.closing_kernel == 7

    def test_invalid_operation(self):
        """Invalid operation should raise ValueError"""
        with pytest.raises(ValueError, match="Invalid operation"):
            MorphologyConfig(operations=["invalid"])

    def test_kernel_size_validation(self):
        """Kernel size should be odd and within range"""
        # Even kernel size
        with pytest.raises(ValueError, match="should be odd"):
            MorphologyConfig(kernel_size=4)

        # Too small
        with pytest.raises(ValueError, match="must be between"):
            MorphologyConfig(kernel_size=0)

        # Too large
        with pytest.raises(ValueError, match="must be between"):
            MorphologyConfig(kernel_size=20)

    def test_kernel_shape_validation(self):
        """Kernel shape should be valid"""
        with pytest.raises(ValueError, match="Invalid kernel_shape"):
            MorphologyConfig(kernel_shape="invalid")

    def test_specific_kernel_validation(self):
        """Specific kernel sizes should be odd and valid"""
        with pytest.raises(ValueError, match="opening_kernel must be odd"):
            MorphologyConfig(opening_kernel=4)

        with pytest.raises(ValueError, match="closing_kernel must be odd"):
            MorphologyConfig(closing_kernel=6)


class TestCreateKernel:
    """Tests untuk create_kernel function"""

    def test_rect_kernel(self):
        """Rectangle kernel should be all ones"""
        kernel = create_kernel(3, "rect")
        assert kernel.shape == (3, 3)
        assert np.all(kernel == 1)

    def test_ellipse_kernel(self):
        """Ellipse kernel should have appropriate shape"""
        kernel = create_kernel(5, "ellipse")
        assert kernel.shape == (5, 5)
        assert kernel.dtype == np.uint8

    def test_cross_kernel(self):
        """Cross kernel should have appropriate shape"""
        kernel = create_kernel(5, "cross")
        assert kernel.shape == (5, 5)
        assert kernel.dtype == np.uint8

    def test_invalid_shape(self):
        """Invalid shape should raise error"""
        with pytest.raises(ValueError, match="Unknown kernel shape"):
            create_kernel(3, "invalid")

    def test_different_sizes(self):
        """Different sizes should work"""
        for size in [3, 5, 7, 9]:
            kernel = create_kernel(size, "rect")
            assert kernel.shape == (size, size)


class TestApplyOpening:
    """Tests untuk apply_opening function"""

    def test_opening_reduces_noise(self, sample_image):
        """Opening should remove small artifacts"""
        # Add noise
        noisy = sample_image.copy()
        gray = cv2.cvtColor(noisy, cv2.COLOR_BGR2GRAY)

        # Add salt noise (white pixels)
        noise_mask = np.random.random(gray.shape) < 0.01
        gray[noise_mask] = 255

        # Apply opening
        cleaned = apply_opening(gray, kernel_size=3)

        # Should have fewer bright pixels
        assert np.sum(cleaned == 255) < np.sum(gray == 255)

    def test_opening_output_shape(self, sample_image):
        """Opening output should be grayscale with correct shape"""
        opened = apply_opening(sample_image, kernel_size=3)

        assert len(opened.shape) == 2
        assert opened.shape == sample_image.shape[:2]

    def test_opening_output_range(self, sample_image):
        """Opening output should be in valid range"""
        opened = apply_opening(sample_image)

        assert opened.min() >= 0
        assert opened.max() <= 255
        assert opened.dtype == np.uint8

    def test_opening_kernel_size_effect(self, sample_image):
        """Larger kernel should have stronger effect"""
        small = apply_opening(sample_image, kernel_size=3)
        large = apply_opening(sample_image, kernel_size=7)

        # Results should be different
        assert not np.array_equal(small, large)

    def test_opening_kernel_shapes(self, sample_image):
        """Different kernel shapes should work"""
        rect = apply_opening(sample_image, kernel_size=3, kernel_shape="rect")
        ellipse = apply_opening(sample_image, kernel_size=3, kernel_shape="ellipse")
        cross = apply_opening(sample_image, kernel_size=3, kernel_shape="cross")

        assert rect.shape == ellipse.shape == cross.shape

    def test_opening_empty_image_error(self):
        """Opening should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            apply_opening(empty_image)


class TestApplyClosing:
    """Tests untuk apply_closing function"""

    def test_closing_fills_holes(self):
        """Closing should fill small holes"""
        # Create image with small holes (1-2 pixel gaps)
        image = np.ones((100, 100), dtype=np.uint8) * 255
        image[45:47, 45:47] = 0  # 2x2 hole (fillable with kernel=3)
        image[50:52, 50:52] = 0  # Another 2x2 hole
        image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Apply closing with larger kernel
        filled = apply_closing(image_bgr, kernel_size=5)

        # Should have fewer or equal black pixels (some filled)
        assert np.sum(filled == 0) <= np.sum(image == 0)

    def test_closing_output_shape(self, sample_image):
        """Closing output should be grayscale with correct shape"""
        closed = apply_closing(sample_image, kernel_size=3)

        assert len(closed.shape) == 2
        assert closed.shape == sample_image.shape[:2]

    def test_closing_output_range(self, sample_image):
        """Closing output should be in valid range"""
        closed = apply_closing(sample_image)

        assert closed.min() >= 0
        assert closed.max() <= 255
        assert closed.dtype == np.uint8

    def test_closing_kernel_size_effect(self, sample_image):
        """Larger kernel should have stronger effect"""
        small = apply_closing(sample_image, kernel_size=3)
        large = apply_closing(sample_image, kernel_size=7)

        # Results should be different
        assert not np.array_equal(small, large)

    def test_closing_empty_image_error(self):
        """Closing should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            apply_closing(empty_image)


class TestApplyCombinedMorphology:
    """Tests untuk apply_combined_morphology function"""

    def test_combined_operations(self, sample_image):
        """Combined operations should apply opening then closing"""
        combined = apply_combined_morphology(sample_image, opening_kernel=3, closing_kernel=3)

        assert combined is not None
        assert len(combined.shape) == 2
        assert combined.dtype == np.uint8

    def test_combined_different_kernels(self, sample_image):
        """Different kernel combinations should work"""
        combo1 = apply_combined_morphology(sample_image, opening_kernel=3, closing_kernel=3)
        combo2 = apply_combined_morphology(sample_image, opening_kernel=5, closing_kernel=5)

        assert combo1.shape == combo2.shape
        # Results should be different
        assert not np.array_equal(combo1, combo2)

    def test_combined_output_range(self, sample_image):
        """Combined output should be in valid range"""
        combined = apply_combined_morphology(sample_image)

        assert combined.min() >= 0
        assert combined.max() <= 255

    def test_combined_empty_image_error(self):
        """Combined operations should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            apply_combined_morphology(empty_image)


class TestApplyMorphology:
    """Integration tests untuk apply_morphology function"""

    def test_morphology_default_opening(self, sample_image):
        """Default should use opening dengan kernel=3"""
        result = apply_morphology(sample_image)

        assert result is not None
        assert len(result.shape) == 2
        assert result.dtype == np.uint8

    def test_morphology_with_config(self, sample_image):
        """Morphology with config object should work"""
        config = MorphologyConfig(operations=["opening"], kernel_size=5)
        result = apply_morphology(sample_image, config)

        assert result is not None

    def test_morphology_operation_routing(self, sample_image):
        """Should correctly route to different operations"""
        # Opening only
        opening_result = apply_morphology(sample_image, operations=["opening"])
        assert opening_result is not None

        # Closing only
        closing_result = apply_morphology(sample_image, operations=["closing"])
        assert closing_result is not None

        # Combined
        combined_result = apply_morphology(sample_image, operations=["opening", "closing"])
        assert combined_result is not None

        # Results should be different
        assert not np.array_equal(opening_result, closing_result)

    def test_morphology_kwargs_override(self, sample_image):
        """Kwargs should override config parameters"""
        config = MorphologyConfig(operations=["opening"], kernel_size=3)

        # Override operations
        result1 = apply_morphology(sample_image, config, operations=["closing"])
        assert result1 is not None

        # Override kernel_size
        result2 = apply_morphology(sample_image, config, kernel_size=7)
        assert result2 is not None

    def test_morphology_specific_kernels(self, sample_image):
        """Specific kernel sizes should work"""
        result = apply_morphology(
            sample_image,
            operations=["opening", "closing"],
            opening_kernel=3,
            closing_kernel=5
        )
        assert result is not None

    def test_morphology_empty_image_error(self):
        """Morphology should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            apply_morphology(empty_image)

    def test_morphology_sequential_operations(self, sample_image):
        """Sequential operations should be applied in order"""
        config = MorphologyConfig(operations=["opening", "closing"], kernel_size=3)
        result = apply_morphology(sample_image, config)

        # Should successfully apply both operations
        assert result is not None
        assert result.shape == sample_image.shape[:2]


class TestBenchmarksAndRecommendations:
    """Tests untuk benchmark data dan recommended configs"""

    def test_benchmarks_exist(self):
        """Benchmark data should be defined"""
        assert 'opening' in OPERATION_BENCHMARKS
        assert 'closing' in OPERATION_BENCHMARKS
        assert 'combined' in OPERATION_BENCHMARKS

    def test_benchmark_structure(self):
        """Benchmarks should have expected structure"""
        for operation, configs in OPERATION_BENCHMARKS.items():
            for config_name, metrics in configs.items():
                assert 'edge_preservation' in metrics
                assert 'noise_reduction' in metrics
                assert 'visual_quality' in metrics

    def test_recommended_configs_exist(self):
        """Recommended configurations should be defined"""
        assert 'conservative' in RECOMMENDED_CONFIGS
        assert 'balanced' in RECOMMENDED_CONFIGS
        assert 'aggressive' in RECOMMENDED_CONFIGS
        assert 'very_aggressive' in RECOMMENDED_CONFIGS

    def test_recommended_configs_valid(self):
        """Recommended configs should be valid MorphologyConfig objects"""
        for name, config in RECOMMENDED_CONFIGS.items():
            assert isinstance(config, MorphologyConfig)
            assert all(op in ["opening", "closing"] for op in config.operations)

    def test_use_recommended_configs(self, sample_image):
        """Recommended configs should work in practice"""
        for name, config in RECOMMENDED_CONFIGS.items():
            result = apply_morphology(sample_image, config)
            assert result is not None
            assert result.shape == sample_image.shape[:2]


class TestEdgePreservation:
    """Tests untuk verify edge preservation characteristics"""

    def test_opening_preserves_edges_better(self, sample_image):
        """Opening should preserve more edges than closing"""
        opening_result = apply_opening(sample_image, kernel_size=3)
        closing_result = apply_closing(sample_image, kernel_size=3)

        opening_edges = calculate_edge_density(opening_result)
        closing_edges = calculate_edge_density(closing_result)

        # Opening should preserve more edges (notebook showed 1.005 vs 0.277)
        assert opening_edges > closing_edges

    def test_small_kernel_preserves_better(self, sample_image):
        """Smaller kernel should preserve more edges"""
        small_kernel = apply_opening(sample_image, kernel_size=3)
        large_kernel = apply_opening(sample_image, kernel_size=7)

        small_edges = calculate_edge_density(small_kernel)
        large_edges = calculate_edge_density(large_kernel)

        # Smaller kernel should preserve more edges
        assert small_edges >= large_edges

    def test_conservative_config_performance(self, sample_image):
        """Conservative config should preserve edges well"""
        config = RECOMMENDED_CONFIGS['conservative']
        result = apply_morphology(sample_image, config)

        original_edges = calculate_edge_density(sample_image)
        result_edges = calculate_edge_density(result)

        # Should preserve most edges (notebook showed 1.005 preservation ratio)
        preservation_ratio = result_edges / original_edges if original_edges > 0 else 0
        assert preservation_ratio > 0.8, "Conservative config should preserve >80% of edges"
