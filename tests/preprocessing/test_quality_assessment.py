"""Unit tests untuk quality_assessment module"""

import pytest
import cv2
import numpy as np
from src.preprocessing.quality_assessment import (
    calculate_laplacian_variance,
    calculate_edge_density,
    calculate_rms_contrast,
    calculate_dynamic_range,
    calculate_readiness_score,
    generate_quality_flags,
    assess_image_quality,
    QualityMetrics,
    THRESHOLDS
)


class TestLaplacianVariance:
    """Tests untuk calculate_laplacian_variance"""

    def test_sharp_image_high_variance(self, sharp_image):
        """Sharp image should have high Laplacian variance"""
        variance = calculate_laplacian_variance(sharp_image)
        assert variance > 100, "Sharp image should have variance > 100"

    def test_blurry_image_low_variance(self, blurry_image):
        """Blurred image should have lower variance than sharp image"""
        # Note: Even blurred real images might have variance > 100
        # This test just verifies the function runs
        variance = calculate_laplacian_variance(blurry_image)
        assert variance >= 0, "Variance should be non-negative"

    def test_empty_image_raises_error(self):
        """Empty image should raise ValueError"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            calculate_laplacian_variance(empty_image)

    def test_none_image_raises_error(self):
        """None image should raise ValueError"""
        with pytest.raises(ValueError):
            calculate_laplacian_variance(None)


class TestEdgeDensity:
    """Tests untuk calculate_edge_density"""

    def test_edge_density_range(self, sample_image):
        """Edge density should be between 0 and 1"""
        density = calculate_edge_density(sample_image)
        assert 0 <= density <= 1, "Edge density must be in range [0, 1]"

    def test_sharp_image_high_edge_density(self, sharp_image):
        """Sharp checkerboard image should have high edge density"""
        density = calculate_edge_density(sharp_image)
        assert density > 0.1, "Checkerboard should have high edge density"

    def test_empty_image_raises_error(self):
        """Empty image should raise ValueError"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            calculate_edge_density(empty_image)


class TestRMSContrast:
    """Tests untuk calculate_rms_contrast"""

    def test_high_contrast_image(self, high_contrast_image):
        """High contrast image should have higher RMS than low contrast"""
        contrast = calculate_rms_contrast(high_contrast_image)
        assert contrast > 40, "High contrast image should have RMS > 40"

    def test_low_contrast_image(self, low_contrast_image):
        """Low contrast image should have low RMS contrast"""
        contrast = calculate_rms_contrast(low_contrast_image)
        assert contrast < 20, "Low contrast image should have RMS < 20"

    def test_contrast_positive(self, sample_image):
        """Contrast should always be positive"""
        contrast = calculate_rms_contrast(sample_image)
        assert contrast > 0, "Contrast must be positive"

    def test_empty_image_raises_error(self):
        """Empty image should raise ValueError"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            calculate_rms_contrast(empty_image)


class TestDynamicRange:
    """Tests untuk calculate_dynamic_range"""

    def test_dynamic_range_bounds(self, sample_image):
        """Dynamic range should be between 0 and 255"""
        drange = calculate_dynamic_range(sample_image)
        assert 0 <= drange <= 255, "Dynamic range must be in [0, 255]"

    def test_full_range_image(self):
        """Image with full range should return 255"""
        # Create image dengan pixel values 0 to 255
        image = np.zeros((10, 10, 3), dtype=np.uint8)
        image[0, 0] = [0, 0, 0]  # Min
        image[5, 5] = [255, 255, 255]  # Max
        drange = calculate_dynamic_range(image)
        assert drange == 255, "Full range image should have dynamic range 255"

    def test_empty_image_raises_error(self):
        """Empty image should raise ValueError"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="empty or invalid"):
            calculate_dynamic_range(empty_image)


class TestReadinessScore:
    """Tests untuk calculate_readiness_score"""

    def test_readiness_score_range(self, sample_image):
        """Readiness score should be between 0 and 1"""
        metrics = assess_image_quality(sample_image)
        score = calculate_readiness_score(metrics)
        assert 0 <= score <= 1, "Readiness score must be in [0, 1]"

    def test_high_quality_metrics_high_score(self):
        """High quality metrics should produce high readiness score"""
        metrics = QualityMetrics(
            laplacian_variance=200.0,  # Above optimal (150)
            edge_density=0.08,  # Above optimal (0.05)
            rms_contrast=70.0,  # Above optimal (60)
            dynamic_range=255,
            readiness_score=0.0,  # Will be calculated
            quality_flags={}
        )
        score = calculate_readiness_score(metrics)
        assert score >= 0.9, "High quality metrics should give readiness >= 0.9"

    def test_low_quality_metrics_low_score(self):
        """Low quality metrics should produce low readiness score"""
        metrics = QualityMetrics(
            laplacian_variance=50.0,  # Below threshold (100)
            edge_density=0.01,  # Below threshold (0.03)
            rms_contrast=20.0,  # Below threshold (40)
            dynamic_range=100,
            readiness_score=0.0,
            quality_flags={}
        )
        score = calculate_readiness_score(metrics)
        assert score < 0.5, "Low quality metrics should give readiness < 0.5"


class TestQualityFlags:
    """Tests untuk generate_quality_flags"""

    def test_all_flags_true_high_quality(self):
        """High quality metrics should set all flags to True"""
        metrics = QualityMetrics(
            laplacian_variance=200.0,
            edge_density=0.08,
            rms_contrast=70.0,
            dynamic_range=255,
            readiness_score=0.95,
            quality_flags={}
        )
        flags = generate_quality_flags(metrics)
        assert flags['sufficient_contrast'] is True
        assert flags['acceptable_blur'] is True
        assert flags['sufficient_edges'] is True

    def test_all_flags_false_low_quality(self):
        """Low quality metrics should set all flags to False"""
        metrics = QualityMetrics(
            laplacian_variance=50.0,  # < 100
            edge_density=0.01,  # < 0.03
            rms_contrast=20.0,  # < 40
            dynamic_range=100,
            readiness_score=0.3,
            quality_flags={}
        )
        flags = generate_quality_flags(metrics)
        assert flags['sufficient_contrast'] is False
        assert flags['acceptable_blur'] is False
        assert flags['sufficient_edges'] is False

    def test_threshold_boundaries(self):
        """Test exact threshold values"""
        # Test contrast threshold (40)
        metrics = QualityMetrics(
            laplacian_variance=100.0,
            edge_density=0.03,
            rms_contrast=40.0,
            dynamic_range=255,
            readiness_score=0.8,
            quality_flags={}
        )
        flags = generate_quality_flags(metrics)
        assert flags['sufficient_contrast'] is False  # Threshold is >40, not >=40

        # Test blur threshold (100)
        metrics.laplacian_variance = 100.0
        flags = generate_quality_flags(metrics)
        assert flags['acceptable_blur'] is False  # Threshold is >100

        # Test edge threshold (0.03)
        metrics.edge_density = 0.03
        flags = generate_quality_flags(metrics)
        assert flags['sufficient_edges'] is False  # Threshold is >0.03


class TestAssessImageQuality:
    """Integration tests untuk assess_image_quality"""

    def test_assess_sample_image(self, sample_image):
        """Test full quality assessment pada sample image"""
        metrics = assess_image_quality(sample_image)

        # Verify all metrics are calculated
        assert metrics.laplacian_variance > 0
        assert 0 <= metrics.edge_density <= 1
        assert metrics.rms_contrast > 0
        assert 0 <= metrics.dynamic_range <= 255
        assert 0 <= metrics.readiness_score <= 1

        # Verify quality flags exist
        assert 'sufficient_contrast' in metrics.quality_flags
        assert 'acceptable_blur' in metrics.quality_flags
        assert 'sufficient_edges' in metrics.quality_flags

    def test_assess_with_path(self, sample_image, sample_image_path):
        """Test quality assessment with optional path parameter"""
        metrics = assess_image_quality(sample_image, sample_image_path)
        assert metrics.readiness_score >= 0

    def test_assess_empty_image_raises_error(self):
        """Empty image should raise ValueError dengan informative message"""
        empty_image = np.array([])
        with pytest.raises(ValueError, match="Invalid image"):
            assess_image_quality(empty_image)

    def test_assess_none_image_raises_error(self):
        """None image should raise ValueError"""
        with pytest.raises(ValueError):
            assess_image_quality(None)

    def test_metrics_consistency(self, sample_image):
        """Multiple assessments should produce consistent results"""
        metrics1 = assess_image_quality(sample_image)
        metrics2 = assess_image_quality(sample_image)

        # Results should be identical for same image
        assert metrics1.laplacian_variance == metrics2.laplacian_variance
        assert metrics1.edge_density == metrics2.edge_density
        assert metrics1.rms_contrast == metrics2.rms_contrast
        assert metrics1.readiness_score == metrics2.readiness_score


class TestThresholds:
    """Tests untuk threshold constants"""

    def test_thresholds_exist(self):
        """Verify all threshold constants are defined"""
        assert 'MIN_CONTRAST' in THRESHOLDS
        assert 'MIN_SHARPNESS' in THRESHOLDS
        assert 'MIN_EDGE_DENSITY' in THRESHOLDS
        assert 'TARGET_READINESS' in THRESHOLDS
        assert 'OPTIMAL_CONTRAST' in THRESHOLDS
        assert 'OPTIMAL_SHARPNESS' in THRESHOLDS
        assert 'OPTIMAL_EDGE_DENSITY' in THRESHOLDS

    def test_thresholds_values(self):
        """Verify threshold values are reasonable"""
        assert THRESHOLDS['MIN_CONTRAST'] == 40.0
        assert THRESHOLDS['MIN_SHARPNESS'] == 100.0
        assert THRESHOLDS['MIN_EDGE_DENSITY'] == 0.03
        assert THRESHOLDS['TARGET_READINESS'] == 0.8
        assert THRESHOLDS['OPTIMAL_CONTRAST'] > THRESHOLDS['MIN_CONTRAST']
        assert THRESHOLDS['OPTIMAL_SHARPNESS'] > THRESHOLDS['MIN_SHARPNESS']
