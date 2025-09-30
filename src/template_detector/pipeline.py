"""
Week 6 - Template Detection & Segmentation
End-to-End Pipeline Integration

Pipeline utama yang mengintegrasikan semua komponen Week 6:
1. Grid detection menggunakan multiple methods
2. Grid segmentation dan perspective correction
3. Cell extraction untuk individual answer cells
4. Bubble detection dan classification

Author: Week 6 Implementation
Date: 2024-09-29
Academic Context: Digital Image Processing Course
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging
import time

from .config import ProcessingConfig
from .core import ContourGridDetector, HoughLineDetector, TemplateMatchingDetector, DetectionFusion
from .segmentation import GridNormalizer, CellExtractor, BubbleDetector
from .utils import VisualizationUtils, QualityAssessment, PerformanceMonitor

@dataclass
class OMRProcessingResult:
    """Hasil lengkap dari processing OMR"""
    # Detection results
    grid_detection: Dict[str, Any]
    grid_quality: float

    # Segmentation results
    normalized_grid: np.ndarray
    extracted_cells: List[np.ndarray]
    cell_quality_scores: List[float]

    # Bubble detection results
    bubble_results: List[Any]  # BubbleDetectionResult
    detected_answers: Dict[int, str]

    # Performance metrics
    processing_time: float
    confidence_score: float

    # Metadata
    metadata: Dict[str, Any]

class OMRPipeline:
    """
    End-to-End OMR Processing Pipeline

    Mengintegrasikan semua komponen Week 6 untuk processing lengkap
    dari gambar OMR hingga ekstraksi jawaban final.
    """

    def __init__(self, config: ProcessingConfig):
        """
        Initialize OMR Pipeline

        Args:
            config: Processing configuration parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize all components
        self.contour_detector = ContourGridDetector(config)
        self.hough_detector = HoughLineDetector(config)
        self.template_detector = TemplateMatchingDetector(config)
        self.detection_fusion = DetectionFusion(config)

        self.grid_normalizer = GridNormalizer(config)
        self.cell_extractor = CellExtractor(config)
        self.bubble_detector = BubbleDetector(config)

        self.visualizer = VisualizationUtils(config)
        self.quality_assessor = QualityAssessment(config)
        self.performance_monitor = PerformanceMonitor()

        self.logger.info("OMR Pipeline initialized successfully")

    def process_omr_image(self, image: np.ndarray,
                         visualize: bool = False) -> OMRProcessingResult:
        """
        Process single OMR image secara end-to-end

        Args:
            image: Input OMR image
            visualize: Whether to generate visualization images

        Returns:
            OMRProcessingResult dengan hasil lengkap processing
        """
        start_time = time.time()

        try:
            self.logger.info("Starting OMR image processing")

            # Step 1: Grid Detection
            self.logger.info("Step 1: Grid Detection")
            grid_detection_result = self._detect_grid(image)

            if not grid_detection_result['success']:
                return self._create_failed_result("Grid detection failed")

            # Step 2: Grid Normalization
            self.logger.info("Step 2: Grid Normalization")
            normalized_grid = self._normalize_grid(image, grid_detection_result)

            if normalized_grid is None:
                return self._create_failed_result("Grid normalization failed")

            # Step 3: Cell Extraction
            self.logger.info("Step 3: Cell Extraction")
            extraction_result = self._extract_cells(normalized_grid)

            if not extraction_result['cells']:
                return self._create_failed_result("Cell extraction failed")

            # Step 4: Bubble Detection
            self.logger.info("Step 4: Bubble Detection")
            bubble_results = self._detect_bubbles(extraction_result['cells'])

            # Step 5: Answer Extraction
            self.logger.info("Step 5: Answer Extraction")
            detected_answers = self._extract_answers(bubble_results)

            # Step 6: Quality Assessment
            self.logger.info("Step 6: Quality Assessment")
            quality_metrics = self._assess_overall_quality(
                grid_detection_result, extraction_result, bubble_results
            )

            processing_time = time.time() - start_time

            # Create comprehensive result
            result = OMRProcessingResult(
                grid_detection=grid_detection_result,
                grid_quality=quality_metrics['grid_quality'],
                normalized_grid=normalized_grid,
                extracted_cells=extraction_result['cells'],
                cell_quality_scores=extraction_result['quality_scores'],
                bubble_results=bubble_results,
                detected_answers=detected_answers,
                processing_time=processing_time,
                confidence_score=quality_metrics['overall_confidence'],
                metadata={
                    'image_shape': image.shape,
                    'num_cells': len(extraction_result['cells']),
                    'num_answers': len(detected_answers),
                    'quality_metrics': quality_metrics,
                    'processing_steps': [
                        'grid_detection', 'grid_normalization',
                        'cell_extraction', 'bubble_detection', 'answer_extraction'
                    ]
                }
            )

            # Generate visualization if requested
            if visualize:
                self._generate_pipeline_visualization(image, result)

            self.logger.info(f"OMR processing completed in {processing_time:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Error in OMR processing: {str(e)}")
            return self._create_failed_result(f"Processing error: {str(e)}")

    def _detect_grid(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Deteksi grid menggunakan multiple methods dan fusion
        """
        # Run all detection methods
        contour_result = self.contour_detector.detect_grid(image)
        hough_result = self.hough_detector.detect_grid(image)
        template_result = self.template_detector.detect_grid(image)

        # Fusion hasil detection
        fusion_result = self.detection_fusion.fuse_detections(
            image, [contour_result, hough_result, template_result]
        )

        return {
            'success': fusion_result.confidence > 0.5,
            'grid_corners': fusion_result.grid_corners,
            'confidence': fusion_result.confidence,
            'method_results': {
                'contour': contour_result,
                'hough': hough_result,
                'template': template_result
            },
            'fusion_result': fusion_result
        }

    def _normalize_grid(self, image: np.ndarray,
                       detection_result: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Normalisasi grid menggunakan perspective correction
        """
        try:
            grid_corners = detection_result['grid_corners']
            normalized = self.grid_normalizer.normalize_perspective(image, grid_corners)
            return normalized
        except Exception as e:
            self.logger.error(f"Grid normalization failed: {str(e)}")
            return None

    def _extract_cells(self, normalized_grid: np.ndarray) -> Dict[str, Any]:
        """
        Ekstraksi individual cells dari normalized grid
        """
        # Extract cells menggunakan multiple methods
        adaptive_result = self.cell_extractor.extract_cells_adaptive(normalized_grid)
        uniform_result = self.cell_extractor.extract_cells_uniform(normalized_grid)

        # Pilih hasil terbaik berdasarkan quality
        if adaptive_result['quality'] >= uniform_result['quality']:
            selected_result = adaptive_result
            method = 'adaptive'
        else:
            selected_result = uniform_result
            method = 'uniform'

        self.logger.info(f"Selected {method} extraction method "
                        f"(quality: {selected_result['quality']:.3f})")

        return {
            'cells': selected_result['cells'],
            'quality_scores': selected_result['cell_qualities'],
            'extraction_method': method,
            'quality': selected_result['quality']
        }

    def _detect_bubbles(self, cells: List[np.ndarray]) -> List[Any]:
        """
        Deteksi bubbles dalam semua cells
        """
        return self.bubble_detector.detect_bubbles_in_cells(cells)

    def _extract_answers(self, bubble_results: List[Any]) -> Dict[int, str]:
        """
        Ekstraksi jawaban final dari bubble detection results
        """
        return self.bubble_detector.extract_answers(bubble_results)

    def _assess_overall_quality(self, grid_detection: Dict[str, Any],
                               extraction_result: Dict[str, Any],
                               bubble_results: List[Any]) -> Dict[str, float]:
        """
        Assessment kualitas overall dari seluruh pipeline
        """
        # Grid detection quality
        grid_quality = grid_detection['confidence']

        # Cell extraction quality
        cell_quality = extraction_result['quality']

        # Bubble detection quality
        if bubble_results:
            bubble_qualities = [result.detection_confidence for result in bubble_results]
            bubble_quality = np.mean(bubble_qualities)
        else:
            bubble_quality = 0.0

        # Overall confidence score
        overall_confidence = (grid_quality * 0.4 +
                            cell_quality * 0.3 +
                            bubble_quality * 0.3)

        return {
            'grid_quality': grid_quality,
            'cell_quality': cell_quality,
            'bubble_quality': bubble_quality,
            'overall_confidence': overall_confidence
        }

    def _create_failed_result(self, error_message: str) -> OMRProcessingResult:
        """
        Create result object untuk failed processing
        """
        return OMRProcessingResult(
            grid_detection={'success': False, 'error': error_message},
            grid_quality=0.0,
            normalized_grid=np.array([]),
            extracted_cells=[],
            cell_quality_scores=[],
            bubble_results=[],
            detected_answers={},
            processing_time=0.0,
            confidence_score=0.0,
            metadata={'error': error_message}
        )

    def _generate_pipeline_visualization(self, original_image: np.ndarray,
                                       result: OMRProcessingResult) -> None:
        """
        Generate comprehensive visualization dari pipeline results
        """
        try:
            # Create visualization dengan multiple panels
            vis_panels = []

            # Panel 1: Original image dengan detected grid
            if result.grid_detection['success']:
                grid_vis = self.visualizer.visualize_grid_detection(
                    original_image, result.grid_detection['fusion_result']
                )
                vis_panels.append(('Grid Detection', grid_vis))

            # Panel 2: Normalized grid
            if result.normalized_grid.size > 0:
                vis_panels.append(('Normalized Grid', result.normalized_grid))

            # Panel 3: Cell extraction
            if result.extracted_cells:
                cell_grid = self._create_cell_grid_visualization(result.extracted_cells)
                vis_panels.append(('Extracted Cells', cell_grid))

            # Panel 4: Bubble detection results
            if result.bubble_results:
                bubble_vis = self._create_bubble_visualization(
                    result.extracted_cells, result.bubble_results
                )
                vis_panels.append(('Bubble Detection', bubble_vis))

            # Combine all panels
            if vis_panels:
                combined_vis = self.visualizer.create_multi_panel_visualization(vis_panels)

                # Save visualization
                timestamp = int(time.time())
                filename = f"omr_pipeline_result_{timestamp}.jpg"
                cv2.imwrite(filename, combined_vis)
                self.logger.info(f"Pipeline visualization saved: {filename}")

        except Exception as e:
            self.logger.error(f"Visualization generation failed: {str(e)}")

    def _create_cell_grid_visualization(self, cells: List[np.ndarray]) -> np.ndarray:
        """Create grid visualization dari extracted cells"""
        if not cells:
            return np.zeros((100, 100), dtype=np.uint8)

        # Arrange cells dalam grid layout
        rows = 20  # TOEFL format: 20 questions per column
        cols = 3   # 3 columns untuk 60 questions

        cell_height = max(cell.shape[0] for cell in cells)
        cell_width = max(cell.shape[1] for cell in cells)

        grid_image = np.zeros((rows * cell_height, cols * cell_width), dtype=np.uint8)

        for i, cell in enumerate(cells[:rows*cols]):
            row = i % rows
            col = i // rows

            y_start = row * cell_height
            x_start = col * cell_width

            # Resize cell to standard size
            resized_cell = cv2.resize(cell, (cell_width, cell_height))

            grid_image[y_start:y_start+cell_height,
                      x_start:x_start+cell_width] = resized_cell

        return grid_image

    def _create_bubble_visualization(self, cells: List[np.ndarray],
                                   bubble_results: List[Any]) -> np.ndarray:
        """Create visualization dengan bubble detection overlay"""
        cell_grid = self._create_cell_grid_visualization(cells)

        # Convert to color untuk overlay
        color_grid = cv2.cvtColor(cell_grid, cv2.COLOR_GRAY2BGR)

        # Overlay bubble detection results
        rows, cols = 20, 3
        cell_height = cell_grid.shape[0] // rows
        cell_width = cell_grid.shape[1] // cols

        for i, result in enumerate(bubble_results[:rows*cols]):
            row = i % rows
            col = i // rows

            y_offset = row * cell_height
            x_offset = col * cell_width

            # Draw detected bubbles
            for bubble in result.bubbles:
                center = (bubble.center[0] + x_offset, bubble.center[1] + y_offset)

                # Color berdasarkan filled status
                if bubble.filled_ratio >= 0.3:
                    color = (0, 255, 0)  # Green untuk filled
                else:
                    color = (0, 0, 255)  # Red untuk empty

                cv2.circle(color_grid, center, bubble.radius, color, 2)

                # Draw confidence score
                cv2.putText(color_grid, f"{bubble.confidence:.2f}",
                           (center[0]-10, center[1]-bubble.radius-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

        return color_grid

    def process_batch(self, images: List[np.ndarray],
                     progress_callback=None) -> List[OMRProcessingResult]:
        """
        Process multiple OMR images secara batch

        Args:
            images: List of OMR images
            progress_callback: Optional callback untuk progress tracking

        Returns:
            List of OMRProcessingResult
        """
        results = []

        for i, image in enumerate(images):
            self.logger.info(f"Processing image {i+1}/{len(images)}")

            result = self.process_omr_image(image)
            results.append(result)

            if progress_callback:
                progress_callback(i+1, len(images), result)

        return results

    def get_performance_summary(self, results: List[OMRProcessingResult]) -> Dict[str, Any]:
        """
        Generate performance summary dari batch processing results
        """
        if not results:
            return {}

        # Processing times
        processing_times = [r.processing_time for r in results]

        # Confidence scores
        confidence_scores = [r.confidence_score for r in results]

        # Success rate
        successful_results = [r for r in results if r.confidence_score > 0.5]
        success_rate = len(successful_results) / len(results)

        # Answer extraction rate
        total_possible_answers = len(results) * 60  # 60 questions per sheet
        total_extracted_answers = sum(len(r.detected_answers) for r in results)
        extraction_rate = total_extracted_answers / total_possible_answers if total_possible_answers > 0 else 0

        return {
            'total_images': len(results),
            'success_rate': success_rate,
            'extraction_rate': extraction_rate,
            'processing_time': {
                'mean': np.mean(processing_times),
                'std': np.std(processing_times),
                'min': np.min(processing_times),
                'max': np.max(processing_times)
            },
            'confidence_scores': {
                'mean': np.mean(confidence_scores),
                'std': np.std(confidence_scores),
                'min': np.min(confidence_scores),
                'max': np.max(confidence_scores)
            }
        }