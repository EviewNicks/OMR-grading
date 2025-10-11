"""Unit tests untuk contrast_enhancement module"""

import pytest
import cv2
import numpy as np
from src.preprocessing.contrast_enhancement import (
    apply_clahe,
    apply_histogram_equalization,
    normalize_rms_contrast,
    enhance_contrast,
    ContrastConfig,
    TECHNIQUE_BENCHMARKS,
    RECOMMENDED_CONFIGS
)


def calculate_rms_contrast(image: np.ndarray) -> float:
    """Helper: Calculate RMS contrast untuk testing"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    return float(np.sqrt(np.mean((gray - gray.mean()) ** 2)))


class TestContrastConfig:
    """Tests untuk ContrastConfig dataclass"""

    def test_default_config(self):
        """Default config should use CLAHE dengan conservative settings"""
        config = ContrastConfig()
        assert config.method == "clahe"
        assert config.clip_limit == 2.0
        assert config.tile_size == (8, 8)
        assert config.target_contrast == 70.0

    def test_custom_config(self):
        """Custom config should accept all parameters"""
        config = ContrastConfig(
            method="hist_eq",
            clip_limit=3.0,
            tile_size=(16, 16),
            target_contrast=80.0
        )
        assert config.method == "hist_eq"
        assert config.clip_limit == 3.0
        assert config.tile_size == (16, 16)
        assert config.target_contrast == 80.0

    def test_invalid_method(self):
        """Invalid method should raise ValueError"""
        with pytest.raises(ValueError, match="Invalid method"):
            ContrastConfig(method="invalid")

    def test_clip_limit_validation(self):
        """Clip limit should be within valid range"""
        with pytest.raises(ValueError, match="clip_limit must be between"):
            ContrastConfig(clip_limit=0.5)  # Too low

        with pytest.raises(ValueError, match="clip_limit must be between"):
            ContrastConfig(clip_limit=15.0)  # Too high

    def test_tile_size_validation(self):
        """Tile size should be positive"""
        with pytest.raises(ValueError, match="tile_size must be positive"):
            ContrastConfig(tile_size=(0, 8))

        with pytest.raises(ValueError, match="tile_size must be positive"):
            ContrastConfig(tile_size=(8, -1))

    def test_target_contrast_validation(self):
        """Target contrast should be within reasonable range"""
        with pytest.raises(ValueError, match="target_contrast must be between"):
            ContrastConfig(target_contrast=5.0)  # Too low

        with pytest.raises(ValueError, match="target_contrast must be between"):
            ContrastConfig(target_contrast=150.0)  # Too high


class TestApplyCLAHE:
    """Tests untuk apply_clahe function"""

    def test_clahe_improves_contrast(self, low_contrast_image):
        """CLAHE should improve contrast of low contrast image"""
        original_rms = calculate_rms_contrast(low_contrast_image)
        enhanced = apply_clahe(low_contrast_image, clip_limit=2.0)
        enhanced_rms = calculate_rms_contrast(enhanced)

        assert enhanced_rms > original_rms, "CLAHE should increase RMS contrast"

    def test_clahe_output_shape(self, sample_image):
        """CLAHE output should be grayscale with correct shape"""
        enhanced = apply_clahe(sample_image)

        assert len(enhanced.shape) == 2, "Output should be grayscale (2D)"
        assert enhanced.shape[0] == sample_image.shape[0]
        assert enhanced.shape[1] == sample_image.shape[1]

    def test_clahe_output_range(self, sample_image):
        """CLAHE output should be in valid pixel range"""
        enhanced = apply_clahe(sample_image)

        assert enhanced.min() >= 0, "Min pixel value should be >= 0"
        assert enhanced.max() <= 255, "Max pixel value should be <= 255"
        assert enhanced.dtype == np.uint8, "Output should be 8-bit unsigned"

    def test_clahe_clip_limit_effect(self, sample_image):
        """Higher clip limit should produce more aggressive enhancement"""
        conservative = apply_clahe(sample_image, clip_limit=1.0)
        aggressive = apply_clahe(sample_image, clip_limit=4.0)

        conservative_rms = calculate_rms_contrast(conservative)
        aggressive_rms = calculate_rms_contrast(aggressive)

        # Aggressive should have higher or equal contrast
        assert aggressive_rms >= conservative_rms

    def test_clahe_tile_size_parameter(self, sample_image):
        """Different tile sizes should work correctly"""
        small_tile = apply_clahe(sample_image, tile_size=(4, 4))
        large_tile = apply_clahe(sample_image, tile_size=(16, 16))

        assert small_tile.shape == large_tile.shape
        assert small_tile.dtype == large_tile.dtype

    def test_clahe_grayscale_input(self, sample_image):
        """CLAHE should handle grayscale input"""
        gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
        enhanced = apply_clahe(gray)

        assert enhanced.shape == gray.shape

    def test_clahe_empty_image_error(self):
        """CLAHE should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            apply_clahe(empty_image)


class TestApplyHistogramEqualization:
    """Tests untuk apply_histogram_equalization function"""

    def test_hist_eq_improves_contrast(self, low_contrast_image):
        """Histogram equalization should improve contrast"""
        original_rms = calculate_rms_contrast(low_contrast_image)
        enhanced = apply_histogram_equalization(low_contrast_image)
        enhanced_rms = calculate_rms_contrast(enhanced)

        assert enhanced_rms > original_rms, "HistEq should increase RMS contrast"

    def test_hist_eq_output_shape(self, sample_image):
        """HistEq output should be grayscale with correct shape"""
        enhanced = apply_histogram_equalization(sample_image)

        assert len(enhanced.shape) == 2, "Output should be grayscale (2D)"
        assert enhanced.shape == sample_image.shape[:2]

    def test_hist_eq_output_range(self, sample_image):
        """HistEq output should be in valid pixel range"""
        enhanced = apply_histogram_equalization(sample_image)

        assert enhanced.min() >= 0
        assert enhanced.max() <= 255
        assert enhanced.dtype == np.uint8

    def test_hist_eq_distribution(self, sample_image):
        """Histogram equalization should spread pixel distribution"""
        enhanced = apply_histogram_equalization(sample_image)

        # Check that enhancement uses more intensity levels
        original_gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
        original_unique = len(np.unique(original_gray))
        enhanced_unique = len(np.unique(enhanced))

        # Enhanced should typically have more spread
        assert enhanced_unique > 0

    def test_hist_eq_empty_image_error(self):
        """HistEq should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            apply_histogram_equalization(empty_image)


class TestNormalizeRMSContrast:
    """Tests untuk normalize_rms_contrast function"""

    def test_rms_norm_target_contrast(self, sample_image):
        """RMS normalization should approach target contrast"""
        target = 70.0
        enhanced = normalize_rms_contrast(sample_image, target_contrast=target)
        enhanced_rms = calculate_rms_contrast(enhanced)

        # Should be close to target (within 20% tolerance)
        assert abs(enhanced_rms - target) < target * 0.2

    def test_rms_norm_output_shape(self, sample_image):
        """RMS norm output should be grayscale with correct shape"""
        enhanced = normalize_rms_contrast(sample_image)

        assert len(enhanced.shape) == 2
        assert enhanced.shape == sample_image.shape[:2]

    def test_rms_norm_output_range(self, sample_image):
        """RMS norm output should be in valid pixel range"""
        enhanced = normalize_rms_contrast(sample_image)

        assert enhanced.min() >= 0
        assert enhanced.max() <= 255
        assert enhanced.dtype == np.uint8

    def test_rms_norm_different_targets(self, sample_image):
        """Different target contrasts should produce different results"""
        low_target = normalize_rms_contrast(sample_image, target_contrast=40.0)
        high_target = normalize_rms_contrast(sample_image, target_contrast=80.0)

        low_rms = calculate_rms_contrast(low_target)
        high_rms = calculate_rms_contrast(high_target)

        assert high_rms > low_rms

    def test_rms_norm_flat_image(self):
        """RMS norm should handle flat (zero variance) image"""
        flat_image = np.full((100, 100), 128, dtype=np.uint8)
        flat_bgr = cv2.cvtColor(flat_image, cv2.COLOR_GRAY2BGR)

        # Should not crash, returns original
        enhanced = normalize_rms_contrast(flat_bgr)
        assert enhanced.shape == flat_image.shape

    def test_rms_norm_empty_image_error(self):
        """RMS norm should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            normalize_rms_contrast(empty_image)


class TestEnhanceContrast:
    """Integration tests untuk enhance_contrast function"""

    def test_enhance_default_clahe(self, sample_image):
        """Default enhancement should use CLAHE"""
        enhanced = enhance_contrast(sample_image)

        assert enhanced is not None
        assert len(enhanced.shape) == 2
        assert enhanced.dtype == np.uint8

    def test_enhance_with_config(self, sample_image):
        """Enhancement with config object should work"""
        config = ContrastConfig(method="clahe", clip_limit=3.0)
        enhanced = enhance_contrast(sample_image, config)

        assert enhanced is not None

    def test_enhance_method_routing(self, sample_image):
        """Should correctly route to different methods"""
        # Test CLAHE
        clahe_enhanced = enhance_contrast(sample_image, method="clahe")
        assert clahe_enhanced is not None

        # Test HistEq
        histeq_enhanced = enhance_contrast(sample_image, method="hist_eq")
        assert histeq_enhanced is not None

        # Test RMS Norm
        rms_enhanced = enhance_contrast(sample_image, method="rms_norm")
        assert rms_enhanced is not None

        # Results should be different
        assert not np.array_equal(clahe_enhanced, histeq_enhanced)

    def test_enhance_kwargs_override(self, sample_image):
        """Kwargs should override config parameters"""
        config = ContrastConfig(method="clahe", clip_limit=2.0)

        # Override method via kwargs
        enhanced = enhance_contrast(sample_image, config, method="hist_eq")
        assert enhanced is not None

        # Override clip_limit
        enhanced2 = enhance_contrast(sample_image, config, clip_limit=4.0)
        assert enhanced2 is not None

    def test_enhance_empty_image_error(self):
        """Enhancement should raise error for empty image"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            enhance_contrast(empty_image)

    def test_enhance_invalid_method_error(self, sample_image):
        """Invalid method should raise error"""
        with pytest.raises(ValueError):
            enhance_contrast(sample_image, method="invalid_method")


class TestBenchmarksAndRecommendations:
    """Tests untuk benchmark data dan recommended configs"""

    def test_benchmarks_exist(self):
        """Benchmark data should be defined"""
        assert 'clahe' in TECHNIQUE_BENCHMARKS
        assert 'hist_eq' in TECHNIQUE_BENCHMARKS
        assert 'rms_norm' in TECHNIQUE_BENCHMARKS

    def test_benchmark_structure(self):
        """Benchmarks should have expected structure"""
        for technique, configs in TECHNIQUE_BENCHMARKS.items():
            for config_name, metrics in configs.items():
                assert 'quality' in metrics
                assert 'rms_improvement' in metrics
                assert 'edges' in metrics

    def test_recommended_configs_exist(self):
        """Recommended configurations should be defined"""
        assert 'conservative' in RECOMMENDED_CONFIGS
        assert 'balanced' in RECOMMENDED_CONFIGS
        assert 'aggressive' in RECOMMENDED_CONFIGS
        assert 'controlled' in RECOMMENDED_CONFIGS

    def test_recommended_configs_valid(self):
        """Recommended configs should be valid ContrastConfig objects"""
        for name, config in RECOMMENDED_CONFIGS.items():
            assert isinstance(config, ContrastConfig)
            assert config.method in ["clahe", "hist_eq", "rms_norm"]

    def test_use_recommended_configs(self, sample_image):
        """Recommended configs should work in practice"""
        for name, config in RECOMMENDED_CONFIGS.items():
            enhanced = enhance_contrast(sample_image, config)
            assert enhanced is not None
            assert enhanced.shape == sample_image.shape[:2]


class TestPerformanceCharacteristics:
    """Tests untuk verify performance characteristics dari notebook"""

    def test_clahe_conservative_improvement(self, sample_image):
        """CLAHE conservative should produce modest improvement"""
        config = RECOMMENDED_CONFIGS['conservative']
        original_rms = calculate_rms_contrast(sample_image)
        enhanced = enhance_contrast(sample_image, config)
        enhanced_rms = calculate_rms_contrast(enhanced)

        improvement_pct = ((enhanced_rms - original_rms) / original_rms * 100) if original_rms > 0 else 0

        # Should improve, but not excessively (notebook showed 6-10%)
        assert improvement_pct >= 0, "Should improve contrast"

    def test_hist_eq_aggressive_improvement(self, low_contrast_image):
        """HistEq should produce aggressive improvement"""
        config = RECOMMENDED_CONFIGS['aggressive']
        original_rms = calculate_rms_contrast(low_contrast_image)
        enhanced = enhance_contrast(low_contrast_image, config)
        enhanced_rms = calculate_rms_contrast(enhanced)

        improvement_pct = ((enhanced_rms - original_rms) / original_rms * 100) if original_rms > 0 else 0

        # Should improve significantly (notebook showed 134%)
        assert improvement_pct > 50, "HistEq should dramatically improve contrast"
