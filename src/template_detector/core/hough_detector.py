"""
Hough Transform Line Detection untuk Template Detection system
Line detection dengan grid reconstruction untuk robust template detection
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
import time
from itertools import combinations

from ..config import HoughTransformConfig
from ..utils.quality_assessment import QualityAssessment

logger = logging.getLogger(__name__)


@dataclass
class HoughDetectionResult:
    """Data structure untuk Hough transform detection results"""
    grid_coordinates: Optional[Tuple[int, int, int, int]]
    confidence: float
    detected_lines: List[Tuple[float, float]]  # (rho, theta) pairs
    grid_corners: Optional[List[Tuple[int, int]]]
    line_intersections: List[Tuple[int, int]]
    horizontal_lines: List[Tuple[float, float]]
    vertical_lines: List[Tuple[float, float]]
    processing_time: float
    method: str = "hough"
    validation_score: float = 0.0
    error_message: Optional[str] = None


class HoughLineDetector:
    """Hough Transform line detection dengan grid reconstruction capability"""

    def __init__(self, config: HoughTransformConfig):
        """
        Initialize Hough line detector

        Args:
            config: Configuration untuk Hough transform parameters
        """
        self.config = config
        self.quality_assessor = QualityAssessment()

    def detect_grid(
        self,
        image: np.ndarray,
        preprocessing_params: Optional[Dict] = None
    ) -> HoughDetectionResult:
        """
        Main method untuk detecting grid menggunakan Hough transform

        Args:
            image: Input image (grayscale atau color)
            preprocessing_params: Optional preprocessing parameters

        Returns:
            HoughDetectionResult object
        """
        start_time = time.time()

        try:
            # 1. Preprocessing untuk edge detection
            edges = self._preprocess_for_edges(image, preprocessing_params)

            # 2. Line Detection menggunakan Hough Transform
            detected_lines = self._detect_lines_hough(edges)

            # 3. Line Classification (horizontal vs vertical)
            horizontal_lines, vertical_lines = self._classify_lines(detected_lines)

            # 4. Line Filtering dan Clustering
            filtered_h_lines = self._filter_and_cluster_lines(horizontal_lines, 'horizontal')
            filtered_v_lines = self._filter_and_cluster_lines(vertical_lines, 'vertical')

            # 5. Grid Reconstruction dari line intersections
            intersections = self._find_line_intersections(filtered_h_lines, filtered_v_lines)

            # 6. Grid Boundary Detection
            grid_bounds = self._detect_grid_boundaries(intersections, image.shape)

            # 7. Grid Validation
            validated_grid = self._validate_grid_structure(
                grid_bounds, filtered_h_lines, filtered_v_lines, intersections, image.shape
            )

            # 8. Confidence Calculation
            confidence = self._calculate_confidence(
                validated_grid, filtered_h_lines, filtered_v_lines, intersections
            )

            processing_time = time.time() - start_time

            if validated_grid:
                # Extract corners dari grid boundaries
                corners = self._extract_grid_corners(validated_grid)

                return HoughDetectionResult(
                    grid_coordinates=validated_grid['coordinates'],
                    confidence=confidence,
                    detected_lines=detected_lines,
                    grid_corners=corners,
                    line_intersections=intersections,
                    horizontal_lines=filtered_h_lines,
                    vertical_lines=filtered_v_lines,
                    processing_time=processing_time,
                    validation_score=validated_grid.get('validation_score', 0.0)
                )
            else:
                return HoughDetectionResult(
                    grid_coordinates=None,
                    confidence=0.0,
                    detected_lines=detected_lines,
                    grid_corners=None,
                    line_intersections=intersections,
                    horizontal_lines=filtered_h_lines,
                    vertical_lines=filtered_v_lines,
                    processing_time=processing_time,
                    error_message="No valid grid structure detected"
                )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error dalam Hough detection: {str(e)}")

            return HoughDetectionResult(
                grid_coordinates=None,
                confidence=0.0,
                detected_lines=[],
                grid_corners=None,
                line_intersections=[],
                horizontal_lines=[],
                vertical_lines=[],
                processing_time=processing_time,
                error_message=str(e)
            )

    def _preprocess_for_edges(
        self,
        image: np.ndarray,
        preprocessing_params: Optional[Dict] = None
    ) -> np.ndarray:
        """Preprocess image untuk optimal edge detection"""

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Get preprocessing parameters
        if preprocessing_params:
            blur_kernel = preprocessing_params.get('blur_kernel', 5)
            low_threshold = preprocessing_params.get('canny_low', self.config.canny_low_threshold)
            high_threshold = preprocessing_params.get('canny_high', self.config.canny_high_threshold)
        else:
            blur_kernel = 5
            low_threshold = self.config.canny_low_threshold
            high_threshold = self.config.canny_high_threshold

        # Gaussian blur untuk noise reduction
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)

        # Canny edge detection
        edges = cv2.Canny(blurred, low_threshold, high_threshold)

        # Morphological operations untuk strengthen lines
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        return edges

    def _detect_lines_hough(self, edges: np.ndarray) -> List[Tuple[float, float]]:
        """Detect lines menggunakan Hough Transform"""

        lines = cv2.HoughLines(
            edges,
            self.config.rho_resolution,
            self.config.theta_resolution,
            self.config.threshold
        )

        detected_lines = []
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                detected_lines.append((rho, theta))

        logger.debug(f"Detected {len(detected_lines)} lines dengan Hough Transform")
        return detected_lines

    def _classify_lines(
        self,
        lines: List[Tuple[float, float]]
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """Classify lines ke horizontal dan vertical"""

        horizontal_lines = []
        vertical_lines = []

        for rho, theta in lines:
            # Convert theta ke degrees untuk easier classification
            theta_deg = theta * 180 / np.pi

            # Classify berdasarkan angle
            # Horizontal lines: theta around 0° atau 180°
            # Vertical lines: theta around 90°
            if abs(theta_deg) <= self.config.parallel_tolerance_angle or \
               abs(theta_deg - 180) <= self.config.parallel_tolerance_angle:
                horizontal_lines.append((rho, theta))
            elif abs(theta_deg - 90) <= self.config.parallel_tolerance_angle:
                vertical_lines.append((rho, theta))

        logger.debug(f"Classified: {len(horizontal_lines)} horizontal, {len(vertical_lines)} vertical lines")
        return horizontal_lines, vertical_lines

    def _filter_and_cluster_lines(
        self,
        lines: List[Tuple[float, float]],
        line_type: str
    ) -> List[Tuple[float, float]]:
        """Filter dan cluster similar lines untuk remove duplicates"""

        if not lines:
            return []

        # Sort lines by rho value
        sorted_lines = sorted(lines, key=lambda x: x[0])

        # Cluster similar lines
        clustered_lines = []
        current_cluster = [sorted_lines[0]]

        for i in range(1, len(sorted_lines)):
            rho, theta = sorted_lines[i]
            prev_rho, prev_theta = sorted_lines[i-1]

            # Check if line belongs to current cluster
            rho_diff = abs(rho - prev_rho)
            theta_diff = abs(theta - prev_theta)

            if rho_diff <= 20 and theta_diff <= 0.1:  # Clustering thresholds
                current_cluster.append((rho, theta))
            else:
                # Finalize current cluster dan start new one
                if current_cluster:
                    # Take average untuk cluster representative
                    avg_rho = np.mean([line[0] for line in current_cluster])
                    avg_theta = np.mean([line[1] for line in current_cluster])
                    clustered_lines.append((avg_rho, avg_theta))

                current_cluster = [(rho, theta)]

        # Don't forget last cluster
        if current_cluster:
            avg_rho = np.mean([line[0] for line in current_cluster])
            avg_theta = np.mean([line[1] for line in current_cluster])
            clustered_lines.append((avg_rho, avg_theta))

        logger.debug(f"Filtered {line_type} lines: {len(lines)} -> {len(clustered_lines)}")
        return clustered_lines

    def _find_line_intersections(
        self,
        horizontal_lines: List[Tuple[float, float]],
        vertical_lines: List[Tuple[float, float]]
    ) -> List[Tuple[int, int]]:
        """Find intersection points antara horizontal dan vertical lines"""

        intersections = []

        for h_rho, h_theta in horizontal_lines:
            for v_rho, v_theta in vertical_lines:
                # Calculate intersection point
                intersection = self._calculate_line_intersection(
                    (h_rho, h_theta), (v_rho, v_theta)
                )

                if intersection:
                    x, y = intersection
                    # Validate intersection point (reasonable coordinates)
                    if 0 <= x <= 5000 and 0 <= y <= 5000:  # Reasonable bounds
                        intersections.append((int(x), int(y)))

        logger.debug(f"Found {len(intersections)} line intersections")
        return intersections

    def _calculate_line_intersection(
        self,
        line1: Tuple[float, float],
        line2: Tuple[float, float]
    ) -> Optional[Tuple[float, float]]:
        """Calculate intersection point untuk two lines dalam polar form"""

        rho1, theta1 = line1
        rho2, theta2 = line2

        # Convert polar to cartesian form: ax + by = c
        a1, b1, c1 = np.cos(theta1), np.sin(theta1), rho1
        a2, b2, c2 = np.cos(theta2), np.sin(theta2), rho2

        # Solve system of equations
        determinant = a1 * b2 - a2 * b1

        if abs(determinant) < 1e-6:  # Lines are parallel
            return None

        x = (c1 * b2 - c2 * b1) / determinant
        y = (a1 * c2 - a2 * c1) / determinant

        return (x, y)

    def _detect_grid_boundaries(
        self,
        intersections: List[Tuple[int, int]],
        image_shape: Tuple[int, int]
    ) -> Optional[Dict]:
        """Detect grid boundaries dari intersection points"""

        if len(intersections) < 4:  # Need at least 4 corners
            return None

        intersections = np.array(intersections)

        # Find bounding box of intersections
        min_x = int(np.min(intersections[:, 0]))
        max_x = int(np.max(intersections[:, 0]))
        min_y = int(np.min(intersections[:, 1]))
        max_y = int(np.max(intersections[:, 1]))

        # Validate grid boundaries
        h, w = image_shape[:2]

        # Check if boundaries are within image
        if not (0 <= min_x < max_x <= w and 0 <= min_y < max_y <= h):
            return None

        # Check reasonable grid size
        grid_width = max_x - min_x
        grid_height = max_y - min_y
        grid_area = grid_width * grid_height
        image_area = w * h

        area_ratio = grid_area / image_area
        if not (0.05 <= area_ratio <= 0.8):  # Reasonable grid size
            return None

        # Check aspect ratio
        aspect_ratio = grid_width / grid_height if grid_height > 0 else 0
        if not (0.3 <= aspect_ratio <= 3.0):  # Reasonable aspect ratio
            return None

        return {
            'coordinates': (min_x, min_y, max_x, max_y),
            'width': grid_width,
            'height': grid_height,
            'area': grid_area,
            'aspect_ratio': aspect_ratio,
            'intersections_count': len(intersections)
        }

    def _validate_grid_structure(
        self,
        grid_bounds: Optional[Dict],
        horizontal_lines: List[Tuple[float, float]],
        vertical_lines: List[Tuple[float, float]],
        intersections: List[Tuple[int, int]],
        image_shape: Tuple[int, int]
    ) -> Optional[Dict]:
        """Validate grid structure untuk ensure it represents OMR grid"""

        if not grid_bounds:
            return None

        validation_scores = []

        # 1. Line count validation (reasonable number untuk OMR grid)
        h_count = len(horizontal_lines)
        v_count = len(vertical_lines)

        # Expected line counts untuk common OMR grids
        # 3x20 grid: 4 horizontal, 21 vertical (atau similar)
        # 4x15 grid: 5 horizontal, 16 vertical
        # 5x12 grid: 6 horizontal, 13 vertical

        expected_patterns = [
            (4, 21), (5, 16), (6, 13),  # Standard patterns
            (21, 4), (16, 5), (13, 6)   # Rotated patterns
        ]

        line_count_scores = []
        for exp_h, exp_v in expected_patterns:
            h_score = 1.0 - abs(h_count - exp_h) / max(exp_h, h_count)
            v_score = 1.0 - abs(v_count - exp_v) / max(exp_v, v_count)
            combined_score = (h_score + v_score) / 2
            line_count_scores.append(combined_score)

        line_count_validation = max(line_count_scores)
        validation_scores.append(line_count_validation * 0.3)

        # 2. Line spacing validation (regular spacing)
        h_spacing_score = self._validate_line_spacing(horizontal_lines)
        v_spacing_score = self._validate_line_spacing(vertical_lines)
        spacing_validation = (h_spacing_score + v_spacing_score) / 2
        validation_scores.append(spacing_validation * 0.3)

        # 3. Intersection pattern validation
        intersection_score = self._validate_intersection_pattern(
            intersections, grid_bounds, h_count, v_count
        )
        validation_scores.append(intersection_score * 0.2)

        # 4. Grid geometry validation
        geometry_score = self._validate_grid_geometry(grid_bounds, image_shape)
        validation_scores.append(geometry_score * 0.2)

        overall_validation = sum(validation_scores)
        grid_bounds['validation_score'] = overall_validation

        if overall_validation >= 0.4:  # Minimum validation threshold
            return grid_bounds
        else:
            logger.debug(f"Grid validation failed: score={overall_validation:.3f}")
            return None

    def _validate_line_spacing(self, lines: List[Tuple[float, float]]) -> float:
        """Validate regularity line spacing"""

        if len(lines) < 3:
            return 0.5  # Can't validate spacing dengan few lines

        # Extract rho values dan sort
        rho_values = sorted([line[0] for line in lines])

        # Calculate spacing between consecutive lines
        spacings = []
        for i in range(1, len(rho_values)):
            spacing = abs(rho_values[i] - rho_values[i-1])
            spacings.append(spacing)

        if not spacings:
            return 0.0

        # Calculate coefficient of variation untuk spacing regularity
        mean_spacing = np.mean(spacings)
        std_spacing = np.std(spacings)

        if mean_spacing == 0:
            return 0.0

        cv = std_spacing / mean_spacing

        # Score berdasarkan regularity (lower CV = higher score)
        if cv <= 0.1:
            return 1.0
        elif cv <= 0.3:
            return 0.8
        elif cv <= 0.5:
            return 0.6
        else:
            return 0.3

    def _validate_intersection_pattern(
        self,
        intersections: List[Tuple[int, int]],
        grid_bounds: Dict,
        h_count: int,
        v_count: int
    ) -> float:
        """Validate intersection pattern untuk grid structure"""

        expected_intersections = h_count * v_count
        actual_intersections = len(intersections)

        if expected_intersections == 0:
            return 0.0

        # Score berdasarkan how close actual vs expected intersection count
        intersection_ratio = actual_intersections / expected_intersections
        if 0.7 <= intersection_ratio <= 1.3:
            intersection_score = 1.0
        elif 0.5 <= intersection_ratio <= 1.5:
            intersection_score = 0.7
        else:
            intersection_score = 0.3

        # Additional validation: intersection distribution
        if intersections:
            x_coords = [point[0] for point in intersections]
            y_coords = [point[1] for point in intersections]

            x1, y1, x2, y2 = grid_bounds['coordinates']

            # Check if intersections are well distributed across grid
            x_coverage = (max(x_coords) - min(x_coords)) / (x2 - x1) if x2 > x1 else 0
            y_coverage = (max(y_coords) - min(y_coords)) / (y2 - y1) if y2 > y1 else 0

            coverage_score = (x_coverage + y_coverage) / 2
            overall_score = (intersection_score + coverage_score) / 2
        else:
            overall_score = intersection_score

        return overall_score

    def _validate_grid_geometry(self, grid_bounds: Dict, image_shape: Tuple[int, int]) -> float:
        """Validate grid geometry characteristics"""

        h, w = image_shape[:2]
        x1, y1, x2, y2 = grid_bounds['coordinates']

        validation_checks = []

        # 1. Position validation (not too close to edges)
        margin_x = min(x1, w - x2) / w
        margin_y = min(y1, h - y2) / h
        position_score = min(1.0, (margin_x + margin_y) * 3)
        validation_checks.append(position_score)

        # 2. Size validation
        area_ratio = grid_bounds['area'] / (w * h)
        if 0.1 <= area_ratio <= 0.7:
            size_score = 1.0
        elif 0.05 <= area_ratio <= 0.9:
            size_score = 0.7
        else:
            size_score = 0.3
        validation_checks.append(size_score)

        # 3. Aspect ratio validation untuk OMR grids
        aspect_ratio = grid_bounds['aspect_ratio']
        common_ratios = [3/20, 4/15, 5/12, 20/3, 15/4, 12/5, 1.0, 1.5, 2.0]

        aspect_scores = []
        for ratio in common_ratios:
            similarity = 1.0 - abs(aspect_ratio - ratio) / max(ratio, aspect_ratio)
            aspect_scores.append(similarity)

        best_aspect_score = max(aspect_scores)
        validation_checks.append(best_aspect_score)

        return np.mean(validation_checks)

    def _extract_grid_corners(self, validated_grid: Dict) -> List[Tuple[int, int]]:
        """Extract grid corners dari validated grid"""

        x1, y1, x2, y2 = validated_grid['coordinates']

        corners = [
            (x1, y1),  # Top-left
            (x2, y1),  # Top-right
            (x2, y2),  # Bottom-right
            (x1, y2)   # Bottom-left
        ]

        return corners

    def _calculate_confidence(
        self,
        validated_grid: Optional[Dict],
        horizontal_lines: List[Tuple[float, float]],
        vertical_lines: List[Tuple[float, float]],
        intersections: List[Tuple[int, int]]
    ) -> float:
        """Calculate confidence score untuk Hough-based detection"""

        if not validated_grid:
            return 0.0

        confidence_factors = []

        # 1. Validation score
        validation_score = validated_grid.get('validation_score', 0.0)
        confidence_factors.append(validation_score * 0.4)

        # 2. Line detection quality
        total_lines = len(horizontal_lines) + len(vertical_lines)
        if 6 <= total_lines <= 40:  # Reasonable line count
            line_score = 1.0
        elif 3 <= total_lines <= 60:
            line_score = 0.7
        else:
            line_score = 0.3
        confidence_factors.append(line_score * 0.25)

        # 3. Intersection quality
        intersection_count = len(intersections)
        expected_range = range(10, 100)  # Expected intersection count untuk OMR
        if intersection_count in expected_range:
            intersection_score = 1.0
        elif 5 <= intersection_count <= 150:
            intersection_score = 0.7
        else:
            intersection_score = 0.3
        confidence_factors.append(intersection_score * 0.25)

        # 4. Grid geometry quality
        aspect_ratio = validated_grid.get('aspect_ratio', 0.0)
        area_score = validated_grid.get('area', 0.0)

        # Reasonable geometry untuk OMR grids
        if 0.5 <= aspect_ratio <= 2.0 and area_score > 0:
            geometry_score = 1.0
        else:
            geometry_score = 0.5
        confidence_factors.append(geometry_score * 0.1)

        final_confidence = sum(confidence_factors)
        return min(1.0, final_confidence)