"""
Template Matching Multi-Scale untuk Template Detection system
Multi-scale template matching dengan rotation handling untuk robust grid detection
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
import time
from pathlib import Path
import json

from ..config import TemplateMatchingConfig
from ..utils.quality_assessment import QualityAssessment

logger = logging.getLogger(__name__)


@dataclass
class TemplateMatchResult:
    """Data structure untuk single template match result"""
    match_value: float
    location: Tuple[int, int]
    scale: float
    rotation: float
    template_type: str
    confidence: float


@dataclass
class TemplateDetectionResult:
    """Data structure untuk template matching detection results"""
    grid_coordinates: Optional[Tuple[int, int, int, int]]
    confidence: float
    best_match: Optional[TemplateMatchResult]
    all_matches: List[TemplateMatchResult]
    template_type: Optional[str]
    processing_time: float
    method: str = "template"
    validation_score: float = 0.0
    error_message: Optional[str] = None


class TemplateMatchingDetector:
    """Multi-scale template matching detector dengan rotation invariance"""

    def __init__(self, config: TemplateMatchingConfig):
        """
        Initialize template matching detector

        Args:
            config: Configuration untuk template matching parameters
        """
        self.config = config
        self.quality_assessor = QualityAssessment()
        self.templates = {}
        self.template_cache = {}

        # Initialize templates
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize template database dengan different grid types"""

        # Create synthetic OMR grid templates
        for template_type in self.config.template_types:
            template = self._create_omr_template(template_type)
            if template is not None:
                self.templates[template_type] = template
                logger.debug(f"Created template for {template_type}")

        logger.info(f"Initialized {len(self.templates)} template types")

    def _create_omr_template(self, template_type: str) -> Optional[np.ndarray]:
        """Create synthetic OMR grid template untuk given type"""

        try:
            # Parse template type (e.g., "3x20" -> 3 rows, 20 columns)
            if 'x' not in template_type:
                return None

            rows_str, cols_str = template_type.split('x')
            rows = int(rows_str)
            cols = int(cols_str)

            # Template dimensions (scaled untuk reasonable size)
            cell_width = 20
            cell_height = 20
            line_thickness = 2

            template_width = cols * cell_width + (cols + 1) * line_thickness
            template_height = rows * cell_height + (rows + 1) * line_thickness

            # Create blank template
            template = np.zeros((template_height, template_width), dtype=np.uint8)

            # Draw grid lines
            # Horizontal lines
            for i in range(rows + 1):
                y = i * (cell_height + line_thickness)
                cv2.line(template, (0, y), (template_width - 1, y), 255, line_thickness)

            # Vertical lines
            for j in range(cols + 1):
                x = j * (cell_width + line_thickness)
                cv2.line(template, (x, 0), (x, template_height - 1), 255, line_thickness)

            return template

        except ValueError as e:
            logger.error(f"Error creating template untuk {template_type}: {str(e)}")
            return None

    def detect_grid(
        self,
        image: np.ndarray,
        preprocessing_params: Optional[Dict] = None
    ) -> TemplateDetectionResult:
        """
        Main method untuk detecting grid menggunakan template matching

        Args:
            image: Input image (grayscale atau color)
            preprocessing_params: Optional preprocessing parameters

        Returns:
            TemplateDetectionResult object
        """
        start_time = time.time()

        try:
            # 1. Preprocessing
            processed_image = self._preprocess_image(image, preprocessing_params)

            # 2. Multi-scale Template Matching untuk each template type
            all_matches = []
            for template_type, template in self.templates.items():
                matches = self._match_template_multiscale(
                    processed_image, template, template_type
                )
                all_matches.extend(matches)

            # 3. Filter dan rank matches
            filtered_matches = self._filter_and_rank_matches(all_matches, image.shape)

            # 4. Select best match
            best_match = self._select_best_match(filtered_matches, image.shape)

            # 5. Extract grid coordinates
            grid_coords = None
            if best_match:
                grid_coords = self._extract_grid_coordinates(best_match, image.shape)

            # 6. Validation
            validation_score = self._validate_detection(best_match, grid_coords, image.shape)

            # 7. Calculate confidence
            confidence = self._calculate_confidence(best_match, filtered_matches, validation_score)

            processing_time = time.time() - start_time

            return TemplateDetectionResult(
                grid_coordinates=grid_coords,
                confidence=confidence,
                best_match=best_match,
                all_matches=filtered_matches,
                template_type=best_match.template_type if best_match else None,
                processing_time=processing_time,
                validation_score=validation_score
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error dalam template matching: {str(e)}")

            return TemplateDetectionResult(
                grid_coordinates=None,
                confidence=0.0,
                best_match=None,
                all_matches=[],
                template_type=None,
                processing_time=processing_time,
                error_message=str(e)
            )

    def _preprocess_image(
        self,
        image: np.ndarray,
        preprocessing_params: Optional[Dict] = None
    ) -> np.ndarray:
        """Preprocess image untuk optimal template matching"""

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Apply preprocessing parameters
        if preprocessing_params:
            blur_kernel = preprocessing_params.get('blur_kernel', 3)
            enhance_contrast = preprocessing_params.get('enhance_contrast', True)
        else:
            blur_kernel = 3
            enhance_contrast = True

        # Light gaussian blur untuk noise reduction
        if blur_kernel > 1:
            processed = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
        else:
            processed = gray.copy()

        # Contrast enhancement for better template matching
        if enhance_contrast:
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            processed = clahe.apply(processed)

        return processed

    def _match_template_multiscale(
        self,
        image: np.ndarray,
        template: np.ndarray,
        template_type: str
    ) -> List[TemplateMatchResult]:
        """Perform multi-scale template matching dengan rotation handling"""

        matches = []

        # Scale range
        scale_min, scale_max = self.config.scale_range
        scale_step = self.config.scale_step

        # Rotation range
        rot_min, rot_max = self.config.rotation_range
        rot_step = self.config.rotation_step

        scales = np.arange(scale_min, scale_max + scale_step, scale_step)
        rotations = np.arange(rot_min, rot_max + rot_step, rot_step)

        for scale in scales:
            for rotation in rotations:
                # Transform template
                transformed_template = self._transform_template(template, scale, rotation)

                if transformed_template is None:
                    continue

                # Check if template fits dalam image
                if (transformed_template.shape[0] >= image.shape[0] or
                    transformed_template.shape[1] >= image.shape[1]):
                    continue

                # Perform template matching
                result = cv2.matchTemplate(
                    image,
                    transformed_template,
                    getattr(cv2, self.config.correlation_method)
                )

                # Find best match location
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                # Use appropriate location berdasarkan matching method
                if self.config.correlation_method in ['TM_SQDIFF', 'TM_SQDIFF_NORMED']:
                    match_val = 1.0 - min_val if 'NORMED' in self.config.correlation_method else -min_val
                    location = min_loc
                else:
                    match_val = max_val
                    location = max_loc

                # Calculate confidence untuk this match
                confidence = self._calculate_match_confidence(match_val, scale, rotation)

                # Only keep matches above threshold
                if match_val >= self.config.match_threshold:
                    matches.append(TemplateMatchResult(
                        match_value=match_val,
                        location=location,
                        scale=scale,
                        rotation=rotation,
                        template_type=template_type,
                        confidence=confidence
                    ))

        logger.debug(f"Template {template_type}: {len(matches)} matches found")
        return matches

    def _transform_template(
        self,
        template: np.ndarray,
        scale: float,
        rotation: float
    ) -> Optional[np.ndarray]:
        """Transform template dengan scaling dan rotation"""

        try:
            h, w = template.shape[:2]

            # Apply scaling
            if scale != 1.0:
                new_w = int(w * scale)
                new_h = int(h * scale)
                if new_w <= 0 or new_h <= 0:
                    return None
                scaled_template = cv2.resize(template, (new_w, new_h))
            else:
                scaled_template = template.copy()

            # Apply rotation
            if abs(rotation) > 0.1:  # Only rotate if significant
                h_rot, w_rot = scaled_template.shape[:2]
                center = (w_rot // 2, h_rot // 2)

                # Get rotation matrix
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)

                # Calculate new dimensions
                cos_val = abs(rotation_matrix[0, 0])
                sin_val = abs(rotation_matrix[0, 1])
                new_w = int((h_rot * sin_val) + (w_rot * cos_val))
                new_h = int((h_rot * cos_val) + (w_rot * sin_val))

                # Adjust translation
                rotation_matrix[0, 2] += (new_w / 2) - center[0]
                rotation_matrix[1, 2] += (new_h / 2) - center[1]

                # Apply rotation
                rotated_template = cv2.warpAffine(
                    scaled_template,
                    rotation_matrix,
                    (new_w, new_h),
                    borderValue=0
                )
                return rotated_template
            else:
                return scaled_template

        except Exception as e:
            logger.warning(f"Error transforming template: {str(e)}")
            return None

    def _calculate_match_confidence(
        self,
        match_value: float,
        scale: float,
        rotation: float
    ) -> float:
        """Calculate confidence score untuk individual match"""

        confidence_factors = []

        # 1. Match value confidence
        if self.config.correlation_method in ['TM_CCOEFF_NORMED', 'TM_CCORR_NORMED']:
            # Normalized methods: higher values are better
            match_confidence = match_value
        else:
            # Non-normalized methods: scale appropriately
            match_confidence = min(1.0, match_value / 1000000)  # Rough scaling

        confidence_factors.append(match_confidence * 0.6)

        # 2. Scale confidence (prefer scales close to 1.0)
        scale_deviation = abs(scale - 1.0)
        scale_confidence = max(0.0, 1.0 - scale_deviation)
        confidence_factors.append(scale_confidence * 0.2)

        # 3. Rotation confidence (prefer small rotations)
        rotation_deviation = abs(rotation) / 20.0  # Normalize by max rotation
        rotation_confidence = max(0.0, 1.0 - rotation_deviation)
        confidence_factors.append(rotation_confidence * 0.2)

        return sum(confidence_factors)

    def _filter_and_rank_matches(
        self,
        matches: List[TemplateMatchResult],
        image_shape: Tuple[int, int]
    ) -> List[TemplateMatchResult]:
        """Filter dan rank matches berdasarkan quality criteria"""

        if not matches:
            return []

        filtered_matches = []

        for match in matches:
            # 1. Location validation
            x, y = match.location
            if not (0 <= x < image_shape[1] and 0 <= y < image_shape[0]):
                continue

            # 2. Match value threshold
            if match.match_value < self.config.match_threshold:
                continue

            # 3. Scale reasonableness
            if not (0.5 <= match.scale <= 2.0):
                continue

            # 4. Rotation reasonableness
            if abs(match.rotation) > 30:  # More than 30 degrees is unusual
                continue

            filtered_matches.append(match)

        # Sort by confidence (highest first)
        filtered_matches.sort(key=lambda x: x.confidence, reverse=True)

        # Non-maximum suppression untuk remove overlapping matches
        suppressed_matches = self._non_maximum_suppression(filtered_matches, image_shape)

        logger.debug(f"Filtered matches: {len(matches)} -> {len(filtered_matches)} -> {len(suppressed_matches)}")
        return suppressed_matches

    def _non_maximum_suppression(
        self,
        matches: List[TemplateMatchResult],
        image_shape: Tuple[int, int],
        overlap_threshold: float = 0.3
    ) -> List[TemplateMatchResult]:
        """Apply non-maximum suppression untuk remove overlapping detections"""

        if not matches:
            return []

        # Sort by confidence
        sorted_matches = sorted(matches, key=lambda x: x.confidence, reverse=True)
        suppressed_matches = []

        for current_match in sorted_matches:
            # Check overlap dengan already selected matches
            is_overlapping = False

            for selected_match in suppressed_matches:
                overlap = self._calculate_match_overlap(current_match, selected_match)
                if overlap > overlap_threshold:
                    is_overlapping = True
                    break

            if not is_overlapping:
                suppressed_matches.append(current_match)

        return suppressed_matches

    def _calculate_match_overlap(
        self,
        match1: TemplateMatchResult,
        match2: TemplateMatchResult
    ) -> float:
        """Calculate overlap antara two template matches"""

        # Estimate template sizes berdasarkan type dan scale
        size1 = self._estimate_template_size(match1.template_type, match1.scale)
        size2 = self._estimate_template_size(match2.template_type, match2.scale)

        if not size1 or not size2:
            return 0.0

        # Calculate bounding boxes
        x1, y1 = match1.location
        w1, h1 = size1
        box1 = (x1, y1, x1 + w1, y1 + h1)

        x2, y2 = match2.location
        w2, h2 = size2
        box2 = (x2, y2, x2 + w2, y2 + h2)

        # Calculate intersection
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])

        if x_right <= x_left or y_bottom <= y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)

        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    def _estimate_template_size(self, template_type: str, scale: float) -> Optional[Tuple[int, int]]:
        """Estimate template size berdasarkan type dan scale"""

        if template_type in self.templates:
            original_template = self.templates[template_type]
            h, w = original_template.shape[:2]
            scaled_w = int(w * scale)
            scaled_h = int(h * scale)
            return (scaled_w, scaled_h)

        return None

    def _select_best_match(
        self,
        matches: List[TemplateMatchResult],
        image_shape: Tuple[int, int]
    ) -> Optional[TemplateMatchResult]:
        """Select best match dari filtered candidates"""

        if not matches:
            return None

        # Additional scoring untuk final selection
        scored_matches = []

        for match in matches:
            additional_score = self._calculate_additional_match_score(match, image_shape)
            total_score = match.confidence * 0.7 + additional_score * 0.3
            scored_matches.append((match, total_score))

        # Sort by total score
        scored_matches.sort(key=lambda x: x[1], reverse=True)

        best_match = scored_matches[0][0]
        logger.debug(f"Selected best match: {best_match.template_type} "
                    f"(confidence: {best_match.confidence:.3f})")

        return best_match

    def _calculate_additional_match_score(
        self,
        match: TemplateMatchResult,
        image_shape: Tuple[int, int]
    ) -> float:
        """Calculate additional scoring factors untuk match selection"""

        score_factors = []

        # 1. Position score (prefer central locations)
        x, y = match.location
        h, w = image_shape[:2]
        center_x, center_y = w // 2, h // 2

        distance_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        position_score = 1.0 - (distance_from_center / max_distance)
        score_factors.append(position_score * 0.3)

        # 2. Scale preference (prefer scale close to 1.0)
        scale_score = 1.0 - abs(match.scale - 1.0)
        score_factors.append(scale_score * 0.3)

        # 3. Template type preference (some types more common)
        type_preferences = {
            '3x20': 1.0,
            '4x15': 0.9,
            '5x12': 0.8
        }
        type_score = type_preferences.get(match.template_type, 0.7)
        score_factors.append(type_score * 0.2)

        # 4. Rotation preference (prefer minimal rotation)
        rotation_score = 1.0 - abs(match.rotation) / 20.0
        score_factors.append(rotation_score * 0.2)

        return sum(score_factors)

    def _extract_grid_coordinates(
        self,
        best_match: TemplateMatchResult,
        image_shape: Tuple[int, int]
    ) -> Optional[Tuple[int, int, int, int]]:
        """Extract grid coordinates dari best template match"""

        if not best_match:
            return None

        x, y = best_match.location
        template_size = self._estimate_template_size(
            best_match.template_type,
            best_match.scale
        )

        if not template_size:
            return None

        w, h = template_size

        # Validate coordinates
        img_h, img_w = image_shape[:2]
        if x + w > img_w or y + h > img_h:
            # Adjust if template extends beyond image
            w = min(w, img_w - x)
            h = min(h, img_h - y)

        return (x, y, x + w, y + h)

    def _validate_detection(
        self,
        best_match: Optional[TemplateMatchResult],
        grid_coords: Optional[Tuple[int, int, int, int]],
        image_shape: Tuple[int, int]
    ) -> float:
        """Validate detection quality"""

        if not best_match or not grid_coords:
            return 0.0

        validation_checks = []

        # 1. Match quality validation
        match_quality = best_match.confidence
        validation_checks.append(match_quality)

        # 2. Grid size validation
        x1, y1, x2, y2 = grid_coords
        grid_width = x2 - x1
        grid_height = y2 - y1
        img_h, img_w = image_shape[:2]

        area_ratio = (grid_width * grid_height) / (img_w * img_h)
        if 0.1 <= area_ratio <= 0.8:
            size_score = 1.0
        elif 0.05 <= area_ratio <= 0.9:
            size_score = 0.7
        else:
            size_score = 0.3
        validation_checks.append(size_score)

        # 3. Position validation
        margin_x = min(x1, img_w - x2) / img_w
        margin_y = min(y1, img_h - y2) / img_h
        position_score = min(1.0, (margin_x + margin_y) * 2)
        validation_checks.append(position_score)

        # 4. Template type validation
        template_type = best_match.template_type
        if template_type in ['3x20', '4x15', '5x12']:
            type_score = 1.0
        else:
            type_score = 0.7
        validation_checks.append(type_score)

        return np.mean(validation_checks)

    def _calculate_confidence(
        self,
        best_match: Optional[TemplateMatchResult],
        all_matches: List[TemplateMatchResult],
        validation_score: float
    ) -> float:
        """Calculate final confidence score untuk template detection"""

        if not best_match:
            return 0.0

        confidence_factors = []

        # 1. Best match confidence
        confidence_factors.append(best_match.confidence * 0.4)

        # 2. Validation score
        confidence_factors.append(validation_score * 0.3)

        # 3. Match uniqueness (how much better than alternatives)
        if len(all_matches) > 1:
            sorted_matches = sorted(all_matches, key=lambda x: x.confidence, reverse=True)
            second_best_conf = sorted_matches[1].confidence
            uniqueness = (best_match.confidence - second_best_conf) / best_match.confidence
            uniqueness_score = min(1.0, uniqueness * 2)
        else:
            uniqueness_score = 0.8  # Single match gets good uniqueness score

        confidence_factors.append(uniqueness_score * 0.2)

        # 4. Template quality
        template_quality = best_match.match_value
        if template_quality >= 0.8:
            quality_score = 1.0
        elif template_quality >= 0.6:
            quality_score = 0.8
        else:
            quality_score = 0.6
        confidence_factors.append(quality_score * 0.1)

        final_confidence = sum(confidence_factors)
        return min(1.0, final_confidence)

    def save_templates(self, directory: Union[str, Path]) -> None:
        """Save generated templates ke disk untuk reuse"""

        directory = Path(directory)
        directory.mkdir(exist_ok=True)

        for template_type, template in self.templates.items():
            template_path = directory / f"template_{template_type}.png"
            cv2.imwrite(str(template_path), template)

        logger.info(f"Saved {len(self.templates)} templates to {directory}")

    def load_templates(self, directory: Union[str, Path]) -> None:
        """Load templates dari disk"""

        directory = Path(directory)
        if not directory.exists():
            logger.warning(f"Template directory tidak ditemukan: {directory}")
            return

        loaded_count = 0
        for template_file in directory.glob("template_*.png"):
            template_type = template_file.stem.replace("template_", "")
            template = cv2.imread(str(template_file), cv2.IMREAD_GRAYSCALE)

            if template is not None:
                self.templates[template_type] = template
                loaded_count += 1

        logger.info(f"Loaded {loaded_count} templates dari {directory}")