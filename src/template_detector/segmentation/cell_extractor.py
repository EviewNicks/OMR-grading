"""
Cell Extractor untuk Template Detection system
Individual cell extraction dengan precision boundary detection dan quality assessment
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
import time

from ..config import SegmentationConfig
from ..utils.quality_assessment import QualityAssessment, SegmentationQualityMetrics

logger = logging.getLogger(__name__)


@dataclass
class CellExtractionResult:
    """Data structure untuk cell extraction results"""
    extracted_cells: List[np.ndarray]
    cell_coordinates: List[Tuple[int, int, int, int]]
    cell_quality_scores: List[float]
    grid_structure: Dict[str, int]  # rows, cols, total_cells
    extraction_quality: float
    processing_time: float
    problematic_cells: List[int]
    error_message: Optional[str] = None


class CellExtractor:
    """Individual cell extraction dengan adaptive grid detection dan quality assessment"""

    def __init__(self, config: SegmentationConfig):
        """
        Initialize cell extractor

        Args:
            config: Configuration untuk segmentation parameters
        """
        self.config = config
        self.quality_assessor = QualityAssessment()

    def extract_cells(
        self,
        normalized_grid: np.ndarray,
        expected_grid_type: Optional[str] = None,
        extraction_method: str = "adaptive"
    ) -> CellExtractionResult:
        """
        Main method untuk extracting individual cells dari normalized grid

        Args:
            normalized_grid: Normalized grid image
            expected_grid_type: Expected grid type (e.g., "3x20", "4x15")
            extraction_method: Extraction method ("adaptive", "uniform", "detection")

        Returns:
            CellExtractionResult object
        """
        start_time = time.time()

        try:
            # 1. Detect grid structure
            grid_structure = self._detect_grid_structure(
                normalized_grid, expected_grid_type
            )

            if not grid_structure or grid_structure['total_cells'] == 0:
                return self._create_failed_result(
                    "Failed to detect grid structure", time.time() - start_time
                )

            # 2. Extract cells berdasarkan method
            if extraction_method == "adaptive":
                cells, coordinates = self._extract_cells_adaptive(
                    normalized_grid, grid_structure
                )
            elif extraction_method == "uniform":
                cells, coordinates = self._extract_cells_uniform(
                    normalized_grid, grid_structure
                )
            elif extraction_method == "detection":
                cells, coordinates = self._extract_cells_detection(
                    normalized_grid, grid_structure
                )
            else:
                return self._create_failed_result(
                    f"Unknown extraction method: {extraction_method}",
                    time.time() - start_time
                )

            # 3. Quality assessment untuk each cell
            cell_quality_scores = self._assess_cell_quality(cells)

            # 4. Identify problematic cells
            problematic_cells = self._identify_problematic_cells(
                cell_quality_scores, cells
            )

            # 5. Calculate overall extraction quality
            extraction_quality = self._calculate_extraction_quality(
                cells, cell_quality_scores, grid_structure
            )

            processing_time = time.time() - start_time

            logger.debug(f"Extracted {len(cells)} cells dengan quality {extraction_quality:.3f}")

            return CellExtractionResult(
                extracted_cells=cells,
                cell_coordinates=coordinates,
                cell_quality_scores=cell_quality_scores,
                grid_structure=grid_structure,
                extraction_quality=extraction_quality,
                processing_time=processing_time,
                problematic_cells=problematic_cells
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error dalam cell extraction: {str(e)}")

            return self._create_failed_result(str(e), processing_time)

    def _detect_grid_structure(
        self,
        grid_image: np.ndarray,
        expected_type: Optional[str] = None
    ) -> Optional[Dict[str, int]]:
        """Detect grid structure (rows dan columns)"""

        # Try expected type first
        if expected_type:
            structure = self._parse_grid_type(expected_type)
            if structure and self._validate_grid_structure(grid_image, structure):
                logger.debug(f"Using expected grid structure: {expected_type}")
                return structure

        # Auto-detect grid structure
        detected_structure = self._auto_detect_grid_structure(grid_image)

        if detected_structure:
            logger.debug(f"Auto-detected grid structure: "
                        f"{detected_structure['rows']}x{detected_structure['cols']}")
            return detected_structure

        # Fallback to common OMR configurations
        common_structures = [
            {'rows': 3, 'cols': 20, 'total_cells': 60},
            {'rows': 4, 'cols': 15, 'total_cells': 60},
            {'rows': 5, 'cols': 12, 'total_cells': 60},
            {'rows': 20, 'cols': 3, 'total_cells': 60},
            {'rows': 15, 'cols': 4, 'total_cells': 60},
            {'rows': 12, 'cols': 5, 'total_cells': 60}
        ]

        for structure in common_structures:
            if self._validate_grid_structure(grid_image, structure):
                logger.debug(f"Using fallback structure: "
                            f"{structure['rows']}x{structure['cols']}")
                return structure

        return None

    def _parse_grid_type(self, grid_type: str) -> Optional[Dict[str, int]]:
        """Parse grid type string ke structure dictionary"""

        try:
            if 'x' in grid_type:
                rows_str, cols_str = grid_type.split('x')
                rows = int(rows_str)
                cols = int(cols_str)

                return {
                    'rows': rows,
                    'cols': cols,
                    'total_cells': rows * cols
                }
        except ValueError:
            logger.warning(f"Cannot parse grid type: {grid_type}")

        return None

    def _validate_grid_structure(
        self,
        grid_image: np.ndarray,
        structure: Dict[str, int]
    ) -> bool:
        """Validate if proposed grid structure is reasonable untuk image"""

        rows = structure['rows']
        cols = structure['cols']

        h, w = grid_image.shape[:2]

        # Calculate expected cell size
        expected_cell_width = w / cols
        expected_cell_height = h / rows

        # Check if cell sizes are reasonable
        min_cell_size = 10
        max_cell_size = min(w // 2, h // 2)

        if not (min_cell_size <= expected_cell_width <= max_cell_size):
            return False

        if not (min_cell_size <= expected_cell_height <= max_cell_size):
            return False

        # Check aspect ratio reasonableness
        cell_aspect_ratio = expected_cell_width / expected_cell_height
        if not (0.2 <= cell_aspect_ratio <= 5.0):
            return False

        return True

    def _auto_detect_grid_structure(self, grid_image: np.ndarray) -> Optional[Dict[str, int]]:
        """Auto-detect grid structure menggunakan line detection"""

        # Convert to grayscale if needed
        if len(grid_image.shape) == 3:
            gray = cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = grid_image.copy()

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Detect horizontal dan vertical lines
        horizontal_lines = self._detect_grid_lines(edges, 'horizontal')
        vertical_lines = self._detect_grid_lines(edges, 'vertical')

        if len(horizontal_lines) < 2 or len(vertical_lines) < 2:
            return None

        # Calculate grid structure
        rows = len(horizontal_lines) - 1
        cols = len(vertical_lines) - 1

        if rows <= 0 or cols <= 0:
            return None

        structure = {
            'rows': rows,
            'cols': cols,
            'total_cells': rows * cols
        }

        # Validate detected structure
        if self._validate_grid_structure(grid_image, structure):
            return structure

        return None

    def _detect_grid_lines(
        self,
        edges: np.ndarray,
        direction: str
    ) -> List[int]:
        """Detect grid lines dalam specified direction"""

        h, w = edges.shape

        if direction == 'horizontal':
            # Project edges horizontally
            projection = np.sum(edges, axis=1)
            line_threshold = w * 0.3  # Minimum line length
        else:  # vertical
            # Project edges vertically
            projection = np.sum(edges, axis=0)
            line_threshold = h * 0.3  # Minimum line length

        # Find peaks dalam projection
        line_positions = []
        for i in range(len(projection)):
            if projection[i] > line_threshold:
                line_positions.append(i)

        # Filter close positions (merge nearby lines)
        if not line_positions:
            return []

        filtered_positions = [line_positions[0]]
        min_distance = 20  # Minimum distance between lines

        for pos in line_positions[1:]:
            if pos - filtered_positions[-1] >= min_distance:
                filtered_positions.append(pos)

        return filtered_positions

    def _extract_cells_adaptive(
        self,
        grid_image: np.ndarray,
        grid_structure: Dict[str, int]
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]]]:
        """Extract cells menggunakan adaptive method dengan line detection"""

        # Convert to grayscale untuk line detection
        if len(grid_image.shape) == 3:
            gray = cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = grid_image.copy()

        # Detect grid lines
        edges = cv2.Canny(gray, 50, 150)
        horizontal_lines = self._detect_grid_lines(edges, 'horizontal')
        vertical_lines = self._detect_grid_lines(edges, 'vertical')

        # If line detection insufficient, fallback to uniform
        if (len(horizontal_lines) < grid_structure['rows'] + 1 or
            len(vertical_lines) < grid_structure['cols'] + 1):
            logger.debug("Insufficient lines detected, using uniform extraction")
            return self._extract_cells_uniform(grid_image, grid_structure)

        # Extract cells berdasarkan detected lines
        cells = []
        coordinates = []

        for i in range(len(horizontal_lines) - 1):
            for j in range(len(vertical_lines) - 1):
                y1 = horizontal_lines[i]
                y2 = horizontal_lines[i + 1]
                x1 = vertical_lines[j]
                x2 = vertical_lines[j + 1]

                # Add padding
                padding = self.config.cell_padding
                padded_y1 = max(0, y1 + padding)
                padded_y2 = min(grid_image.shape[0], y2 - padding)
                padded_x1 = max(0, x1 + padding)
                padded_x2 = min(grid_image.shape[1], x2 - padding)

                if padded_y2 > padded_y1 and padded_x2 > padded_x1:
                    cell = grid_image[padded_y1:padded_y2, padded_x1:padded_x2]
                    if cell.size > 0:
                        cells.append(cell)
                        coordinates.append((padded_x1, padded_y1, padded_x2, padded_y2))

        return cells, coordinates

    def _extract_cells_uniform(
        self,
        grid_image: np.ndarray,
        grid_structure: Dict[str, int]
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]]]:
        """Extract cells menggunakan uniform grid division"""

        rows = grid_structure['rows']
        cols = grid_structure['cols']

        h, w = grid_image.shape[:2]

        # Calculate cell dimensions
        cell_height = h / rows
        cell_width = w / cols

        cells = []
        coordinates = []

        for i in range(rows):
            for j in range(cols):
                # Calculate cell boundaries
                y1 = int(i * cell_height)
                y2 = int((i + 1) * cell_height)
                x1 = int(j * cell_width)
                x2 = int((j + 1) * cell_width)

                # Add padding
                padding = self.config.cell_padding
                padded_y1 = max(0, y1 + padding)
                padded_y2 = min(h, y2 - padding)
                padded_x1 = max(0, x1 + padding)
                padded_x2 = min(w, x2 - padding)

                if padded_y2 > padded_y1 and padded_x2 > padded_x1:
                    cell = grid_image[padded_y1:padded_y2, padded_x1:padded_x2]
                    if cell.size > 0:
                        cells.append(cell)
                        coordinates.append((padded_x1, padded_y1, padded_x2, padded_y2))

        return cells, coordinates

    def _extract_cells_detection(
        self,
        grid_image: np.ndarray,
        grid_structure: Dict[str, int]
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int, int, int]]]:
        """Extract cells menggunakan contour detection method"""

        # Convert to grayscale
        if len(grid_image.shape) == 3:
            gray = cv2.cvtColor(grid_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = grid_image.copy()

        # Threshold untuk find cell boundaries
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by size
        min_area = self.config.min_cell_area
        max_area = self.config.max_cell_area

        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area <= area <= max_area:
                valid_contours.append(contour)

        # Sort contours by position (top to bottom, left to right)
        valid_contours = self._sort_contours_by_position(valid_contours)

        # Extract cells dari contours
        cells = []
        coordinates = []

        for contour in valid_contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Add padding
            padding = self.config.cell_padding
            padded_x = max(0, x - padding)
            padded_y = max(0, y - padding)
            padded_w = min(grid_image.shape[1] - padded_x, w + 2 * padding)
            padded_h = min(grid_image.shape[0] - padded_y, h + 2 * padding)

            if padded_w > 0 and padded_h > 0:
                cell = grid_image[padded_y:padded_y + padded_h, padded_x:padded_x + padded_w]
                if cell.size > 0:
                    cells.append(cell)
                    coordinates.append((padded_x, padded_y, padded_x + padded_w, padded_y + padded_h))

        return cells, coordinates

    def _sort_contours_by_position(self, contours: List[np.ndarray]) -> List[np.ndarray]:
        """Sort contours by position (top to bottom, left to right)"""

        # Calculate centroids
        centroids = []
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append((cx, cy))
            else:
                x, y, w, h = cv2.boundingRect(contour)
                centroids.append((x + w // 2, y + h // 2))

        # Sort by y first (top to bottom), then by x (left to right)
        sorted_indices = sorted(range(len(centroids)),
                               key=lambda i: (centroids[i][1], centroids[i][0]))

        return [contours[i] for i in sorted_indices]

    def _assess_cell_quality(self, cells: List[np.ndarray]) -> List[float]:
        """Assess quality untuk each extracted cell"""

        quality_scores = []

        for cell in cells:
            if cell.size == 0:
                quality_scores.append(0.0)
                continue

            quality_factors = []

            # 1. Size validation
            h, w = cell.shape[:2]
            if 10 <= h <= 200 and 10 <= w <= 200:  # Reasonable cell size
                size_score = 1.0
            elif 5 <= h <= 300 and 5 <= w <= 300:
                size_score = 0.7
            else:
                size_score = 0.3
            quality_factors.append(size_score * 0.3)

            # 2. Aspect ratio validation
            aspect_ratio = w / h if h > 0 else 0
            if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratio
                aspect_score = 1.0
            elif 0.3 <= aspect_ratio <= 3.0:
                aspect_score = 0.7
            else:
                aspect_score = 0.3
            quality_factors.append(aspect_score * 0.2)

            # 3. Content validation (not blank)
            if len(cell.shape) == 3:
                gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            else:
                gray_cell = cell

            pixel_variance = np.var(gray_cell)
            if pixel_variance > 100:  # Has significant content
                content_score = 1.0
            elif pixel_variance > 50:
                content_score = 0.7
            else:
                content_score = 0.3
            quality_factors.append(content_score * 0.3)

            # 4. Edge clarity
            edges = cv2.Canny(gray_cell, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            if edge_density > 0.05:  # Good edge density
                edge_score = 1.0
            elif edge_density > 0.02:
                edge_score = 0.7
            else:
                edge_score = 0.5
            quality_factors.append(edge_score * 0.2)

            total_quality = sum(quality_factors)
            quality_scores.append(total_quality)

        return quality_scores

    def _identify_problematic_cells(
        self,
        quality_scores: List[float],
        cells: List[np.ndarray]
    ) -> List[int]:
        """Identify problematic cells yang need attention"""

        problematic_cells = []
        quality_threshold = 0.5

        for idx, (quality, cell) in enumerate(zip(quality_scores, cells)):
            if quality < quality_threshold:
                problematic_cells.append(idx)

        logger.debug(f"Identified {len(problematic_cells)} problematic cells")
        return problematic_cells

    def _calculate_extraction_quality(
        self,
        cells: List[np.ndarray],
        quality_scores: List[float],
        grid_structure: Dict[str, int]
    ) -> float:
        """Calculate overall extraction quality"""

        if not cells or not quality_scores:
            return 0.0

        quality_factors = []

        # 1. Extraction completeness
        expected_cells = grid_structure['total_cells']
        actual_cells = len(cells)
        completeness = min(1.0, actual_cells / expected_cells) if expected_cells > 0 else 0.0
        quality_factors.append(completeness * 0.4)

        # 2. Average cell quality
        avg_quality = np.mean(quality_scores)
        quality_factors.append(avg_quality * 0.4)

        # 3. Quality consistency
        if len(quality_scores) > 1:
            quality_std = np.std(quality_scores)
            consistency = max(0.0, 1.0 - quality_std)
            quality_factors.append(consistency * 0.2)
        else:
            quality_factors.append(0.8 * 0.2)  # Single cell gets good consistency

        overall_quality = sum(quality_factors)
        return min(1.0, overall_quality)

    def _create_failed_result(self, error_message: str, processing_time: float) -> CellExtractionResult:
        """Create failed extraction result"""

        return CellExtractionResult(
            extracted_cells=[],
            cell_coordinates=[],
            cell_quality_scores=[],
            grid_structure={'rows': 0, 'cols': 0, 'total_cells': 0},
            extraction_quality=0.0,
            processing_time=processing_time,
            problematic_cells=[],
            error_message=error_message
        )

    def refine_cell_boundaries(
        self,
        cell: np.ndarray,
        original_coordinates: Tuple[int, int, int, int]
    ) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        """Refine cell boundaries untuk improved accuracy"""

        # Convert to grayscale if needed
        if len(cell.shape) == 3:
            gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        else:
            gray = cell.copy()

        # Find content boundaries
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find largest contour (main content)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)

            # Extract refined region
            refined_cell = cell[y:y+h, x:x+w] if y+h <= cell.shape[0] and x+w <= cell.shape[1] else cell

            # Calculate refined coordinates
            orig_x1, orig_y1, orig_x2, orig_y2 = original_coordinates
            refined_coords = (orig_x1 + x, orig_y1 + y, orig_x1 + x + w, orig_y1 + y + h)

            return refined_cell, refined_coords

        return cell, original_coordinates