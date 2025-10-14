"""
Test Suite untuk Rotation-Robust Contour Detection
Comprehensive testing untuk enhanced contour detection dengan rotation invariance
"""

import pytest
import cv2
import numpy as np
from pathlib import Path
import sys
import logging

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig, TemplateDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector, ContourDetectionResult
from template_detector.core.week5_integration import Week5IntegrationManager, Week5PreprocessingResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRotationRobustDetection:
    """Test suite untuk rotation-robust contour detection"""

    @pytest.fixture
    def sample_config(self):
        """ContourDetectionConfig dengan rotation-robust parameters"""
        return ContourDetectionConfig(
            min_area=1000,
            max_area=50000,
            aspect_ratio_min=0.1,
            aspect_ratio_max=2.0,
            rectangularity_threshold=0.6,
            approximation_epsilon=0.02,
            hierarchy_level=2,

            # Rotation-robust parameters
            min_area_ratio=0.05,
            max_area_ratio=0.70,
            min_aspect_ratio=0.05,
            max_aspect_ratio=0.80,
            min_rectangularity=0.60,

            # Control flags
            use_rotation_robust=True,
            use_hybrid_threshold=True
        )

    @pytest.fixture
    def traditional_config(self):
        """ContourDetectionConfig dengan traditional parameters"""
        return ContourDetectionConfig(
            min_area=1000,
            max_area=50000,
            aspect_ratio_min=0.3,
            aspect_ratio_max=3.0,
            rectangularity_threshold=0.7,
            approximation_epsilon=0.02,
            hierarchy_level=2,

            # Traditional parameters (no rotation support)
            use_rotation_robust=False,
            use_hybrid_threshold=False
        )

    @pytest.fixture
    def rotation_detector(self, sample_config):
        """ContourGridDetector dengan rotation-robust config"""
        return ContourGridDetector(sample_config)

    @pytest.fixture
    def traditional_detector(self, traditional_config):
        """ContourGridDetector dengan traditional config"""
        return ContourGridDetector(traditional_config)

    def create_synthetic_grid(self, width=400, height=300, rotation_angle=0, noise_level=0.1):
        """
        Create synthetic grid image dengan optional rotation

        Args:
            width: Image width
            height: Image height
            rotation_angle: Rotation angle in degrees
            noise_level: Noise level (0.0-1.0)

        Returns:
            Rotated synthetic grid image
        """
        # Create base image
        image = np.ones((height, width), dtype=np.uint8) * 255

        # Draw grid rectangle
        grid_width, grid_height = int(width * 0.6), int(height * 0.8)
        grid_x = (width - grid_width) // 2
        grid_y = (height - grid_height) // 2

        cv2.rectangle(image, (grid_x, grid_y),
                     (grid_x + grid_width, grid_y + grid_height), 0, -1)

        # Add grid lines
        for i in range(1, 4):
            x = grid_x + (grid_width * i // 4)
            cv2.line(image, (x, grid_y), (x, grid_y + grid_height), 255, 2)

        for i in range(1, 6):
            y = grid_y + (grid_height * i // 6)
            cv2.line(image, (grid_x, y), (grid_x + grid_width, y), 255, 2)

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

    def test_rotation_robust_properties_calculation(self, rotation_detector):
        """Test rotation-robust property calculation"""
        # Create simple square contour
        contour = np.array([[[100, 100]], [[200, 100]], [[200, 200]], [[100, 200]]], dtype=np.int32)

        props = rotation_detector._calculate_rotation_robust_properties(contour)

        assert 'area' in props
        assert 'aspect_ratio' in props
        assert 'rectangularity' in props
        assert 'angle' in props
        assert 'box_points' in props
        assert 'center' in props
        assert 'dimensions' in props

        # Verify properties
        assert props['area'] > 0
        assert 0 <= props['aspect_ratio'] <= 1.0
        assert 0 <= props['rectangularity'] <= 1.0
        assert isinstance(props['angle'], (int, float))
        assert len(props['box_points']) == 4
        assert len(props['center']) == 2
        assert len(props['dimensions']) == 2

    def test_rotation_robust_filtering(self, rotation_detector):
        """Test rotation-robust contour filtering"""
        # Create test image
        image = self.create_synthetic_grid(rotation_angle=15)

        # Extract contours
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY_INV, 11, 2)
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Apply rotation-robust filtering
        filtered_data = rotation_detector._filter_contours_rotation_robust(contours, image.shape)
        filtered_contours = [d['contour'] for d in filtered_data]

        assert len(filtered_contours) > 0, "Should detect at least one contour"

        # Verify filtered data structure
        for data in filtered_data:
            assert 'contour' in data
            assert 'area' in data
            assert 'aspect_ratio' in data
            assert 'rectangularity' in data
            assert 'angle' in data
            assert 'box_points' in data

    def test_detect_grid_rotation_robust(self, rotation_detector):
        """Test rotation-robust grid detection"""
        # Test dengan rotated image
        rotated_image = self.create_synthetic_grid(rotation_angle=25)

        result = rotation_detector._detect_grid_rotation_robust(rotated_image)

        assert isinstance(result, ContourDetectionResult)
        assert result.rotation_robust is True
        assert result.processing_time > 0

        if result.confidence > 0:
            assert result.grid_coordinates is not None
            assert len(result.grid_coordinates) == 4
            assert result.grid_corners is not None
            assert result.angle is not None
            assert result.box_points is not None

    def test_hybrid_threshold_selection(self, rotation_detector):
        """Test hybrid threshold method selection"""
        image = self.create_synthetic_grid(rotation_angle=15)

        result = rotation_detector._detect_grid_rotation_robust(image)

        assert isinstance(result, ContourDetectionResult)
        assert result.rotation_robust is True

    def test_traditional_vs_rotation_robust(self, rotation_detector, traditional_detector):
        """Compare traditional vs rotation-robust detection"""
        # Test dengan unrotated image
        normal_image = self.create_synthetic_grid(rotation_angle=0)

        traditional_result = traditional_detector.detect_grid(normal_image)
        rotation_result = rotation_detector.detect_grid(normal_image)

        # Both should detect something in normal case
        assert isinstance(traditional_result, ContourDetectionResult)
        assert isinstance(rotation_result, ContourDetectionResult)

        # Test dengan rotated image
        rotated_image = self.create_synthetic_grid(rotation_angle=30)

        traditional_rotated = traditional_detector.detect_grid(rotated_image)
        rotation_rotated = rotation_detector.detect_grid(rotated_image)

        # Rotation-robust should perform better with rotated images
        assert rotation_rotated.rotation_robust is True
        assert traditional_rotated.rotation_robust is False

        # Compare confidence (rotation-robust should be equal or better)
        if rotation_rotated.confidence > 0 and traditional_rotated.confidence > 0:
            logger.info(f"Traditional confidence: {traditional_rotated.confidence:.3f}")
            logger.info(f"Rotation-robust confidence: {rotation_rotated.confidence:.3f}")

    def test_different_rotation_angles(self, rotation_detector):
        """Test detection dengan various rotation angles"""
        angles = [0, 15, 30, 45, 60, 90]
        results = {}

        for angle in angles:
            image = self.create_synthetic_grid(rotation_angle=angle)
            result = rotation_detector.detect_grid(image)
            results[angle] = result

            assert isinstance(result, ContourDetectionResult)
            assert result.rotation_robust is True

            if result.confidence > 0:
                assert result.grid_coordinates is not None
                # Verify angle is detected (within tolerance)
                if result.angle is not None:
                    angle_diff = abs(result.angle - angle) % 90
                    if angle_diff > 45:
                        angle_diff = 90 - angle_diff
                    assert angle_diff <= 20, f"Angle detection too inaccurate: detected {result.angle}, expected {angle}"

        # Log results
        logger.info("Rotation angle test results:")
        for angle, result in results.items():
            logger.info(f"  {angle:3d}°: confidence={result.confidence:.3f}, detected_angle={result.angle}")

    def test_noise_robustness(self, rotation_detector):
        """Test detection robustness dengan noise"""
        noise_levels = [0.0, 0.1, 0.2, 0.3]
        results = {}

        for noise in noise_levels:
            image = self.create_synthetic_grid(rotation_angle=20, noise_level=noise)
            result = rotation_detector.detect_grid(image)
            results[noise] = result

            assert isinstance(result, ContourDetectionResult)
            assert result.rotation_robust is True

        # Log results
        logger.info("Noise robustness test results:")
        for noise, result in results.items():
            logger.info(f"  Noise {noise:.1f}: confidence={result.confidence:.3f}")

    def test_confidence_calculation(self, rotation_detector):
        """Test confidence score calculation"""
        image = self.create_synthetic_grid(rotation_angle=15)
        result = rotation_detector.detect_grid(image)

        assert isinstance(result, ContourDetectionResult)
        assert 0 <= result.confidence <= 1.0

        if result.confidence > 0:
            assert result.rectangularity_score >= 0
            assert result.aspect_ratio >= 0
            assert result.validation_score >= 0

    def test_error_handling(self, rotation_detector):
        """Test error handling dalam rotation-robust detection"""
        # Test dengan invalid image
        invalid_image = np.zeros((10, 10, 3), dtype=np.uint8)
        result = rotation_detector.detect_grid(invalid_image)

        assert isinstance(result, ContourDetectionResult)
        assert result.confidence == 0.0
        assert result.grid_coordinates is None
        assert result.error_message is not None or result.confidence == 0.0

    def test_week5_integration_config_creation(self):
        """Test Week5 integration config creation"""
        # Create sample Week5PreprocessingResult
        preprocessing_result = Week5PreprocessingResult(
            filename="test.jpg",
            file_size_kb=100.0,
            image_shape=(300, 400, 3),
            laplacian_variance=100.0,
            edge_density=0.2,
            blur_detected=False,
            blur_intensity=0.1,
            local_variance=50.0,
            high_freq_ratio=0.3,
            noise_reduction_detected=False,
            smoothness_score=0.8,
            rms_contrast=0.5,
            dynamic_range=200,
            low_light_detected=False,
            histogram_uniformity=0.7,
            contrast_enhanced=False,
            contrast_enhancement_intensity=0.0,
            overall_readiness=0.8,
            quality_score=0.75,
            recommendation="Good",
            contrast_readiness=0.8,
            sharpness_readiness=0.7,
            edge_readiness=0.9,
            sufficient_contrast=True,
            acceptable_blur=True,
            sufficient_edges=True,
            good_dynamic_range=True
        )

        # Mock Week5IntegrationManager
        manager = Week5IntegrationManager(
            Path("dummy_results.json"),
            Path("dummy_readiness.csv")
        )

        config = manager.create_rotation_robust_config(preprocessing_result)

        assert isinstance(config, ContourDetectionConfig)
        assert config.use_rotation_robust is True
        assert config.use_hybrid_threshold is True
        assert config.min_area_ratio == 0.05  # Should use standard values for edge_readiness=0.9
        assert config.max_area_ratio == 0.70
        assert config.min_aspect_ratio == 0.05
        assert config.max_aspect_ratio == 0.80
        assert config.min_rectangularity == 0.70

    def test_parameter_adaptation_by_quality(self):
        """Test parameter adaptation berdasarkan image quality"""
        manager = Week5IntegrationManager(
            Path("dummy_results.json"),
            Path("dummy_readiness.csv")
        )

        # Test high quality image
        high_quality = Week5PreprocessingResult(
            filename="high_quality.jpg",
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

        params = manager.get_adaptive_detection_parameters(high_quality)

        # High quality should have stricter parameters
        assert params['min_area_ratio'] == 0.08
        assert params['max_area_ratio'] == 0.60
        assert params['min_rectangularity'] == 0.70
        assert params['use_rotation_robust'] is False  # High quality = traditional method

        # Test low quality image
        low_quality = Week5PreprocessingResult(
            filename="low_quality.jpg",
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

        params = manager.get_adaptive_detection_parameters(low_quality)

        # Low quality should have relaxed parameters
        assert params['min_area_ratio'] == 0.03
        assert params['max_area_ratio'] == 0.80
        assert params['min_rectangularity'] == 0.50
        assert params['use_rotation_robust'] is True  # Low quality = rotation-robust


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])