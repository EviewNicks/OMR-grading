"""
Quality Assessment module untuk Template Detection system
Comprehensive quality metrics untuk detection results dan confidence scoring
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import logging
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)


@dataclass
class DetectionQualityMetrics:
    """Data structure untuk detection quality metrics"""
    geometric_accuracy: float
    confidence_score: float
    consistency_score: float
    completeness_score: float
    robustness_score: float
    overall_quality: float
    uncertainty_bounds: Tuple[float, float]
    validation_flags: Dict[str, bool]


@dataclass
class SegmentationQualityMetrics:
    """Data structure untuk segmentation quality metrics"""
    cell_uniformity: float
    boundary_clarity: float
    grid_regularity: float
    extraction_completeness: float
    cell_quality_distribution: List[float]
    overall_segmentation_quality: float
    problematic_cells: List[int]


class QualityAssessment:
    """Quality assessment framework untuk template detection dan segmentation"""

    def __init__(self, confidence_threshold: float = 0.6, quality_threshold: float = 0.7):
        """
        Initialize quality assessment dengan thresholds

        Args:
            confidence_threshold: Minimum confidence untuk acceptable detection
            quality_threshold: Minimum quality score untuk validation
        """
        self.confidence_threshold = confidence_threshold
        self.quality_threshold = quality_threshold

    def assess_detection_quality(
        self,
        detection_result: Dict,
        ground_truth: Optional[Dict] = None,
        image_shape: Tuple[int, int] = None
    ) -> DetectionQualityMetrics:
        """
        Assess quality untuk detection results

        Args:
            detection_result: Detection result dengan coordinates dan confidence
            ground_truth: Optional ground truth untuk accuracy calculation
            image_shape: Image dimensions untuk relative assessment

        Returns:
            DetectionQualityMetrics object
        """
        metrics = {}

        # 1. Geometric Accuracy Assessment
        metrics['geometric_accuracy'] = self._assess_geometric_accuracy(
            detection_result, ground_truth, image_shape
        )

        # 2. Confidence Score Validation
        metrics['confidence_score'] = self._validate_confidence_score(detection_result)

        # 3. Consistency Score (internal validation)
        metrics['consistency_score'] = self._assess_detection_consistency(detection_result)

        # 4. Completeness Score
        metrics['completeness_score'] = self._assess_detection_completeness(detection_result)

        # 5. Robustness Score (stability assessment)
        metrics['robustness_score'] = self._assess_detection_robustness(detection_result)

        # 6. Overall Quality Score
        metrics['overall_quality'] = self._calculate_overall_quality(metrics)

        # 7. Uncertainty Bounds
        metrics['uncertainty_bounds'] = self._calculate_uncertainty_bounds(metrics)

        # 8. Validation Flags
        metrics['validation_flags'] = self._generate_validation_flags(metrics)

        return DetectionQualityMetrics(**metrics)

    def _assess_geometric_accuracy(
        self,
        detection_result: Dict,
        ground_truth: Optional[Dict],
        image_shape: Tuple[int, int]
    ) -> float:
        """Assess geometric accuracy detection results"""
        if ground_truth is None:
            # Internal geometric validation
            return self._internal_geometric_validation(detection_result, image_shape)

        # Ground truth comparison
        if 'grid_coordinates' not in detection_result or 'grid_coordinates' not in ground_truth:
            return 0.0

        detected_coords = detection_result['grid_coordinates']
        true_coords = ground_truth['grid_coordinates']

        if detected_coords is None or true_coords is None:
            return 0.0

        # Calculate IoU (Intersection over Union)
        iou = self._calculate_iou(detected_coords, true_coords)
        return iou

    def _internal_geometric_validation(
        self,
        detection_result: Dict,
        image_shape: Tuple[int, int]
    ) -> float:
        """Internal geometric validation tanpa ground truth"""
        if 'grid_coordinates' not in detection_result:
            return 0.0

        coords = detection_result['grid_coordinates']
        if coords is None or len(coords) != 4:
            return 0.0

        x1, y1, x2, y2 = coords

        # Validation checks
        checks = []

        # 1. Coordinates within image bounds
        if image_shape:
            h, w = image_shape[:2]
            checks.append(0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h)
        else:
            checks.append(x1 < x2 and y1 < y2)

        # 2. Reasonable grid size (not too small/large)
        grid_width = x2 - x1
        grid_height = y2 - y1
        if image_shape:
            h, w = image_shape[:2]
            size_ratio = (grid_width * grid_height) / (w * h)
            checks.append(0.1 <= size_ratio <= 0.8)

        # 3. Reasonable aspect ratio untuk OMR grid
        aspect_ratio = grid_width / grid_height if grid_height > 0 else 0
        checks.append(0.5 <= aspect_ratio <= 2.0)

        # 4. Grid positioning (not too close to edges)
        if image_shape:
            h, w = image_shape[:2]
            margin_x = min(x1, w - x2) / w
            margin_y = min(y1, h - y2) / h
            checks.append(margin_x >= 0.05 and margin_y >= 0.05)

        return sum(checks) / len(checks)

    def _calculate_iou(self, coords1: List, coords2: List) -> float:
        """Calculate Intersection over Union untuk two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = coords1
        x1_2, y1_2, x2_2, y2_2 = coords2

        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)

        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0

        intersection = (x2_i - x1_i) * (y2_i - y1_i)

        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    def _validate_confidence_score(self, detection_result: Dict) -> float:
        """Validate confidence score dari detection result"""
        confidence = detection_result.get('confidence', 0.0)

        # Normalize confidence to 0-1 range
        normalized_confidence = max(0.0, min(1.0, confidence))

        # Apply confidence threshold
        if normalized_confidence >= self.confidence_threshold:
            return normalized_confidence
        else:
            # Penalize low confidence
            return normalized_confidence * 0.5

    def _assess_detection_consistency(self, detection_result: Dict) -> float:
        """Assess internal consistency detection result"""
        consistency_checks = []

        # 1. Check if confidence matches detection quality
        confidence = detection_result.get('confidence', 0.0)
        has_coordinates = detection_result.get('grid_coordinates') is not None

        if has_coordinates and confidence > 0.5:
            consistency_checks.append(1.0)
        elif not has_coordinates and confidence <= 0.5:
            consistency_checks.append(1.0)
        else:
            consistency_checks.append(0.0)

        # 2. Check method-specific consistency
        method_name = detection_result.get('method', 'unknown')

        if method_name == 'contour':
            contours = detection_result.get('contours')
            if contours is not None and len(contours) > 0:
                consistency_checks.append(1.0)
            else:
                consistency_checks.append(0.0)

        elif method_name == 'hough':
            lines = detection_result.get('detected_lines')
            if lines is not None and len(lines) > 0:
                consistency_checks.append(1.0)
            else:
                consistency_checks.append(0.0)

        elif method_name == 'template':
            match_value = detection_result.get('match_value', 0.0)
            if match_value > 0.5:
                consistency_checks.append(1.0)
            else:
                consistency_checks.append(0.0)

        # 3. Processing time consistency
        processing_time = detection_result.get('processing_time', 0.0)
        if 0.1 <= processing_time <= 10.0:  # Reasonable processing time
            consistency_checks.append(1.0)
        else:
            consistency_checks.append(0.5)

        return np.mean(consistency_checks) if consistency_checks else 0.0

    def _assess_detection_completeness(self, detection_result: Dict) -> float:
        """Assess completeness detection result"""
        required_fields = ['grid_coordinates', 'confidence', 'method', 'processing_time']
        optional_fields = ['grid_corners', 'validation_score']

        completeness_score = 0.0

        # Check required fields
        for field in required_fields:
            if field in detection_result and detection_result[field] is not None:
                completeness_score += 0.7 / len(required_fields)

        # Check optional fields
        for field in optional_fields:
            if field in detection_result and detection_result[field] is not None:
                completeness_score += 0.3 / len(optional_fields)

        return min(1.0, completeness_score)

    def _assess_detection_robustness(self, detection_result: Dict) -> float:
        """Assess robustness detection result"""
        robustness_factors = []

        # 1. Confidence stability
        confidence = detection_result.get('confidence', 0.0)
        confidence_stability = 1.0 - abs(confidence - 0.8)  # Prefer moderate confidence
        robustness_factors.append(max(0.0, confidence_stability))

        # 2. Processing time stability
        processing_time = detection_result.get('processing_time', 0.0)
        if 0.5 <= processing_time <= 3.0:  # Reasonable range
            time_stability = 1.0
        else:
            time_stability = max(0.0, 1.0 - abs(processing_time - 1.5) / 3.0)
        robustness_factors.append(time_stability)

        # 3. Method-specific robustness
        method_name = detection_result.get('method', 'unknown')
        if method_name in ['contour', 'hough', 'template', 'fusion']:
            robustness_factors.append(1.0)
        else:
            robustness_factors.append(0.5)

        return np.mean(robustness_factors)

    def _calculate_overall_quality(self, metrics: Dict) -> float:
        """Calculate overall quality score dari individual metrics"""
        weights = {
            'geometric_accuracy': 0.3,
            'confidence_score': 0.25,
            'consistency_score': 0.2,
            'completeness_score': 0.15,
            'robustness_score': 0.1
        }

        overall_score = 0.0
        for metric, weight in weights.items():
            if metric in metrics:
                overall_score += metrics[metric] * weight

        return min(1.0, overall_score)

    def _calculate_uncertainty_bounds(self, metrics: Dict) -> Tuple[float, float]:
        """Calculate uncertainty bounds untuk quality assessment"""
        overall_quality = metrics.get('overall_quality', 0.0)
        confidence = metrics.get('confidence_score', 0.0)

        # Calculate uncertainty berdasarkan confidence dan consistency
        consistency = metrics.get('consistency_score', 0.0)
        uncertainty = 1.0 - (confidence * consistency)

        lower_bound = max(0.0, overall_quality - uncertainty * 0.2)
        upper_bound = min(1.0, overall_quality + uncertainty * 0.1)

        return (lower_bound, upper_bound)

    def _generate_validation_flags(self, metrics: Dict) -> Dict[str, bool]:
        """Generate validation flags berdasarkan quality metrics"""
        flags = {}

        # Quality thresholds
        flags['passes_quality_threshold'] = metrics.get('overall_quality', 0.0) >= self.quality_threshold
        flags['passes_confidence_threshold'] = metrics.get('confidence_score', 0.0) >= self.confidence_threshold
        flags['geometrically_valid'] = metrics.get('geometric_accuracy', 0.0) >= 0.7
        flags['internally_consistent'] = metrics.get('consistency_score', 0.0) >= 0.8
        flags['sufficiently_complete'] = metrics.get('completeness_score', 0.0) >= 0.8
        flags['sufficiently_robust'] = metrics.get('robustness_score', 0.0) >= 0.7

        # Overall validation
        flags['recommended_for_use'] = all([
            flags['passes_quality_threshold'],
            flags['passes_confidence_threshold'],
            flags['geometrically_valid']
        ])

        return flags

    def assess_segmentation_quality(
        self,
        segmented_cells: List[np.ndarray],
        grid_coordinates: Tuple[int, int, int, int],
        original_image_shape: Tuple[int, int]
    ) -> SegmentationQualityMetrics:
        """
        Assess quality untuk grid segmentation results

        Args:
            segmented_cells: List extracted cell regions
            grid_coordinates: Original grid coordinates
            original_image_shape: Shape original image

        Returns:
            SegmentationQualityMetrics object
        """
        if not segmented_cells:
            return SegmentationQualityMetrics(
                cell_uniformity=0.0,
                boundary_clarity=0.0,
                grid_regularity=0.0,
                extraction_completeness=0.0,
                cell_quality_distribution=[],
                overall_segmentation_quality=0.0,
                problematic_cells=[]
            )

        # 1. Cell Uniformity Assessment
        cell_uniformity = self._assess_cell_uniformity(segmented_cells)

        # 2. Boundary Clarity Assessment
        boundary_clarity = self._assess_boundary_clarity(segmented_cells)

        # 3. Grid Regularity Assessment
        grid_regularity = self._assess_grid_regularity(segmented_cells, grid_coordinates)

        # 4. Extraction Completeness
        extraction_completeness = self._assess_extraction_completeness(
            segmented_cells, grid_coordinates
        )

        # 5. Individual Cell Quality Distribution
        cell_quality_distribution = self._assess_individual_cell_quality(segmented_cells)

        # 6. Identify Problematic Cells
        problematic_cells = self._identify_problematic_cells(cell_quality_distribution)

        # 7. Overall Segmentation Quality
        overall_quality = np.mean([
            cell_uniformity * 0.25,
            boundary_clarity * 0.25,
            grid_regularity * 0.25,
            extraction_completeness * 0.25
        ])

        return SegmentationQualityMetrics(
            cell_uniformity=cell_uniformity,
            boundary_clarity=boundary_clarity,
            grid_regularity=grid_regularity,
            extraction_completeness=extraction_completeness,
            cell_quality_distribution=cell_quality_distribution,
            overall_segmentation_quality=overall_quality,
            problematic_cells=problematic_cells
        )

    def _assess_cell_uniformity(self, segmented_cells: List[np.ndarray]) -> float:
        """Assess uniformity extracted cells"""
        if len(segmented_cells) < 2:
            return 1.0

        # Calculate cell size uniformity
        cell_sizes = [cell.shape[0] * cell.shape[1] for cell in segmented_cells]
        size_cv = np.std(cell_sizes) / np.mean(cell_sizes) if np.mean(cell_sizes) > 0 else 1.0

        # Calculate aspect ratio uniformity
        aspect_ratios = [
            cell.shape[1] / cell.shape[0] if cell.shape[0] > 0 else 1.0
            for cell in segmented_cells
        ]
        aspect_cv = np.std(aspect_ratios) / np.mean(aspect_ratios) if np.mean(aspect_ratios) > 0 else 1.0

        # Uniformity score (lower CV = higher uniformity)
        size_uniformity = max(0.0, 1.0 - size_cv)
        aspect_uniformity = max(0.0, 1.0 - aspect_cv)

        return (size_uniformity + aspect_uniformity) / 2

    def _assess_boundary_clarity(self, segmented_cells: List[np.ndarray]) -> float:
        """Assess boundary clarity extracted cells"""
        clarity_scores = []

        for cell in segmented_cells:
            if cell.size == 0:
                clarity_scores.append(0.0)
                continue

            # Calculate edge strength
            if len(cell.shape) == 3:
                gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            else:
                gray_cell = cell

            edges = cv2.Canny(gray_cell, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size

            # Normalize edge density
            clarity_score = min(1.0, edge_density * 5.0)  # Scale factor
            clarity_scores.append(clarity_score)

        return np.mean(clarity_scores) if clarity_scores else 0.0

    def _assess_grid_regularity(
        self,
        segmented_cells: List[np.ndarray],
        grid_coordinates: Tuple[int, int, int, int]
    ) -> float:
        """Assess regularity grid structure"""
        if len(segmented_cells) == 0:
            return 0.0

        # Expected grid dimensions (estimate dari number of cells)
        num_cells = len(segmented_cells)

        # Common OMR grid configurations
        possible_grids = [(3, 20), (4, 15), (5, 12), (6, 10)]

        best_regularity = 0.0
        for rows, cols in possible_grids:
            if rows * cols == num_cells:
                # Calculate expected vs actual cell arrangements
                x1, y1, x2, y2 = grid_coordinates
                expected_cell_width = (x2 - x1) / cols
                expected_cell_height = (y2 - y1) / rows

                # Check cell size consistency
                actual_widths = [cell.shape[1] for cell in segmented_cells]
                actual_heights = [cell.shape[0] for cell in segmented_cells]

                width_regularity = 1.0 - (np.std(actual_widths) / np.mean(actual_widths))
                height_regularity = 1.0 - (np.std(actual_heights) / np.mean(actual_heights))

                regularity = (width_regularity + height_regularity) / 2
                best_regularity = max(best_regularity, regularity)

        return max(0.0, best_regularity)

    def _assess_extraction_completeness(
        self,
        segmented_cells: List[np.ndarray],
        grid_coordinates: Tuple[int, int, int, int]
    ) -> float:
        """Assess completeness cell extraction"""
        # Expected number of cells untuk OMR grids
        expected_cell_counts = [60, 60, 60]  # 3x20, 4x15, 5x12

        actual_count = len(segmented_cells)

        # Calculate completeness berdasarkan expected counts
        completeness_scores = []
        for expected_count in expected_cell_counts:
            if expected_count > 0:
                completeness = min(1.0, actual_count / expected_count)
                completeness_scores.append(completeness)

        # Return best completeness score
        return max(completeness_scores) if completeness_scores else 0.0

    def _assess_individual_cell_quality(self, segmented_cells: List[np.ndarray]) -> List[float]:
        """Assess quality untuk individual cells"""
        quality_scores = []

        for cell in segmented_cells:
            if cell.size == 0:
                quality_scores.append(0.0)
                continue

            cell_quality = 0.0

            # 1. Size validation
            h, w = cell.shape[:2]
            if 10 <= h <= 100 and 10 <= w <= 100:  # Reasonable cell size
                cell_quality += 0.3

            # 2. Aspect ratio validation
            aspect_ratio = w / h if h > 0 else 0
            if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratio
                cell_quality += 0.3

            # 3. Content validation (not blank)
            if len(cell.shape) == 3:
                gray_cell = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
            else:
                gray_cell = cell

            pixel_variance = np.var(gray_cell)
            if pixel_variance > 100:  # Has content
                cell_quality += 0.4

            quality_scores.append(cell_quality)

        return quality_scores

    def _identify_problematic_cells(self, cell_quality_distribution: List[float]) -> List[int]:
        """Identify problematic cells berdasarkan quality scores"""
        problematic_threshold = 0.5
        problematic_cells = []

        for idx, quality in enumerate(cell_quality_distribution):
            if quality < problematic_threshold:
                problematic_cells.append(idx)

        return problematic_cells

    def generate_quality_report(
        self,
        detection_metrics: DetectionQualityMetrics,
        segmentation_metrics: Optional[SegmentationQualityMetrics] = None
    ) -> Dict:
        """Generate comprehensive quality report"""
        report = {
            'detection_quality': {
                'overall_score': detection_metrics.overall_quality,
                'geometric_accuracy': detection_metrics.geometric_accuracy,
                'confidence_score': detection_metrics.confidence_score,
                'consistency_score': detection_metrics.consistency_score,
                'completeness_score': detection_metrics.completeness_score,
                'robustness_score': detection_metrics.robustness_score,
                'uncertainty_bounds': detection_metrics.uncertainty_bounds,
                'validation_flags': detection_metrics.validation_flags,
                'recommendation': self._generate_recommendation(detection_metrics)
            }
        }

        if segmentation_metrics:
            report['segmentation_quality'] = {
                'overall_score': segmentation_metrics.overall_segmentation_quality,
                'cell_uniformity': segmentation_metrics.cell_uniformity,
                'boundary_clarity': segmentation_metrics.boundary_clarity,
                'grid_regularity': segmentation_metrics.grid_regularity,
                'extraction_completeness': segmentation_metrics.extraction_completeness,
                'total_cells': len(segmentation_metrics.cell_quality_distribution),
                'problematic_cells_count': len(segmentation_metrics.problematic_cells),
                'average_cell_quality': np.mean(segmentation_metrics.cell_quality_distribution)
                if segmentation_metrics.cell_quality_distribution else 0.0
            }

        return report

    def _generate_recommendation(self, metrics: DetectionQualityMetrics) -> str:
        """Generate recommendation berdasarkan quality metrics"""
        if metrics.overall_quality >= 0.9:
            return "EXCELLENT - High quality detection, recommended untuk production use"
        elif metrics.overall_quality >= 0.7:
            return "GOOD - Acceptable quality dengan minor concerns"
        elif metrics.overall_quality >= 0.5:
            return "FAIR - Moderate quality, requires validation"
        else:
            return "POOR - Low quality, tidak recommended untuk use"