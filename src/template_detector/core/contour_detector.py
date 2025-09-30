"""
Contour-Based Grid Detection untuk Template Detection system
Hierarchical contour analysis dengan geometric filtering untuk robust grid detection
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
import time

from ..config import ContourDetectionConfig
from ..utils.quality_assessment import QualityAssessment

logger = logging.getLogger(__name__)


@dataclass
class ContourDetectionResult:
    """Data structure untuk contour detection results"""
    grid_coordinates: Optional[Tuple[int, int, int, int]]
    confidence: float
    contours: List[np.ndarray]
    grid_corners: Optional[List[Tuple[int, int]]]
    rectangularity_score: float
    aspect_ratio: float
    processing_time: float
    method: str = "contour"
    validation_score: float = 0.0
    error_message: Optional[str] = None


class ContourGridDetector:
    """Contour-based grid detection dengan hierarchical analysis dan geometric filtering"""

    def __init__(self, config: ContourDetectionConfig):
        """
        Initialize contour grid detector

        Args:
            config: Configuration untuk contour detection parameters
        """
        self.config = config
        self.quality_assessor = QualityAssessment()

    def detect_grid(
        self,
        image: np.ndarray,
        preprocessing_params: Optional[Dict] = None
    ) -> ContourDetectionResult:
        """
        Main method untuk detecting grid menggunakan contour analysis

        Args:
            image: Input image (grayscale atau color)
            preprocessing_params: Optional preprocessing parameters

        Returns:
            ContourDetectionResult object
        """
        start_time = time.time()

        try:
            # 1. Preprocessing
            processed_image = self._preprocess_image(image, preprocessing_params)

            # 2. Contour Detection
            contours, hierarchy = self._detect_contours(processed_image)

            # 3. Geometric Filtering
            filtered_contours = self._filter_contours_by_geometry(contours, image.shape)

            # 4. Grid Candidate Selection
            grid_candidates = self._select_grid_candidates(filtered_contours, hierarchy)

            # 5. Best Grid Selection
            best_grid = self._select_best_grid(grid_candidates, image.shape)

            # 6. Grid Validation dan Refinement
            validated_grid = self._validate_and_refine_grid(best_grid, image.shape)

            # 7. Calculate Confidence
            confidence = self._calculate_confidence(validated_grid, filtered_contours)

            processing_time = time.time() - start_time

            if validated_grid:
                return ContourDetectionResult(
                    grid_coordinates=validated_grid['coordinates'],
                    confidence=confidence,
                    contours=filtered_contours,
                    grid_corners=validated_grid.get('corners'),
                    rectangularity_score=validated_grid.get('rectangularity', 0.0),
                    aspect_ratio=validated_grid.get('aspect_ratio', 0.0),
                    processing_time=processing_time,
                    validation_score=validated_grid.get('validation_score', 0.0)
                )
            else:
                return ContourDetectionResult(
                    grid_coordinates=None,
                    confidence=0.0,
                    contours=filtered_contours,
                    grid_corners=None,
                    rectangularity_score=0.0,
                    aspect_ratio=0.0,
                    processing_time=processing_time,
                    error_message="No valid grid detected"
                )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error dalam contour detection: {str(e)}")

            return ContourDetectionResult(
                grid_coordinates=None,
                confidence=0.0,
                contours=[],
                grid_corners=None,
                rectangularity_score=0.0,
                aspect_ratio=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )

    def _preprocess_image(
        self,
        image: np.ndarray,
        preprocessing_params: Optional[Dict] = None
    ) -> np.ndarray:
        """Preprocess image untuk optimal contour detection"""

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Apply adaptive parameters berdasarkan image characteristics
        if preprocessing_params:
            # Use provided parameters
            blur_kernel = preprocessing_params.get('blur_kernel', 5)
            threshold_method = preprocessing_params.get('threshold_method', 'adaptive')
        else:
            # Default adaptive parameters
            blur_kernel = 5
            threshold_method = 'adaptive'

        # Gaussian blur untuk noise reduction
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)

        # Adaptive thresholding untuk robust edge detection
        if threshold_method == 'adaptive':
            binary = cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
        else:
            # Otsu thresholding
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Morphological operations untuk improve contour quality
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        return binary

    def _detect_contours(self, binary_image: np.ndarray) -> Tuple[List[np.ndarray], np.ndarray]:
        """Detect contours dengan hierarchical information"""

        contours, hierarchy = cv2.findContours(
            binary_image,
            cv2.RETR_TREE,  # Hierarchical retrieval
            cv2.CHAIN_APPROX_SIMPLE
        )

        logger.debug(f"Detected {len(contours)} contours")
        return contours, hierarchy

    def _filter_contours_by_geometry(
        self,
        contours: List[np.ndarray],
        image_shape: Tuple[int, int]
    ) -> List[np.ndarray]:
        """Filter contours berdasarkan geometric criteria"""

        filtered_contours = []
        h, w = image_shape[:2]
        image_area = h * w

        for contour in contours:
            # 1. Area filtering
            area = cv2.contourArea(contour)
            if not (self.config.min_area <= area <= self.config.max_area):
                continue

            # 2. Area ratio filtering (relative to image size)
            area_ratio = area / image_area
            if not (0.05 <= area_ratio <= 0.8):  # Reasonable grid size
                continue

            # 3. Aspect ratio filtering
            x, y, w_rect, h_rect = cv2.boundingRect(contour)
            if h_rect == 0:
                continue

            aspect_ratio = w_rect / h_rect
            if not (self.config.aspect_ratio_min <= aspect_ratio <= self.config.aspect_ratio_max):
                continue

            # 4. Rectangularity filtering
            rectangularity = self._calculate_rectangularity(contour)
            if rectangularity < self.config.rectangularity_threshold:
                continue

            # 5. Convexity filtering (grids should be relatively convex)
            hull_area = cv2.contourArea(cv2.convexHull(contour))
            convexity = area / hull_area if hull_area > 0 else 0
            if convexity < 0.7:  # Reasonable convexity
                continue

            filtered_contours.append(contour)

        logger.debug(f"Filtered to {len(filtered_contours)} candidate contours")
        return filtered_contours

    def _calculate_rectangularity(self, contour: np.ndarray) -> float:
        """Calculate rectangularity score untuk contour"""

        contour_area = cv2.contourArea(contour)
        if contour_area == 0:
            return 0.0

        # Bounding rectangle area
        x, y, w, h = cv2.boundingRect(contour)
        rect_area = w * h

        rectangularity = contour_area / rect_area if rect_area > 0 else 0.0
        return rectangularity

    def _select_grid_candidates(
        self,
        contours: List[np.ndarray],
        hierarchy: np.ndarray
    ) -> List[Dict]:
        """Select potential grid candidates dari filtered contours"""

        grid_candidates = []

        for idx, contour in enumerate(contours):
            # Calculate geometric properties
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            rectangularity = self._calculate_rectangularity(contour)

            # Approximate contour untuk corner detection
            epsilon = self.config.approximation_epsilon * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Calculate confidence score untuk candidate
            confidence_score = self._calculate_candidate_confidence(
                area, aspect_ratio, rectangularity, len(approx)
            )

            # Extract corners if approximation has 4 points (rectangular)
            corners = None
            if len(approx) == 4:
                corners = [(point[0][0], point[0][1]) for point in approx]

            grid_candidates.append({
                'contour': contour,
                'coordinates': (x, y, x + w, y + h),
                'corners': corners,
                'area': area,
                'aspect_ratio': aspect_ratio,
                'rectangularity': rectangularity,
                'confidence': confidence_score,
                'approx_points': len(approx)
            })

        # Sort by confidence score
        grid_candidates.sort(key=lambda x: x['confidence'], reverse=True)

        logger.debug(f"Selected {len(grid_candidates)} grid candidates")
        return grid_candidates

    def _calculate_candidate_confidence(
        self,
        area: float,
        aspect_ratio: float,
        rectangularity: float,
        approx_points: int
    ) -> float:
        """Calculate confidence score untuk grid candidate"""

        score_components = []

        # 1. Rectangularity score (higher is better)
        rect_score = min(1.0, rectangularity / self.config.rectangularity_threshold)
        score_components.append(rect_score * 0.4)

        # 2. Aspect ratio score (prefer reasonable ratios)
        ideal_ratios = [1.0, 1.5, 2.0, 0.67, 0.5]  # Common OMR grid ratios
        aspect_scores = [1.0 - abs(aspect_ratio - ideal) / ideal for ideal in ideal_ratios]
        best_aspect_score = max(aspect_scores)
        score_components.append(best_aspect_score * 0.3)

        # 3. Area score (prefer moderate sizes)
        area_score = 1.0 if self.config.min_area <= area <= self.config.max_area else 0.5
        score_components.append(area_score * 0.2)

        # 4. Approximation points score (prefer 4 corners)
        if approx_points == 4:
            points_score = 1.0
        elif 3 <= approx_points <= 6:
            points_score = 0.7
        else:
            points_score = 0.3
        score_components.append(points_score * 0.1)

        total_score = sum(score_components)
        return min(1.0, total_score)

    def _select_best_grid(
        self,
        grid_candidates: List[Dict],
        image_shape: Tuple[int, int]
    ) -> Optional[Dict]:
        """Select best grid dari candidates menggunakan multiple criteria"""

        if not grid_candidates:
            return None

        # Additional validation untuk top candidates
        validated_candidates = []

        for candidate in grid_candidates[:5]:  # Check top 5 candidates
            validation_score = self._validate_grid_candidate(candidate, image_shape)
            candidate['validation_score'] = validation_score

            if validation_score > 0.5:  # Minimum validation threshold
                validated_candidates.append(candidate)

        if not validated_candidates:
            logger.warning("No candidates passed validation")
            return None

        # Sort by combined confidence dan validation score
        for candidate in validated_candidates:
            candidate['combined_score'] = (
                candidate['confidence'] * 0.7 +
                candidate['validation_score'] * 0.3
            )

        validated_candidates.sort(key=lambda x: x['combined_score'], reverse=True)

        best_candidate = validated_candidates[0]
        logger.debug(f"Selected best grid dengan confidence {best_candidate['confidence']:.3f}")

        return best_candidate

    def _validate_grid_candidate(self, candidate: Dict, image_shape: Tuple[int, int]) -> float:
        """Validate grid candidate dengan comprehensive checks"""

        validation_checks = []

        # 1. Position validation (not too close to edges)
        x1, y1, x2, y2 = candidate['coordinates']
        h, w = image_shape[:2]

        margin_x = min(x1, w - x2) / w
        margin_y = min(y1, h - y2) / h
        position_score = min(1.0, (margin_x + margin_y) * 5)  # Prefer some margin
        validation_checks.append(position_score)

        # 2. Size validation (reasonable grid size)
        grid_width = x2 - x1
        grid_height = y2 - y1
        size_ratio = (grid_width * grid_height) / (w * h)

        if 0.1 <= size_ratio <= 0.7:
            size_score = 1.0
        elif 0.05 <= size_ratio <= 0.9:
            size_score = 0.7
        else:
            size_score = 0.3
        validation_checks.append(size_score)

        # 3. Aspect ratio validation untuk OMR grids
        aspect_ratio = candidate['aspect_ratio']
        common_ratios = [
            (3/20, "3x20"), (4/15, "4x15"), (5/12, "5x12"),
            (20/3, "20x3"), (15/4, "15x4"), (12/5, "12x5")
        ]

        aspect_scores = []
        for ratio, name in common_ratios:
            similarity = 1.0 - abs(aspect_ratio - ratio) / max(ratio, aspect_ratio)
            aspect_scores.append(similarity)

        best_aspect_score = max(aspect_scores)
        validation_checks.append(best_aspect_score)

        # 4. Contour quality validation
        contour_area = cv2.contourArea(candidate['contour'])
        bbox_area = grid_width * grid_height
        fill_ratio = contour_area / bbox_area if bbox_area > 0 else 0

        if 0.7 <= fill_ratio <= 1.0:
            quality_score = 1.0
        elif 0.5 <= fill_ratio < 0.7:
            quality_score = 0.7
        else:
            quality_score = 0.3
        validation_checks.append(quality_score)

        # 5. Corner validation (if available)
        if candidate['corners'] and len(candidate['corners']) == 4:
            corner_score = self._validate_corner_geometry(candidate['corners'])
            validation_checks.append(corner_score)

        return np.mean(validation_checks)

    def _validate_corner_geometry(self, corners: List[Tuple[int, int]]) -> float:
        """Validate corner geometry untuk rectangular grid"""

        if len(corners) != 4:
            return 0.0

        # Calculate angles at corners
        angles = []
        for i in range(4):
            p1 = np.array(corners[i])
            p2 = np.array(corners[(i + 1) % 4])
            p3 = np.array(corners[(i + 2) % 4])

            v1 = p1 - p2
            v2 = p3 - p2

            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle = np.arccos(cos_angle) * 180 / np.pi

            angles.append(angle)

        # Check how close angles are to 90 degrees
        angle_deviations = [abs(angle - 90) for angle in angles]
        avg_deviation = np.mean(angle_deviations)

        # Score berdasarkan deviation dari 90 degrees
        if avg_deviation <= 10:  # Within 10 degrees
            return 1.0
        elif avg_deviation <= 20:  # Within 20 degrees
            return 0.7
        elif avg_deviation <= 30:  # Within 30 degrees
            return 0.4
        else:
            return 0.1

    def _validate_and_refine_grid(
        self,
        grid_candidate: Optional[Dict],
        image_shape: Tuple[int, int]
    ) -> Optional[Dict]:
        """Final validation dan refinement grid detection"""

        if not grid_candidate:
            return None

        # Apply final refinements
        refined_candidate = grid_candidate.copy()

        # 1. Coordinate refinement (sub-pixel accuracy)
        contour = grid_candidate['contour']
        if len(contour) > 0:
            # Fit minimal area rectangle untuk better coordinates
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)

            # Update coordinates dengan refined box
            x_coords = box[:, 0]
            y_coords = box[:, 1]
            refined_coordinates = (
                int(np.min(x_coords)),
                int(np.min(y_coords)),
                int(np.max(x_coords)),
                int(np.max(y_coords))
            )
            refined_candidate['coordinates'] = refined_coordinates

            # Update corners
            refined_candidate['corners'] = [(int(point[0]), int(point[1])) for point in box]

        # 2. Final validation check
        final_validation = self._validate_grid_candidate(refined_candidate, image_shape)
        refined_candidate['validation_score'] = final_validation

        if final_validation < 0.3:  # Minimum threshold
            logger.warning("Final validation failed")
            return None

        return refined_candidate

    def _calculate_confidence(
        self,
        validated_grid: Optional[Dict],
        filtered_contours: List[np.ndarray]
    ) -> float:
        """Calculate final confidence score untuk detection"""

        if not validated_grid:
            return 0.0

        confidence_factors = []

        # 1. Validation score
        validation_score = validated_grid.get('validation_score', 0.0)
        confidence_factors.append(validation_score * 0.4)

        # 2. Geometric quality
        rectangularity = validated_grid.get('rectangularity', 0.0)
        confidence_factors.append(rectangularity * 0.3)

        # 3. Uniqueness (how much better than other candidates)
        candidate_confidence = validated_grid.get('confidence', 0.0)
        confidence_factors.append(candidate_confidence * 0.2)

        # 4. Contour quality
        contour_count = len(filtered_contours)
        if contour_count > 0:
            # Prefer moderate number of contours (not too many, not too few)
            if 5 <= contour_count <= 20:
                contour_score = 1.0
            elif 1 <= contour_count <= 50:
                contour_score = 0.7
            else:
                contour_score = 0.3
        else:
            contour_score = 0.0

        confidence_factors.append(contour_score * 0.1)

        final_confidence = sum(confidence_factors)
        return min(1.0, final_confidence)