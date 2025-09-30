"""
Grid Normalizer untuk Template Detection system
Perspective correction dan grid normalization untuk standardized cell extraction
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
import time

from ..config import SegmentationConfig
from ..utils.quality_assessment import QualityAssessment

logger = logging.getLogger(__name__)


@dataclass
class GridNormalizationResult:
    """Data structure untuk grid normalization results"""
    normalized_grid: Optional[np.ndarray]
    transformation_matrix: Optional[np.ndarray]
    corrected_coordinates: Optional[Tuple[int, int, int, int]]
    perspective_corrected: bool
    quality_score: float
    processing_time: float
    error_message: Optional[str] = None


class GridNormalizer:
    """Grid normalization dengan perspective correction dan geometric standardization"""

    def __init__(self, config: SegmentationConfig):
        """
        Initialize grid normalizer

        Args:
            config: Configuration untuk segmentation parameters
        """
        self.config = config
        self.quality_assessor = QualityAssessment()

    def normalize_grid(
        self,
        image: np.ndarray,
        grid_coordinates: Tuple[int, int, int, int],
        grid_corners: Optional[List[Tuple[int, int]]] = None,
        target_size: Optional[Tuple[int, int]] = None
    ) -> GridNormalizationResult:
        """
        Main method untuk normalizing detected grid

        Args:
            image: Original image
            grid_coordinates: Detected grid coordinates (x1, y1, x2, y2)
            grid_corners: Optional precise grid corners untuk perspective correction
            target_size: Optional target size untuk normalized grid

        Returns:
            GridNormalizationResult object
        """
        start_time = time.time()

        try:
            # 1. Extract grid region
            grid_region = self._extract_grid_region(image, grid_coordinates)

            if grid_region is None:
                return self._create_failed_result(
                    "Failed to extract grid region", time.time() - start_time
                )

            # 2. Detect atau refine corners
            refined_corners = self._detect_or_refine_corners(
                grid_region, grid_coordinates, grid_corners
            )

            # 3. Apply perspective correction if needed
            corrected_grid, transformation_matrix = self._apply_perspective_correction(
                image, grid_coordinates, refined_corners, target_size
            )

            # 4. Validate correction quality
            quality_score = self._assess_correction_quality(
                grid_region, corrected_grid, refined_corners
            )

            # 5. Calculate corrected coordinates
            corrected_coords = self._calculate_corrected_coordinates(
                grid_coordinates, transformation_matrix, corrected_grid.shape if corrected_grid is not None else None
            )

            processing_time = time.time() - start_time

            perspective_corrected = transformation_matrix is not None

            return GridNormalizationResult(
                normalized_grid=corrected_grid,
                transformation_matrix=transformation_matrix,
                corrected_coordinates=corrected_coords,
                perspective_corrected=perspective_corrected,
                quality_score=quality_score,
                processing_time=processing_time
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error dalam grid normalization: {str(e)}")

            return self._create_failed_result(str(e), processing_time)

    def _extract_grid_region(
        self,
        image: np.ndarray,
        grid_coordinates: Tuple[int, int, int, int]
    ) -> Optional[np.ndarray]:
        """Extract grid region dari original image"""

        x1, y1, x2, y2 = grid_coordinates

        # Validate coordinates
        h, w = image.shape[:2]
        if not (0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h):
            logger.warning(f"Invalid grid coordinates: {grid_coordinates}")
            return None

        # Extract region dengan optional padding
        padding = self.config.cell_padding
        padded_x1 = max(0, x1 - padding)
        padded_y1 = max(0, y1 - padding)
        padded_x2 = min(w, x2 + padding)
        padded_y2 = min(h, y2 + padding)

        grid_region = image[padded_y1:padded_y2, padded_x1:padded_x2]

        if grid_region.size == 0:
            logger.warning("Extracted grid region is empty")
            return None

        return grid_region

    def _detect_or_refine_corners(
        self,
        grid_region: np.ndarray,
        grid_coordinates: Tuple[int, int, int, int],
        provided_corners: Optional[List[Tuple[int, int]]] = None
    ) -> List[Tuple[int, int]]:
        """Detect atau refine grid corners untuk precise perspective correction"""

        if provided_corners and len(provided_corners) == 4:
            # Validate provided corners
            if self._validate_corners(provided_corners, grid_coordinates):
                return provided_corners

        # Detect corners menggunakan Harris corner detection
        detected_corners = self._detect_corners_harris(grid_region, grid_coordinates)

        if detected_corners and len(detected_corners) == 4:
            return detected_corners

        # Fallback: use bounding rectangle corners
        x1, y1, x2, y2 = grid_coordinates
        fallback_corners = [
            (x1, y1),  # Top-left
            (x2, y1),  # Top-right
            (x2, y2),  # Bottom-right
            (x1, y2)   # Bottom-left
        ]

        logger.debug("Using fallback rectangular corners")
        return fallback_corners

    def _validate_corners(
        self,
        corners: List[Tuple[int, int]],
        grid_coordinates: Tuple[int, int, int, int]
    ) -> bool:
        """Validate corner points"""

        if len(corners) != 4:
            return False

        x1, y1, x2, y2 = grid_coordinates

        # Check if all corners are within reasonable bounds
        for x, y in corners:
            if not (x1 - 20 <= x <= x2 + 20 and y1 - 20 <= y <= y2 + 20):
                return False

        # Check if corners form reasonable quadrilateral
        # Calculate area using shoelace formula
        x_coords = [corner[0] for corner in corners]
        y_coords = [corner[1] for corner in corners]

        area = 0.5 * abs(sum(x_coords[i] * y_coords[(i + 1) % 4] -
                            x_coords[(i + 1) % 4] * y_coords[i] for i in range(4)))

        expected_area = (x2 - x1) * (y2 - y1)
        area_ratio = area / expected_area if expected_area > 0 else 0

        return 0.5 <= area_ratio <= 1.5  # Reasonable area ratio

    def _detect_corners_harris(
        self,
        grid_region: np.ndarray,
        grid_coordinates: Tuple[int, int, int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """Detect corners menggunakan Harris corner detection"""

        # Convert to grayscale if needed
        if len(grid_region.shape) == 3:
            gray = cv2.cvtColor(grid_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = grid_region.copy()

        # Harris corner detection
        corners_response = cv2.cornerHarris(gray, 2, 3, 0.04)

        # Threshold untuk corner response
        threshold = 0.01 * corners_response.max()
        corner_points = np.where(corners_response > threshold)

        if len(corner_points[0]) < 4:
            return None

        # Convert to (x, y) coordinates
        corners = [(int(x), int(y)) for y, x in zip(corner_points[0], corner_points[1])]

        # Filter dan select best 4 corners
        filtered_corners = self._select_best_corners(corners, grid_region.shape)

        if len(filtered_corners) == 4:
            # Convert back to image coordinates
            x1, y1, _, _ = grid_coordinates
            padding = self.config.cell_padding
            adjusted_x1 = max(0, x1 - padding)
            adjusted_y1 = max(0, y1 - padding)

            image_corners = [
                (x + adjusted_x1, y + adjusted_y1) for x, y in filtered_corners
            ]

            return image_corners

        return None

    def _select_best_corners(
        self,
        corner_candidates: List[Tuple[int, int]],
        region_shape: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Select best 4 corners yang form rectangular grid"""

        if len(corner_candidates) <= 4:
            return corner_candidates

        h, w = region_shape[:2]

        # Divide region into quadrants dan select best corner dari each
        quadrant_corners = [[], [], [], []]  # TL, TR, BR, BL

        for x, y in corner_candidates:
            if x < w // 2 and y < h // 2:
                quadrant_corners[0].append((x, y))  # Top-left
            elif x >= w // 2 and y < h // 2:
                quadrant_corners[1].append((x, y))  # Top-right
            elif x >= w // 2 and y >= h // 2:
                quadrant_corners[2].append((x, y))  # Bottom-right
            else:
                quadrant_corners[3].append((x, y))  # Bottom-left

        selected_corners = []

        # Select corner closest to expected position dari each quadrant
        expected_positions = [
            (0, 0),        # Top-left
            (w - 1, 0),    # Top-right
            (w - 1, h - 1), # Bottom-right
            (0, h - 1)     # Bottom-left
        ]

        for quadrant_idx, (exp_x, exp_y) in enumerate(expected_positions):
            if quadrant_corners[quadrant_idx]:
                # Find closest corner to expected position
                best_corner = min(
                    quadrant_corners[quadrant_idx],
                    key=lambda corner: (corner[0] - exp_x)**2 + (corner[1] - exp_y)**2
                )
                selected_corners.append(best_corner)

        return selected_corners if len(selected_corners) == 4 else corner_candidates[:4]

    def _apply_perspective_correction(
        self,
        image: np.ndarray,
        grid_coordinates: Tuple[int, int, int, int],
        corners: List[Tuple[int, int]],
        target_size: Optional[Tuple[int, int]] = None
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Apply perspective correction jika diperlukan"""

        if not self.config.perspective_correction_enabled:
            # Just extract rectangular region
            x1, y1, x2, y2 = grid_coordinates
            extracted = image[y1:y2, x1:x2]
            return extracted, None

        if len(corners) != 4:
            logger.warning("Cannot apply perspective correction: need exactly 4 corners")
            x1, y1, x2, y2 = grid_coordinates
            extracted = image[y1:y2, x1:x2]
            return extracted, None

        # Check if perspective correction is actually needed
        if self._is_grid_already_rectangular(corners):
            logger.debug("Grid already rectangular, skipping perspective correction")
            x1, y1, x2, y2 = grid_coordinates
            extracted = image[y1:y2, x1:x2]
            return extracted, None

        try:
            # Order corners: top-left, top-right, bottom-right, bottom-left
            ordered_corners = self._order_corners(corners)

            # Calculate target dimensions
            if target_size:
                target_w, target_h = target_size
            else:
                target_w, target_h = self._calculate_target_dimensions(ordered_corners)

            # Define source dan destination points
            src_points = np.float32(ordered_corners)
            dst_points = np.float32([
                [0, 0],                    # Top-left
                [target_w - 1, 0],         # Top-right
                [target_w - 1, target_h - 1], # Bottom-right
                [0, target_h - 1]          # Bottom-left
            ])

            # Get perspective transformation matrix
            transform_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

            # Apply transformation
            corrected = cv2.warpPerspective(
                image,
                transform_matrix,
                (target_w, target_h),
                flags=getattr(cv2, self.config.interpolation_method, cv2.INTER_LINEAR)
            )

            logger.debug(f"Applied perspective correction: {image.shape} -> {corrected.shape}")
            return corrected, transform_matrix

        except Exception as e:
            logger.error(f"Error dalam perspective correction: {str(e)}")
            # Fallback to rectangular extraction
            x1, y1, x2, y2 = grid_coordinates
            extracted = image[y1:y2, x1:x2]
            return extracted, None

    def _is_grid_already_rectangular(self, corners: List[Tuple[int, int]]) -> bool:
        """Check if grid corners already form reasonable rectangle"""

        if len(corners) != 4:
            return False

        # Order corners
        ordered = self._order_corners(corners)

        # Calculate angles at each corner
        angles = []
        for i in range(4):
            p1 = np.array(ordered[i])
            p2 = np.array(ordered[(i + 1) % 4])
            p3 = np.array(ordered[(i + 2) % 4])

            v1 = p1 - p2
            v2 = p3 - p2

            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle) * 180 / np.pi

            angles.append(angle)

        # Check if all angles are close to 90 degrees
        angle_deviations = [abs(angle - 90) for angle in angles]
        avg_deviation = np.mean(angle_deviations)

        return avg_deviation <= 15  # Within 15 degrees tolerance

    def _order_corners(self, corners: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Order corners dalam clockwise order starting dari top-left"""

        if len(corners) != 4:
            return corners

        # Convert to numpy array
        points = np.array(corners)

        # Find centroid
        centroid = np.mean(points, axis=0)

        # Calculate angles dari centroid
        angles = []
        for point in points:
            angle = np.arctan2(point[1] - centroid[1], point[0] - centroid[0])
            angles.append(angle)

        # Sort by angle
        sorted_indices = np.argsort(angles)

        # Identify top-left corner (smallest x + y)
        sums = [corners[i][0] + corners[i][1] for i in sorted_indices]
        top_left_idx = sorted_indices[np.argmin(sums)]

        # Reorder starting dari top-left
        start_pos = list(sorted_indices).index(top_left_idx)
        ordered_indices = sorted_indices[start_pos:] + sorted_indices[:start_pos]

        ordered_corners = [corners[i] for i in ordered_indices]

        return ordered_corners

    def _calculate_target_dimensions(self, ordered_corners: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Calculate optimal target dimensions untuk perspective correction"""

        if len(ordered_corners) != 4:
            return (400, 300)  # Default fallback

        # Calculate distances between opposite corners
        top_width = np.linalg.norm(np.array(ordered_corners[1]) - np.array(ordered_corners[0]))
        bottom_width = np.linalg.norm(np.array(ordered_corners[2]) - np.array(ordered_corners[3]))
        left_height = np.linalg.norm(np.array(ordered_corners[3]) - np.array(ordered_corners[0]))
        right_height = np.linalg.norm(np.array(ordered_corners[2]) - np.array(ordered_corners[1]))

        # Use maximum dimensions untuk preserve detail
        target_w = int(max(top_width, bottom_width))
        target_h = int(max(left_height, right_height))

        # Ensure reasonable dimensions
        target_w = max(100, min(target_w, 2000))
        target_h = max(100, min(target_h, 2000))

        return (target_w, target_h)

    def _assess_correction_quality(
        self,
        original_grid: np.ndarray,
        corrected_grid: Optional[np.ndarray],
        corners: List[Tuple[int, int]]
    ) -> float:
        """Assess quality perspective correction"""

        if corrected_grid is None:
            return 0.5  # Neutral score untuk no correction

        quality_factors = []

        # 1. Size preservation
        orig_area = original_grid.shape[0] * original_grid.shape[1]
        corrected_area = corrected_grid.shape[0] * corrected_grid.shape[1]

        if orig_area > 0:
            area_ratio = corrected_area / orig_area
            area_score = 1.0 - abs(area_ratio - 1.0)  # Prefer area preservation
            quality_factors.append(max(0.0, area_score))

        # 2. Corner geometry quality
        if len(corners) == 4:
            rectangularity_score = 1.0 - self._calculate_corner_deviation(corners) / 45.0
            quality_factors.append(max(0.0, rectangularity_score))

        # 3. Content preservation (using image variance)
        if len(original_grid.shape) == 3:
            orig_gray = cv2.cvtColor(original_grid, cv2.COLOR_BGR2GRAY)
        else:
            orig_gray = original_grid

        if len(corrected_grid.shape) == 3:
            corr_gray = cv2.cvtColor(corrected_grid, cv2.COLOR_BGR2GRAY)
        else:
            corr_gray = corrected_grid

        orig_variance = np.var(orig_gray)
        corr_variance = np.var(corr_gray)

        if orig_variance > 0:
            variance_ratio = corr_variance / orig_variance
            variance_score = 1.0 - abs(variance_ratio - 1.0)
            quality_factors.append(max(0.0, variance_score))

        return np.mean(quality_factors) if quality_factors else 0.5

    def _calculate_corner_deviation(self, corners: List[Tuple[int, int]]) -> float:
        """Calculate average deviation dari 90-degree angles"""

        if len(corners) != 4:
            return 45.0  # Maximum deviation

        ordered = self._order_corners(corners)

        deviations = []
        for i in range(4):
            p1 = np.array(ordered[i])
            p2 = np.array(ordered[(i + 1) % 4])
            p3 = np.array(ordered[(i + 2) % 4])

            v1 = p1 - p2
            v2 = p3 - p2

            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle) * 180 / np.pi

            deviation = abs(angle - 90)
            deviations.append(deviation)

        return np.mean(deviations)

    def _calculate_corrected_coordinates(
        self,
        original_coordinates: Tuple[int, int, int, int],
        transformation_matrix: Optional[np.ndarray],
        corrected_shape: Optional[Tuple[int, int]]
    ) -> Optional[Tuple[int, int, int, int]]:
        """Calculate coordinates dalam corrected image space"""

        if transformation_matrix is None:
            return original_coordinates

        if corrected_shape is None:
            return None

        h, w = corrected_shape[:2]
        return (0, 0, w, h)

    def _create_failed_result(self, error_message: str, processing_time: float) -> GridNormalizationResult:
        """Create failed normalization result"""

        return GridNormalizationResult(
            normalized_grid=None,
            transformation_matrix=None,
            corrected_coordinates=None,
            perspective_corrected=False,
            quality_score=0.0,
            processing_time=processing_time,
            error_message=error_message
        )