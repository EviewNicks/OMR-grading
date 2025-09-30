"""
Detection Fusion untuk Template Detection system
Multi-method consensus algorithm dengan confidence scoring dan uncertainty quantification
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Union, Any
import logging
from dataclasses import dataclass
import time
from scipy import stats
from sklearn.cluster import DBSCAN

from ..config import DetectionFusionConfig
from ..utils.quality_assessment import QualityAssessment, DetectionQualityMetrics
from .contour_detector import ContourDetectionResult
from .hough_detector import HoughDetectionResult
from .template_matcher import TemplateDetectionResult

logger = logging.getLogger(__name__)


@dataclass
class FusionInput:
    """Data structure untuk input detection results"""
    method_name: str
    result: Union[ContourDetectionResult, HoughDetectionResult, TemplateDetectionResult]
    weight: float
    preprocessing_quality: float = 1.0


@dataclass
class FusionResult:
    """Data structure untuk fused detection result"""
    grid_coordinates: Optional[Tuple[int, int, int, int]]
    confidence: float
    consensus_score: float
    uncertainty_bounds: Tuple[float, float]
    contributing_methods: List[str]
    method_agreements: Dict[str, float]
    quality_metrics: Optional[DetectionQualityMetrics]
    processing_time: float
    method: str = "fusion"
    validation_score: float = 0.0
    error_message: Optional[str] = None
    individual_results: Optional[Dict[str, Any]] = None


class DetectionFusion:
    """Multi-method detection fusion dengan weighted consensus dan uncertainty quantification"""

    def __init__(self, config: DetectionFusionConfig):
        """
        Initialize detection fusion system

        Args:
            config: Configuration untuk fusion parameters
        """
        self.config = config
        self.quality_assessor = QualityAssessment(
            confidence_threshold=config.confidence_threshold
        )

    def fuse_detections(
        self,
        detection_inputs: List[FusionInput],
        image_shape: Tuple[int, int],
        ground_truth: Optional[Dict] = None
    ) -> FusionResult:
        """
        Main method untuk fusing multiple detection results

        Args:
            detection_inputs: List detection results dari different methods
            image_shape: Shape original image
            ground_truth: Optional ground truth untuk validation

        Returns:
            FusionResult object
        """
        start_time = time.time()

        try:
            # 1. Validate inputs
            valid_inputs = self._validate_inputs(detection_inputs)

            if not valid_inputs:
                return self._create_failed_result(
                    "No valid detection inputs",
                    time.time() - start_time
                )

            # 2. Normalize dan weight detection results
            normalized_inputs = self._normalize_detection_results(valid_inputs)

            # 3. Calculate consensus coordinates
            consensus_coords = self._calculate_consensus_coordinates(normalized_inputs)

            # 4. Calculate consensus confidence
            consensus_confidence = self._calculate_consensus_confidence(normalized_inputs)

            # 5. Quantify uncertainty
            uncertainty_bounds = self._quantify_uncertainty(normalized_inputs, consensus_coords)

            # 6. Analyze method agreements
            method_agreements = self._analyze_method_agreements(normalized_inputs, consensus_coords)

            # 7. Calculate consensus score
            consensus_score = self._calculate_consensus_score(
                normalized_inputs, consensus_coords, method_agreements
            )

            # 8. Quality assessment
            quality_metrics = None
            if consensus_coords:
                quality_metrics = self.quality_assessor.assess_detection_quality(
                    {
                        'grid_coordinates': consensus_coords,
                        'confidence': consensus_confidence,
                        'method': 'fusion'
                    },
                    ground_truth,
                    image_shape
                )

            # 9. Final validation
            validation_score = self._validate_fusion_result(
                consensus_coords, consensus_confidence, consensus_score, quality_metrics
            )

            processing_time = time.time() - start_time

            # Extract contributing methods
            contributing_methods = [inp.method_name for inp in normalized_inputs
                                  if inp.result.grid_coordinates is not None]

            return FusionResult(
                grid_coordinates=consensus_coords,
                confidence=consensus_confidence,
                consensus_score=consensus_score,
                uncertainty_bounds=uncertainty_bounds,
                contributing_methods=contributing_methods,
                method_agreements=method_agreements,
                quality_metrics=quality_metrics,
                processing_time=processing_time,
                validation_score=validation_score,
                individual_results={
                    inp.method_name: {
                        'coordinates': inp.result.grid_coordinates,
                        'confidence': inp.result.confidence,
                        'weight': inp.weight
                    } for inp in normalized_inputs
                }
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error dalam detection fusion: {str(e)}")

            return self._create_failed_result(str(e), processing_time)

    def _validate_inputs(self, detection_inputs: List[FusionInput]) -> List[FusionInput]:
        """Validate detection inputs"""

        valid_inputs = []

        for inp in detection_inputs:
            # Check if result exists dan has required attributes
            if not hasattr(inp.result, 'grid_coordinates'):
                logger.warning(f"Invalid result dari {inp.method_name}: missing grid_coordinates")
                continue

            if not hasattr(inp.result, 'confidence'):
                logger.warning(f"Invalid result dari {inp.method_name}: missing confidence")
                continue

            # Check confidence threshold
            if inp.result.confidence < self.config.confidence_threshold:
                logger.debug(f"Low confidence hasil dari {inp.method_name}: {inp.result.confidence:.3f}")
                continue

            valid_inputs.append(inp)

        logger.debug(f"Validated inputs: {len(valid_inputs)}/{len(detection_inputs)}")
        return valid_inputs

    def _normalize_detection_results(self, inputs: List[FusionInput]) -> List[FusionInput]:
        """Normalize detection results untuk consistent processing"""

        normalized_inputs = []

        for inp in inputs:
            # Normalize confidence scores
            normalized_confidence = min(1.0, max(0.0, inp.result.confidence))

            # Apply quality-based weighting
            quality_adjusted_weight = inp.weight * inp.preprocessing_quality

            # Create normalized input
            normalized_result = inp.result
            normalized_result.confidence = normalized_confidence

            normalized_input = FusionInput(
                method_name=inp.method_name,
                result=normalized_result,
                weight=quality_adjusted_weight,
                preprocessing_quality=inp.preprocessing_quality
            )

            normalized_inputs.append(normalized_input)

        return normalized_inputs

    def _calculate_consensus_coordinates(
        self,
        inputs: List[FusionInput]
    ) -> Optional[Tuple[int, int, int, int]]:
        """Calculate consensus coordinates menggunakan weighted voting"""

        valid_coords = []
        weights = []

        for inp in inputs:
            if inp.result.grid_coordinates is not None:
                valid_coords.append(inp.result.grid_coordinates)
                # Combined weight dari method weight, confidence, dan quality
                combined_weight = (
                    inp.weight * 0.5 +
                    inp.result.confidence * 0.3 +
                    inp.preprocessing_quality * 0.2
                )
                weights.append(combined_weight)

        if not valid_coords:
            return None

        if len(valid_coords) == 1:
            return valid_coords[0]

        # Apply outlier rejection if configured
        if self.config.outlier_rejection_method == 'RANSAC' and len(valid_coords) >= 3:
            filtered_coords, filtered_weights = self._apply_ransac_filtering(
                valid_coords, weights
            )
        else:
            filtered_coords, filtered_weights = valid_coords, weights

        # Calculate weighted average coordinates
        if not filtered_coords:
            return None

        coords_array = np.array(filtered_coords)
        weights_array = np.array(filtered_weights)

        # Normalize weights
        weights_normalized = weights_array / np.sum(weights_array)

        # Weighted average
        weighted_coords = np.average(coords_array, axis=0, weights=weights_normalized)

        # Round to integer coordinates
        consensus_coords = tuple(int(coord) for coord in weighted_coords)

        logger.debug(f"Consensus coordinates dari {len(filtered_coords)} detections: {consensus_coords}")
        return consensus_coords

    def _apply_ransac_filtering(
        self,
        coordinates: List[Tuple[int, int, int, int]],
        weights: List[float]
    ) -> Tuple[List[Tuple[int, int, int, int]], List[float]]:
        """Apply RANSAC-based outlier rejection"""

        if len(coordinates) < 3:
            return coordinates, weights

        # Convert coordinates to points for clustering
        points = []
        for x1, y1, x2, y2 in coordinates:
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            width = x2 - x1
            height = y2 - y1
            points.append([center_x, center_y, width, height])

        points_array = np.array(points)

        # Use DBSCAN untuk identify outliers
        # Scale features untuk uniform clustering
        scaled_points = points_array / np.max(points_array, axis=0)

        clustering = DBSCAN(eps=0.3, min_samples=2).fit(scaled_points)
        labels = clustering.labels_

        # Find largest cluster (consensus group)
        unique_labels, counts = np.unique(labels[labels >= 0], return_counts=True)

        if len(unique_labels) == 0:
            # No clusters found, return original
            return coordinates, weights

        largest_cluster_label = unique_labels[np.argmax(counts)]
        inlier_indices = np.where(labels == largest_cluster_label)[0]

        # Filter coordinates dan weights
        filtered_coords = [coordinates[i] for i in inlier_indices]
        filtered_weights = [weights[i] for i in inlier_indices]

        logger.debug(f"RANSAC filtering: {len(coordinates)} -> {len(filtered_coords)} coordinates")
        return filtered_coords, filtered_weights

    def _calculate_consensus_confidence(self, inputs: List[FusionInput]) -> float:
        """Calculate consensus confidence score"""

        if not inputs:
            return 0.0

        confidence_factors = []

        # 1. Weighted average confidence
        confidences = [inp.result.confidence for inp in inputs if inp.result.grid_coordinates is not None]
        method_weights = [inp.weight for inp in inputs if inp.result.grid_coordinates is not None]

        if confidences and method_weights:
            weighted_avg_confidence = np.average(confidences, weights=method_weights)
            confidence_factors.append(weighted_avg_confidence * 0.4)

        # 2. Method consensus bonus
        num_agreeing_methods = len([inp for inp in inputs if inp.result.grid_coordinates is not None])
        total_methods = len(inputs)

        consensus_bonus = num_agreeing_methods / total_methods
        confidence_factors.append(consensus_bonus * 0.3)

        # 3. Quality consistency bonus
        qualities = [inp.preprocessing_quality for inp in inputs]
        if qualities:
            quality_consistency = 1.0 - np.std(qualities) / max(np.mean(qualities), 0.1)
            confidence_factors.append(quality_consistency * 0.2)

        # 4. Confidence variance penalty
        if len(confidences) > 1:
            confidence_variance = np.var(confidences)
            variance_penalty = max(0.0, 1.0 - confidence_variance * 2)
            confidence_factors.append(variance_penalty * 0.1)

        final_confidence = sum(confidence_factors) if confidence_factors else 0.0
        return min(1.0, final_confidence)

    def _quantify_uncertainty(
        self,
        inputs: List[FusionInput],
        consensus_coords: Optional[Tuple[int, int, int, int]]
    ) -> Tuple[float, float]:
        """Quantify uncertainty dalam consensus result"""

        if not consensus_coords or not inputs:
            return (0.0, 0.0)

        # Calculate coordinate variations
        valid_coords = [inp.result.grid_coordinates for inp in inputs
                       if inp.result.grid_coordinates is not None]

        if len(valid_coords) <= 1:
            # Single detection - use confidence-based uncertainty
            confidence = inputs[0].result.confidence if inputs else 0.0
            uncertainty = (1.0 - confidence) * 0.1
            return (max(0.0, confidence - uncertainty), min(1.0, confidence + uncertainty))

        # Calculate coordinate deviations
        coords_array = np.array(valid_coords)
        consensus_array = np.array(consensus_coords)

        # Calculate distances dari consensus
        distances = []
        for coords in valid_coords:
            coord_array = np.array(coords)
            distance = np.linalg.norm(coord_array - consensus_array)
            distances.append(distance)

        # Statistical uncertainty quantification
        mean_distance = np.mean(distances)
        std_distance = np.std(distances)

        # Convert to confidence uncertainty
        max_reasonable_distance = 100  # pixels
        normalized_uncertainty = min(1.0, (mean_distance + std_distance) / max_reasonable_distance)

        # Calculate confidence interval
        base_confidence = self._calculate_consensus_confidence(inputs)
        uncertainty_margin = normalized_uncertainty * 0.2

        lower_bound = max(0.0, base_confidence - uncertainty_margin)
        upper_bound = min(1.0, base_confidence + uncertainty_margin)

        return (lower_bound, upper_bound)

    def _analyze_method_agreements(
        self,
        inputs: List[FusionInput],
        consensus_coords: Optional[Tuple[int, int, int, int]]
    ) -> Dict[str, float]:
        """Analyze agreements antara different detection methods"""

        agreements = {}

        if not consensus_coords:
            return {inp.method_name: 0.0 for inp in inputs}

        consensus_array = np.array(consensus_coords)

        for inp in inputs:
            if inp.result.grid_coordinates is not None:
                coord_array = np.array(inp.result.grid_coordinates)

                # Calculate agreement berdasarkan coordinate similarity
                distance = np.linalg.norm(coord_array - consensus_array)
                max_distance = 100  # pixels

                # Agreement score (higher = better agreement)
                agreement = max(0.0, 1.0 - distance / max_distance)

                # Factor dalam confidence
                confidence_weighted_agreement = (
                    agreement * 0.7 + inp.result.confidence * 0.3
                )

                agreements[inp.method_name] = confidence_weighted_agreement
            else:
                agreements[inp.method_name] = 0.0

        return agreements

    def _calculate_consensus_score(
        self,
        inputs: List[FusionInput],
        consensus_coords: Optional[Tuple[int, int, int, int]],
        method_agreements: Dict[str, float]
    ) -> float:
        """Calculate overall consensus score untuk fusion quality"""

        if not consensus_coords:
            return 0.0

        score_factors = []

        # 1. Number of contributing methods
        contributing_count = len([inp for inp in inputs if inp.result.grid_coordinates is not None])
        contribution_score = min(1.0, contributing_count / 3)  # Normalize by expected 3 methods
        score_factors.append(contribution_score * 0.3)

        # 2. Average method agreement
        if method_agreements:
            avg_agreement = np.mean(list(method_agreements.values()))
            score_factors.append(avg_agreement * 0.3)

        # 3. Confidence consistency
        confidences = [inp.result.confidence for inp in inputs if inp.result.grid_coordinates is not None]
        if len(confidences) > 1:
            confidence_std = np.std(confidences)
            consistency_score = max(0.0, 1.0 - confidence_std)
            score_factors.append(consistency_score * 0.2)
        elif len(confidences) == 1:
            score_factors.append(confidences[0] * 0.2)

        # 4. Weight distribution balance
        weights = [inp.weight for inp in inputs if inp.result.grid_coordinates is not None]
        if weights:
            weight_entropy = -np.sum([w * np.log(w + 1e-8) for w in weights if w > 0])
            max_entropy = np.log(len(weights))
            balance_score = weight_entropy / max_entropy if max_entropy > 0 else 1.0
            score_factors.append(balance_score * 0.2)

        consensus_score = sum(score_factors)
        return min(1.0, consensus_score)

    def _validate_fusion_result(
        self,
        consensus_coords: Optional[Tuple[int, int, int, int]],
        consensus_confidence: float,
        consensus_score: float,
        quality_metrics: Optional[DetectionQualityMetrics]
    ) -> float:
        """Validate fusion result quality"""

        if not consensus_coords:
            return 0.0

        validation_checks = []

        # 1. Consensus confidence validation
        confidence_score = consensus_confidence
        validation_checks.append(confidence_score * 0.3)

        # 2. Consensus score validation
        validation_checks.append(consensus_score * 0.3)

        # 3. Quality metrics validation
        if quality_metrics:
            quality_score = quality_metrics.overall_quality
            validation_checks.append(quality_score * 0.3)
        else:
            validation_checks.append(0.5 * 0.3)  # Neutral score

        # 4. Coordinate reasonableness
        x1, y1, x2, y2 = consensus_coords
        if x1 < x2 and y1 < y2 and all(coord >= 0 for coord in consensus_coords):
            coord_score = 1.0
        else:
            coord_score = 0.0
        validation_checks.append(coord_score * 0.1)

        validation_score = sum(validation_checks)
        return min(1.0, validation_score)

    def _create_failed_result(self, error_message: str, processing_time: float) -> FusionResult:
        """Create failed fusion result"""

        return FusionResult(
            grid_coordinates=None,
            confidence=0.0,
            consensus_score=0.0,
            uncertainty_bounds=(0.0, 0.0),
            contributing_methods=[],
            method_agreements={},
            quality_metrics=None,
            processing_time=processing_time,
            error_message=error_message
        )

    def create_fusion_input(
        self,
        method_name: str,
        detection_result: Union[ContourDetectionResult, HoughDetectionResult, TemplateDetectionResult],
        weight: Optional[float] = None,
        preprocessing_quality: float = 1.0
    ) -> FusionInput:
        """Create fusion input dari detection result"""

        # Use default weights if not provided
        if weight is None:
            default_weights = self.config.consensus_weights
            weight = default_weights.get(method_name, 0.33)

        return FusionInput(
            method_name=method_name,
            result=detection_result,
            weight=weight,
            preprocessing_quality=preprocessing_quality
        )

    def adaptive_fusion(
        self,
        detection_inputs: List[FusionInput],
        image_shape: Tuple[int, int],
        adaptation_strategy: str = "quality_based"
    ) -> FusionResult:
        """
        Adaptive fusion dengan dynamic weight adjustment

        Args:
            detection_inputs: Detection inputs
            image_shape: Image shape
            adaptation_strategy: Strategy untuk weight adaptation

        Returns:
            FusionResult dengan adapted weights
        """

        # Adapt weights berdasarkan strategy
        adapted_inputs = self._adapt_weights(detection_inputs, adaptation_strategy)

        # Perform fusion dengan adapted weights
        return self.fuse_detections(adapted_inputs, image_shape)

    def _adapt_weights(
        self,
        inputs: List[FusionInput],
        strategy: str
    ) -> List[FusionInput]:
        """Adapt weights berdasarkan specified strategy"""

        if strategy == "quality_based":
            # Adjust weights berdasarkan preprocessing quality
            total_quality = sum(inp.preprocessing_quality for inp in inputs)

            adapted_inputs = []
            for inp in inputs:
                if total_quality > 0:
                    quality_ratio = inp.preprocessing_quality / total_quality
                    adapted_weight = inp.weight * (1.0 + quality_ratio)
                else:
                    adapted_weight = inp.weight

                adapted_input = FusionInput(
                    method_name=inp.method_name,
                    result=inp.result,
                    weight=adapted_weight,
                    preprocessing_quality=inp.preprocessing_quality
                )
                adapted_inputs.append(adapted_input)

            return adapted_inputs

        elif strategy == "confidence_based":
            # Adjust weights berdasarkan detection confidence
            confidences = [inp.result.confidence for inp in inputs if inp.result.confidence > 0]
            total_confidence = sum(confidences) if confidences else 1.0

            adapted_inputs = []
            for inp in inputs:
                if inp.result.confidence > 0 and total_confidence > 0:
                    confidence_ratio = inp.result.confidence / total_confidence
                    adapted_weight = inp.weight * (1.0 + confidence_ratio)
                else:
                    adapted_weight = inp.weight * 0.5  # Penalize low confidence

                adapted_input = FusionInput(
                    method_name=inp.method_name,
                    result=inp.result,
                    weight=adapted_weight,
                    preprocessing_quality=inp.preprocessing_quality
                )
                adapted_inputs.append(adapted_input)

            return adapted_inputs

        else:
            # No adaptation - return original inputs
            return inputs