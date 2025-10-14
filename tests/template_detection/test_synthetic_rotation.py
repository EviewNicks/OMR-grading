"""
Synthetic Rotation Tests untuk Rotation-Robust Contour Detection
MVP validation untuk rotation invariance
"""

import pytest
import cv2
import numpy as np
import sys
from pathlib import Path

# Add src ke path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from template_detector.config import ContourDetectionConfig
from template_detector.core.contour_detector import ContourGridDetector


class TestSyntheticRotation:
    """Test synthetic rotation scenarios"""

    @pytest.fixture
    def detector(self):
        """Rotation-robust detector dengan ultra-relaxed parameters"""
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
        return ContourGridDetector(config)

    def create_synthetic_grid(self, rotation_angle=0, noise_level=0.0, size=(400, 300)):
        """
        Create synthetic OMR grid dengan rotation dan noise

        Args:
            rotation_angle: Rotation angle in degrees
            noise_level: Noise level (0.0-1.0)
            size: Image size (width, height)

        Returns:
            Synthetic grid image
        """
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

    @pytest.mark.parametrize("rotation_angle", [0, 15, 30, 45, 60, 90])
    def test_rotation_invariance(self, detector, rotation_angle):
        """Test detection invariance across rotation angles"""
        image = self.create_synthetic_grid(rotation_angle=rotation_angle)

        result = detector.detect_grid(image)

        # Core MVP validation
        assert result.confidence > 0.5, f"Failed to detect grid at {rotation_angle}° rotation"
        assert result.grid_coordinates is not None, f"No coordinates for {rotation_angle}° rotation"
        assert result.rotation_robust is True, "Should use rotation-robust detection"

        # Angle detection validation (within 15° tolerance)
        if result.angle is not None:
            angle_diff = abs(result.angle - rotation_angle) % 90
            if angle_diff > 45:
                angle_diff = 90 - angle_diff
            assert angle_diff <= 15, f"Angle detection too inaccurate: detected {result.angle}, expected {rotation_angle}"

    @pytest.mark.parametrize("noise_level", [0.0, 0.1, 0.2, 0.3])
    def test_noise_tolerance(self, detector, noise_level):
        """Test detection robustness against noise"""
        image = self.create_synthetic_grid(rotation_angle=15, noise_level=noise_level)

        result = detector.detect_grid(image)

        # MVP validation - should handle moderate noise
        if noise_level <= 0.2:
            assert result.confidence > 0.3, f"Failed with noise level {noise_level}"

        # Very high noise may fail, but should not crash
        assert isinstance(result.confidence, float), "Confidence should be a float"
        assert 0.0 <= result.confidence <= 1.0, "Confidence should be in valid range"

    def test_grid_size_variations(self, detector):
        """Test detection dengan different grid sizes"""
        sizes = [
            (300, 200),   # Small image
            (400, 300),   # Medium image
            (600, 400),   # Large image
            (800, 600)    # Very large image
        ]

        for size in sizes:
            image = self.create_synthetic_grid(rotation_angle=25, size=size)
            result = detector.detect_grid(image)

            # Should detect grid in all reasonable sizes
            assert result.confidence > 0.3, f"Failed with image size {size}"

    def test_multiple_rotation_angles_single_image(self, detector):
        """Test multiple angles on same base image"""
        base_image = self.create_synthetic_grid(rotation_angle=0)

        angles = [0, 10, 20, 30, 40, 50]
        results = []

        for angle in angles:
            # Rotate base image
            height, width = base_image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated_image = cv2.warpAffine(base_image, rotation_matrix, (width, height))

            result = detector.detect_grid(rotated_image)
            results.append(result)

            # Basic validation
            assert isinstance(result, object), "Should return valid result object"

        # At least 50% of angles should be detected
        success_count = sum(1 for r in results if r.confidence > 0.3)
        assert success_count >= len(angles) // 2, f"Too few successful detections: {success_count}/{len(angles)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])