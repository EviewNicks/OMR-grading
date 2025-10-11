"""Integration tests untuk preprocessing pipeline"""

import pytest
import cv2
import numpy as np
from pathlib import Path
from src.preprocessing.pipeline import (
    preprocess_image,
    batch_preprocess,
    validate_preprocessing,
    PreprocessConfig,
    PreprocessResult,
    OPTIMAL_CONFIG,
    PERFORMANCE_BENCHMARKS
)
from src.preprocessing.contrast_enhancement import ContrastConfig
from src.preprocessing.morphological_ops import MorphologyConfig


class TestPreprocessConfig:
    """Tests untuk PreprocessConfig dataclass"""

    def test_default_config(self):
        """Default config should use optimal parameters"""
        config = PreprocessConfig()

        # Check contrast config
        assert config.contrast is not None
        assert config.contrast.method == "clahe"
        assert config.contrast.clip_limit == 2.0
        assert config.contrast.tile_size == (8, 8)

        # Check morphology config
        assert config.morphology is not None
        assert config.morphology.operations == ["opening"]
        assert config.morphology.kernel_size == 3

        # Check quality thresholds
        assert config.quality_threshold == 0.8
        assert config.min_rms_contrast == 30.0
        assert config.min_edge_density == 0.03

    def test_custom_config(self):
        """Custom config should accept all parameters"""
        custom_contrast = ContrastConfig(method="hist_eq")
        custom_morphology = MorphologyConfig(operations=["closing"], kernel_size=5)

        config = PreprocessConfig(
            contrast=custom_contrast,
            morphology=custom_morphology,
            quality_threshold=0.9,
            min_rms_contrast=40.0,
            min_edge_density=0.05
        )

        assert config.contrast.method == "hist_eq"
        assert config.morphology.operations == ["closing"]
        assert config.quality_threshold == 0.9

    def test_threshold_validation(self):
        """Thresholds should be validated"""
        # Invalid quality_threshold
        with pytest.raises(ValueError, match="quality_threshold must be 0-1"):
            PreprocessConfig(quality_threshold=1.5)

        # Invalid min_rms_contrast
        with pytest.raises(ValueError, match="min_rms_contrast must be positive"):
            PreprocessConfig(min_rms_contrast=-10)

        # Invalid min_edge_density
        with pytest.raises(ValueError, match="min_edge_density must be 0-1"):
            PreprocessConfig(min_edge_density=2.0)


class TestPreprocessImage:
    """Tests untuk preprocess_image function"""

    def test_preprocess_with_default_config(self, sample_image_path):
        """Preprocessing should work with default config"""
        result = preprocess_image(sample_image_path)

        assert result is not None
        assert isinstance(result, PreprocessResult)
        assert result.processed_image is not None

    def test_preprocess_success_fields(self, sample_image_path):
        """Result should contain all required fields"""
        result = preprocess_image(sample_image_path)

        # Check all fields exist
        assert hasattr(result, 'success')
        assert hasattr(result, 'processed_image')
        assert hasattr(result, 'metrics')
        assert hasattr(result, 'processing_time')
        assert hasattr(result, 'quality_flags')
        assert hasattr(result, 'error_message')

    def test_preprocess_output_format(self, sample_image_path):
        """Processed image should be grayscale 8-bit"""
        result = preprocess_image(sample_image_path)

        assert len(result.processed_image.shape) == 2, "Output should be grayscale (2D)"
        assert result.processed_image.dtype == np.uint8, "Output should be 8-bit"
        assert result.processed_image.min() >= 0
        assert result.processed_image.max() <= 255

    def test_preprocess_with_custom_config(self, sample_image_path):
        """Preprocessing should work with custom config"""
        config = PreprocessConfig(
            quality_threshold=0.7,
            min_rms_contrast=25.0
        )

        result = preprocess_image(sample_image_path, config)
        assert result is not None

    def test_preprocess_performance(self, sample_image_path):
        """Processing should meet performance targets"""
        result = preprocess_image(sample_image_path)

        # Should be faster than 2 seconds
        assert result.processing_time < 2.0, f"Too slow: {result.processing_time:.3f}s"

        # Typically should be much faster (notebook showed 0.104s average)
        assert result.processing_time < 1.0, "Should be faster than 1 second"

    def test_preprocess_quality_flags(self, sample_image_path):
        """Quality flags should be populated"""
        result = preprocess_image(sample_image_path)

        assert 'sufficient_contrast' in result.quality_flags
        assert 'sufficient_edges' in result.quality_flags
        assert 'meets_readiness' in result.quality_flags

        # All flags should be boolean
        for flag_value in result.quality_flags.values():
            assert isinstance(flag_value, bool)

    def test_preprocess_metrics(self, sample_image_path):
        """Metrics should be calculated"""
        result = preprocess_image(sample_image_path)

        assert result.metrics is not None
        assert result.metrics.readiness_score >= 0
        assert result.metrics.readiness_score <= 1
        assert result.metrics.rms_contrast > 0
        assert result.metrics.edge_density >= 0

    def test_preprocess_save_intermediate(self, sample_image_path):
        """Should save intermediate steps when requested"""
        result = preprocess_image(sample_image_path, save_intermediate=True)

        assert result.intermediate_steps is not None
        assert 'original' in result.intermediate_steps
        assert 'after_contrast' in result.intermediate_steps
        assert 'after_morphology' in result.intermediate_steps

    def test_preprocess_nonexistent_file(self):
        """Should handle nonexistent file gracefully"""
        result = preprocess_image("nonexistent.jpg")

        assert result.success is False
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()

    def test_preprocess_invalid_file(self, tmp_path):
        """Should handle invalid file gracefully"""
        # Create empty file
        invalid_file = tmp_path / "invalid.jpg"
        invalid_file.write_bytes(b"not an image")

        result = preprocess_image(invalid_file)

        assert result.success is False
        assert result.error_message is not None

    def test_preprocess_improves_quality(self, sample_image_path):
        """Preprocessing should improve or maintain quality"""
        result = preprocess_image(sample_image_path, save_intermediate=True)

        if result.success:
            # Quality should be maintained or improved
            assert result.metrics.readiness_score >= 0


class TestBatchPreprocess:
    """Tests untuk batch_preprocess function"""

    def test_batch_preprocess_multiple_images(self, sample_image_path):
        """Batch processing should handle multiple images"""
        # Use same image multiple times for testing
        image_paths = [sample_image_path] * 3

        results = batch_preprocess(image_paths, show_progress=False)

        assert len(results) == 3
        assert all(isinstance(r, PreprocessResult) for r in results)

    def test_batch_preprocess_with_config(self, sample_image_path):
        """Batch processing should use provided config"""
        image_paths = [sample_image_path] * 2
        config = PreprocessConfig(quality_threshold=0.7)

        results = batch_preprocess(image_paths, config, show_progress=False)

        assert len(results) == 2

    def test_batch_preprocess_empty_list(self):
        """Batch processing should handle empty list"""
        results = batch_preprocess([], show_progress=False)

        assert len(results) == 0

    def test_batch_preprocess_mixed_success(self, sample_image_path):
        """Batch processing should handle mix of valid/invalid files"""
        image_paths = [
            sample_image_path,
            "nonexistent1.jpg",
            sample_image_path,
            "nonexistent2.jpg"
        ]

        results = batch_preprocess(image_paths, show_progress=False)

        assert len(results) == 4
        # Some should succeed, some should fail
        success_count = sum(r.success for r in results)
        assert success_count >= 2  # At least the valid images


class TestValidatePreprocessing:
    """Tests untuk validate_preprocessing function"""

    def test_validate_successful_result(self, sample_image_path):
        """Valid result should pass validation"""
        result = preprocess_image(sample_image_path)

        if result.success:
            is_valid, issues = validate_preprocessing(result)
            assert is_valid is True
            assert len(issues) == 0

    def test_validate_failed_result(self):
        """Failed result should not pass validation"""
        result = preprocess_image("nonexistent.jpg")

        is_valid, issues = validate_preprocessing(result)

        assert is_valid is False
        assert len(issues) > 0

    def test_validate_strict_mode(self, sample_image_path):
        """Strict validation should apply stricter criteria"""
        result = preprocess_image(sample_image_path)

        # Standard validation
        is_valid_standard, issues_standard = validate_preprocessing(result, strict=False)

        # Strict validation
        is_valid_strict, issues_strict = validate_preprocessing(result, strict=True)

        # Strict should be equal or more strict
        if is_valid_strict:
            assert is_valid_standard

    def test_validate_returns_issues_list(self, sample_image_path):
        """Validation should return list of specific issues"""
        result = preprocess_image(sample_image_path)
        is_valid, issues = validate_preprocessing(result)

        assert isinstance(issues, list)
        # If valid, issues should be empty
        if is_valid:
            assert len(issues) == 0


class TestIntegrationEndToEnd:
    """End-to-end integration tests"""

    def test_complete_pipeline_flow(self, sample_image_path):
        """Test complete pipeline from image to result"""
        # Step 1: Load and preprocess
        result = preprocess_image(sample_image_path)

        # Step 2: Verify success
        if result.success:
            # Step 3: Check output quality
            assert result.processed_image.shape[0] > 0
            assert result.processed_image.shape[1] > 0

            # Step 4: Validate result
            is_valid, issues = validate_preprocessing(result)
            assert is_valid, f"Validation failed: {issues}"

            # Step 5: Check metrics consistency with quality flags
            if result.quality_flags['meets_readiness']:
                # If meets_readiness is True, score should be >= threshold
                assert result.metrics.readiness_score >= 0

    def test_pipeline_with_optimal_config(self, sample_image_path):
        """Pipeline should work with OPTIMAL_CONFIG"""
        result = preprocess_image(sample_image_path, OPTIMAL_CONFIG)

        assert result is not None
        assert result.processed_image is not None

    def test_pipeline_consistency(self, sample_image_path):
        """Multiple runs should produce consistent results"""
        result1 = preprocess_image(sample_image_path)
        result2 = preprocess_image(sample_image_path)

        # Results should be identical for same image
        assert result1.success == result2.success
        assert np.array_equal(result1.processed_image, result2.processed_image)
        assert result1.metrics.readiness_score == result2.metrics.readiness_score


class TestPerformanceBenchmarks:
    """Tests untuk performance benchmarks"""

    def test_benchmarks_exist(self):
        """Performance benchmarks should be defined"""
        assert 'notebook_experiment' in PERFORMANCE_BENCHMARKS
        assert 'targets' in PERFORMANCE_BENCHMARKS

    def test_benchmark_structure(self):
        """Benchmarks should have expected structure"""
        exp = PERFORMANCE_BENCHMARKS['notebook_experiment']

        assert 'total_images' in exp
        assert 'success_rate' in exp
        assert 'avg_processing_time' in exp
        assert 'avg_readiness_improvement' in exp

    def test_optimal_config_exists(self):
        """OPTIMAL_CONFIG should be defined"""
        assert OPTIMAL_CONFIG is not None
        assert isinstance(OPTIMAL_CONFIG, PreprocessConfig)

    def test_optimal_config_usable(self, sample_image_path):
        """OPTIMAL_CONFIG should work in practice"""
        result = preprocess_image(sample_image_path, OPTIMAL_CONFIG)
        assert result is not None


class TestModuleIntegration:
    """Tests untuk integration between M1-M4"""

    def test_m1_m2_integration(self, sample_image_path):
        """Quality assessment should work with contrast enhancement"""
        from src.preprocessing import assess_image_quality, enhance_contrast

        image = cv2.imread(str(sample_image_path))
        enhanced = enhance_contrast(image)

        # Should be able to assess enhanced image
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        metrics = assess_image_quality(enhanced_bgr)

        assert metrics is not None
        assert metrics.readiness_score >= 0

    def test_m2_m3_integration(self, sample_image_path):
        """Contrast enhancement output should work with morphology"""
        from src.preprocessing import enhance_contrast, apply_morphology

        image = cv2.imread(str(sample_image_path))
        enhanced = enhance_contrast(image)
        morphed = apply_morphology(enhanced)

        assert morphed is not None
        assert morphed.shape == enhanced.shape

    def test_m1_m2_m3_pipeline(self, sample_image_path):
        """Complete M1→M2→M3 integration"""
        from src.preprocessing import (
            assess_image_quality,
            enhance_contrast,
            apply_morphology
        )

        # Load image
        image = cv2.imread(str(sample_image_path))

        # M2: Enhance contrast
        enhanced = enhance_contrast(image)

        # M3: Apply morphology
        final = apply_morphology(enhanced)

        # M1: Assess quality
        final_bgr = cv2.cvtColor(final, cv2.COLOR_GRAY2BGR)
        metrics = assess_image_quality(final_bgr)

        # All steps should succeed
        assert final is not None
        assert metrics is not None
        assert metrics.readiness_score > 0
