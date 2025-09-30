"""
Week 6 - Template Detection & Segmentation
Bubble Detection Module

Modul ini mengimplementasikan algoritma deteksi bubble dalam sel jawaban
untuk sistem OMR (Optical Mark Recognition). Fokus pada deteksi bubble
yang terisi dan kosong menggunakan teknik computer vision.

Author: Week 6 Implementation
Date: 2024-09-29
Academic Context: Digital Image Processing Course
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

from ..config import ProcessingConfig
from ..utils.quality_assessment import QualityAssessment

@dataclass
class BubbleRegion:
    """Data class untuk menyimpan informasi region bubble"""
    center: Tuple[int, int]
    radius: int
    filled_ratio: float
    confidence: float
    contour: np.ndarray
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    quality_score: float

@dataclass
class BubbleDetectionResult:
    """Result dari proses bubble detection"""
    bubbles: List[BubbleRegion]
    grid_quality: float
    detection_confidence: float
    processing_time: float
    metadata: Dict[str, Any]

class BubbleDetector:
    """
    Kelas untuk mendeteksi bubble dalam sel jawaban OMR

    Menggunakan kombinasi teknik:
    1. Template-based detection untuk mencari pola bubble
    2. Contour detection untuk identifikasi bentuk circular/oval
    3. Regional thresholding untuk ekstraksi bubble
    4. Quality assessment untuk validasi hasil
    """

    def __init__(self, config: ProcessingConfig):
        """
        Initialize BubbleDetector

        Args:
            config: Konfigurasi processing parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.quality_assessor = QualityAssessment(config)

        # Parameters untuk bubble detection
        self.min_bubble_radius = config.detection.get('min_bubble_radius', 8)
        self.max_bubble_radius = config.detection.get('max_bubble_radius', 25)
        self.filled_threshold = config.detection.get('filled_threshold', 0.3)
        self.confidence_threshold = config.detection.get('confidence_threshold', 0.6)

    def detect_bubbles_in_cells(self, cells: List[np.ndarray]) -> List[BubbleDetectionResult]:
        """
        Deteksi bubble dalam multiple cells

        Args:
            cells: List of cell images

        Returns:
            List of BubbleDetectionResult untuk setiap cell
        """
        results = []

        for i, cell in enumerate(cells):
            self.logger.info(f"Processing cell {i+1}/{len(cells)}")

            # Detect bubbles in single cell
            result = self.detect_bubbles_in_cell(cell)
            results.append(result)

        return results

    def detect_bubbles_in_cell(self, cell_image: np.ndarray) -> BubbleDetectionResult:
        """
        Deteksi bubble dalam single cell

        Args:
            cell_image: Image dari single cell

        Returns:
            BubbleDetectionResult dengan informasi bubble yang terdeteksi
        """
        import time
        start_time = time.time()

        # Preprocessing cell image
        processed_cell = self._preprocess_cell(cell_image)

        # Multiple detection methods
        template_bubbles = self._template_based_detection(processed_cell)
        contour_bubbles = self._contour_based_detection(processed_cell)
        regional_bubbles = self._regional_thresholding_detection(processed_cell)

        # Fusion of detection results
        fused_bubbles = self._fuse_bubble_detections(
            template_bubbles, contour_bubbles, regional_bubbles, processed_cell
        )

        # Quality assessment
        grid_quality = self._assess_cell_quality(cell_image, fused_bubbles)
        detection_confidence = self._calculate_detection_confidence(fused_bubbles)

        processing_time = time.time() - start_time

        return BubbleDetectionResult(
            bubbles=fused_bubbles,
            grid_quality=grid_quality,
            detection_confidence=detection_confidence,
            processing_time=processing_time,
            metadata={
                'template_count': len(template_bubbles),
                'contour_count': len(contour_bubbles),
                'regional_count': len(regional_bubbles),
                'final_count': len(fused_bubbles),
                'cell_shape': cell_image.shape
            }
        )

    def _preprocess_cell(self, cell_image: np.ndarray) -> np.ndarray:
        """
        Preprocessing untuk cell image sebelum bubble detection

        Args:
            cell_image: Raw cell image

        Returns:
            Preprocessed cell image
        """
        # Convert to grayscale if needed
        if len(cell_image.shape) == 3:
            gray = cv2.cvtColor(cell_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = cell_image.copy()

        # Noise reduction
        denoised = cv2.medianBlur(gray, 3)

        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(denoised)

        # Gaussian blur untuk smoothing
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

        return blurred

    def _template_based_detection(self, cell_image: np.ndarray) -> List[BubbleRegion]:
        """
        Template-based bubble detection menggunakan template matching

        Args:
            cell_image: Preprocessed cell image

        Returns:
            List of detected bubble regions
        """
        bubbles = []

        # Create circular templates dengan berbagai ukuran
        templates = self._create_bubble_templates()

        for template_size, template in templates.items():
            # Template matching
            result = cv2.matchTemplate(cell_image, template, cv2.TM_CCOEFF_NORMED)

            # Find matches above threshold
            locations = np.where(result >= 0.7)

            for pt in zip(*locations[::-1]):
                center_x = pt[0] + template_size // 2
                center_y = pt[1] + template_size // 2
                radius = template_size // 2

                # Calculate filled ratio
                filled_ratio = self._calculate_filled_ratio(
                    cell_image, (center_x, center_y), radius
                )

                # Estimate confidence based on template match
                confidence = result[pt[1], pt[0]]

                # Create dummy contour (circle)
                angles = np.linspace(0, 2*np.pi, 20)
                contour_points = np.array([
                    [center_x + radius * np.cos(angle), center_y + radius * np.sin(angle)]
                    for angle in angles
                ], dtype=np.int32)

                bubble = BubbleRegion(
                    center=(center_x, center_y),
                    radius=radius,
                    filled_ratio=filled_ratio,
                    confidence=confidence,
                    contour=contour_points,
                    bounding_box=(center_x-radius, center_y-radius, 2*radius, 2*radius),
                    quality_score=confidence * (1.0 - abs(filled_ratio - 0.5))
                )

                bubbles.append(bubble)

        return bubbles

    def _contour_based_detection(self, cell_image: np.ndarray) -> List[BubbleRegion]:
        """
        Contour-based detection untuk mencari bentuk circular/oval

        Args:
            cell_image: Preprocessed cell image

        Returns:
            List of detected bubble regions
        """
        bubbles = []

        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            cell_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Filter by area
            area = cv2.contourArea(contour)
            if area < np.pi * self.min_bubble_radius**2 or area > np.pi * self.max_bubble_radius**2:
                continue

            # Check circularity
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.6:  # Threshold untuk circularity
                continue

            # Get bounding circle
            (center_x, center_y), radius = cv2.minEnclosingCircle(contour)
            center_x, center_y = int(center_x), int(center_y)
            radius = int(radius)

            # Validate radius range
            if radius < self.min_bubble_radius or radius > self.max_bubble_radius:
                continue

            # Calculate filled ratio
            filled_ratio = self._calculate_filled_ratio(cell_image, (center_x, center_y), radius)

            # Calculate confidence based on circularity dan size consistency
            confidence = circularity * min(1.0, area / (np.pi * radius**2))

            # Bounding box
            x, y, w, h = cv2.boundingRect(contour)

            bubble = BubbleRegion(
                center=(center_x, center_y),
                radius=radius,
                filled_ratio=filled_ratio,
                confidence=confidence,
                contour=contour,
                bounding_box=(x, y, w, h),
                quality_score=confidence * circularity
            )

            bubbles.append(bubble)

        return bubbles

    def _regional_thresholding_detection(self, cell_image: np.ndarray) -> List[BubbleRegion]:
        """
        Regional thresholding untuk deteksi bubble area

        Args:
            cell_image: Preprocessed cell image

        Returns:
            List of detected bubble regions
        """
        bubbles = []

        # Multiple threshold values
        threshold_values = [100, 120, 140, 160]

        for thresh_val in threshold_values:
            # Binary thresholding
            _, binary = cv2.threshold(cell_image, thresh_val, 255, cv2.THRESH_BINARY_INV)

            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < np.pi * self.min_bubble_radius**2 or area > np.pi * self.max_bubble_radius**2:
                    continue

                # Get center dan radius
                (center_x, center_y), radius = cv2.minEnclosingCircle(contour)
                center_x, center_y = int(center_x), int(center_y)
                radius = int(radius)

                if radius < self.min_bubble_radius or radius > self.max_bubble_radius:
                    continue

                # Calculate filled ratio
                filled_ratio = self._calculate_filled_ratio(cell_image, (center_x, center_y), radius)

                # Confidence based on threshold consistency
                confidence = 1.0 - abs(thresh_val - 130) / 100.0  # Peak at 130
                confidence = max(0.1, confidence)

                # Bounding box
                x, y, w, h = cv2.boundingRect(contour)

                bubble = BubbleRegion(
                    center=(center_x, center_y),
                    radius=radius,
                    filled_ratio=filled_ratio,
                    confidence=confidence,
                    contour=contour,
                    bounding_box=(x, y, w, h),
                    quality_score=confidence * filled_ratio
                )

                bubbles.append(bubble)

        return bubbles

    def _create_bubble_templates(self) -> Dict[int, np.ndarray]:
        """
        Create circular templates untuk template matching

        Returns:
            Dictionary mapping template size to template image
        """
        templates = {}

        for radius in range(self.min_bubble_radius, self.max_bubble_radius + 1, 2):
            size = radius * 2 + 4  # Extra padding
            template = np.zeros((size, size), dtype=np.uint8)

            # Draw filled circle
            cv2.circle(template, (size//2, size//2), radius, 255, -1)

            # Apply gaussian blur untuk smoothing
            template = cv2.GaussianBlur(template, (3, 3), 0)

            templates[size] = template

        return templates

    def _calculate_filled_ratio(self, image: np.ndarray, center: Tuple[int, int], radius: int) -> float:
        """
        Calculate filled ratio dari bubble region

        Args:
            image: Cell image
            center: Center coordinates of bubble
            radius: Radius of bubble

        Returns:
            Filled ratio (0.0 to 1.0)
        """
        # Create circular mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, -1)

        # Calculate pixels dalam circle
        masked_region = cv2.bitwise_and(image, image, mask=mask)
        circle_pixels = masked_region[mask > 0]

        if len(circle_pixels) == 0:
            return 0.0

        # Calculate dark pixels (filled area)
        dark_pixels = np.sum(circle_pixels < 128)
        total_pixels = len(circle_pixels)

        filled_ratio = dark_pixels / total_pixels
        return filled_ratio

    def _fuse_bubble_detections(self, template_bubbles: List[BubbleRegion],
                               contour_bubbles: List[BubbleRegion],
                               regional_bubbles: List[BubbleRegion],
                               cell_image: np.ndarray) -> List[BubbleRegion]:
        """
        Fuse hasil dari multiple detection methods

        Args:
            template_bubbles: Results from template matching
            contour_bubbles: Results from contour detection
            regional_bubbles: Results from regional thresholding
            cell_image: Original cell image

        Returns:
            Fused list of bubble regions
        """
        all_bubbles = template_bubbles + contour_bubbles + regional_bubbles

        if not all_bubbles:
            return []

        # Group bubbles by proximity
        bubble_groups = self._group_bubbles_by_proximity(all_bubbles)

        # Fuse each group
        fused_bubbles = []
        for group in bubble_groups:
            fused_bubble = self._fuse_bubble_group(group)
            if fused_bubble.confidence >= self.confidence_threshold:
                fused_bubbles.append(fused_bubble)

        return fused_bubbles

    def _group_bubbles_by_proximity(self, bubbles: List[BubbleRegion]) -> List[List[BubbleRegion]]:
        """
        Group bubbles berdasarkan kedekatan posisi

        Args:
            bubbles: List of all detected bubbles

        Returns:
            List of bubble groups
        """
        groups = []
        used_indices = set()

        for i, bubble1 in enumerate(bubbles):
            if i in used_indices:
                continue

            group = [bubble1]
            used_indices.add(i)

            for j, bubble2 in enumerate(bubbles):
                if j in used_indices:
                    continue

                # Calculate distance between centers
                dist = np.sqrt((bubble1.center[0] - bubble2.center[0])**2 +
                              (bubble1.center[1] - bubble2.center[1])**2)

                # Group if within threshold
                if dist < max(bubble1.radius, bubble2.radius) * 1.5:
                    group.append(bubble2)
                    used_indices.add(j)

            groups.append(group)

        return groups

    def _fuse_bubble_group(self, group: List[BubbleRegion]) -> BubbleRegion:
        """
        Fuse multiple bubble detections dalam satu group

        Args:
            group: List of bubble regions in the same area

        Returns:
            Single fused bubble region
        """
        if len(group) == 1:
            return group[0]

        # Weighted average berdasarkan confidence
        total_weight = sum(bubble.confidence for bubble in group)

        if total_weight == 0:
            return group[0]

        # Weighted center
        center_x = sum(bubble.center[0] * bubble.confidence for bubble in group) / total_weight
        center_y = sum(bubble.center[1] * bubble.confidence for bubble in group) / total_weight

        # Average radius
        radius = sum(bubble.radius for bubble in group) / len(group)

        # Average filled ratio
        filled_ratio = sum(bubble.filled_ratio for bubble in group) / len(group)

        # Combined confidence
        confidence = total_weight / len(group)

        # Use best contour
        best_bubble = max(group, key=lambda b: b.confidence)

        # Calculate new bounding box
        x = int(center_x - radius)
        y = int(center_y - radius)
        w = h = int(radius * 2)

        return BubbleRegion(
            center=(int(center_x), int(center_y)),
            radius=int(radius),
            filled_ratio=filled_ratio,
            confidence=confidence,
            contour=best_bubble.contour,
            bounding_box=(x, y, w, h),
            quality_score=confidence * (1.0 - abs(filled_ratio - 0.5))
        )

    def _assess_cell_quality(self, cell_image: np.ndarray, bubbles: List[BubbleRegion]) -> float:
        """
        Assess kualitas cell dan bubble detection

        Args:
            cell_image: Original cell image
            bubbles: Detected bubbles

        Returns:
            Quality score (0.0 to 1.0)
        """
        # Basic quality metrics
        clarity_score = self._calculate_image_clarity(cell_image)
        bubble_consistency = self._calculate_bubble_consistency(bubbles)
        detection_completeness = min(1.0, len(bubbles) / 5.0)  # Expect ~5 bubbles per cell

        # Combined quality score
        quality = (clarity_score * 0.4 +
                  bubble_consistency * 0.4 +
                  detection_completeness * 0.2)

        return quality

    def _calculate_image_clarity(self, image: np.ndarray) -> float:
        """Calculate image clarity using variance of Laplacian"""
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        # Normalize to 0-1 range
        clarity = min(1.0, laplacian_var / 1000.0)
        return clarity

    def _calculate_bubble_consistency(self, bubbles: List[BubbleRegion]) -> float:
        """Calculate consistency of detected bubbles"""
        if len(bubbles) < 2:
            return 1.0 if len(bubbles) == 1 else 0.0

        # Check radius consistency
        radii = [bubble.radius for bubble in bubbles]
        radius_std = np.std(radii)
        radius_consistency = max(0.0, 1.0 - radius_std / np.mean(radii))

        # Check confidence consistency
        confidences = [bubble.confidence for bubble in bubbles]
        confidence_consistency = np.mean(confidences)

        return (radius_consistency + confidence_consistency) / 2

    def _calculate_detection_confidence(self, bubbles: List[BubbleRegion]) -> float:
        """Calculate overall detection confidence"""
        if not bubbles:
            return 0.0

        # Average confidence weighted by quality
        total_weight = sum(bubble.quality_score for bubble in bubbles)
        if total_weight == 0:
            return 0.0

        weighted_confidence = sum(bubble.confidence * bubble.quality_score
                                for bubble in bubbles) / total_weight

        return weighted_confidence

    def classify_bubbles(self, bubbles: List[BubbleRegion]) -> Dict[str, List[BubbleRegion]]:
        """
        Classify bubbles sebagai filled atau empty

        Args:
            bubbles: List of detected bubbles

        Returns:
            Dictionary dengan 'filled' dan 'empty' bubble lists
        """
        filled_bubbles = []
        empty_bubbles = []

        for bubble in bubbles:
            if bubble.filled_ratio >= self.filled_threshold:
                filled_bubbles.append(bubble)
            else:
                empty_bubbles.append(bubble)

        return {
            'filled': filled_bubbles,
            'empty': empty_bubbles
        }

    def extract_answers(self, cell_bubbles: List[BubbleDetectionResult]) -> Dict[int, str]:
        """
        Extract jawaban dari detected bubbles

        Args:
            cell_bubbles: List of bubble detection results per cell

        Returns:
            Dictionary mapping question number to answer (A, B, C, D, E)
        """
        answers = {}
        choices = ['A', 'B', 'C', 'D', 'E']

        for question_idx, result in enumerate(cell_bubbles):
            classified = self.classify_bubbles(result.bubbles)
            filled_bubbles = classified['filled']

            if len(filled_bubbles) == 1:
                # Single answer - ideal case
                bubble_idx = self._determine_bubble_choice_index(filled_bubbles[0], result.bubbles)
                if 0 <= bubble_idx < len(choices):
                    answers[question_idx + 1] = choices[bubble_idx]
            elif len(filled_bubbles) > 1:
                # Multiple answers - choose highest confidence
                best_bubble = max(filled_bubbles, key=lambda b: b.confidence)
                bubble_idx = self._determine_bubble_choice_index(best_bubble, result.bubbles)
                if 0 <= bubble_idx < len(choices):
                    answers[question_idx + 1] = f"{choices[bubble_idx]}*"  # Mark as ambiguous
            else:
                # No answer detected
                answers[question_idx + 1] = "?"

        return answers

    def _determine_bubble_choice_index(self, target_bubble: BubbleRegion,
                                     all_bubbles: List[BubbleRegion]) -> int:
        """
        Determine choice index (0-4 for A-E) berdasarkan posisi bubble

        Args:
            target_bubble: Bubble yang ingin dicari index-nya
            all_bubbles: Semua bubbles dalam cell

        Returns:
            Index choice (0-4) atau -1 jika tidak valid
        """
        if not all_bubbles:
            return -1

        # Sort bubbles by x-coordinate (left to right)
        sorted_bubbles = sorted(all_bubbles, key=lambda b: b.center[0])

        try:
            return sorted_bubbles.index(target_bubble)
        except ValueError:
            # Find closest bubble by center distance
            min_dist = float('inf')
            closest_idx = -1

            for i, bubble in enumerate(sorted_bubbles):
                dist = np.sqrt((target_bubble.center[0] - bubble.center[0])**2 +
                              (target_bubble.center[1] - bubble.center[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    closest_idx = i

            return closest_idx