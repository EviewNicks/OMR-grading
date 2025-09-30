"""
Visualization utilities untuk Template Detection debugging dan analysis
Comprehensive visualization framework untuk algorithm development
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import cv2
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VisualizationUtils:
    """Utility class untuk visualization template detection results"""

    def __init__(self):
        """Initialize visualization utilities dengan default styling"""
        self.setup_style()
        self.detection_colors = {
            'contour': '#FF6B6B',     # Red
            'hough': '#4ECDC4',       # Teal
            'template': '#45B7D1',    # Blue
            'fusion': '#96CEB4',      # Green
            'ground_truth': '#FECA57', # Yellow
            'segmentation': '#A855F7'  # Purple
        }

    def setup_style(self) -> None:
        """Setup matplotlib styling untuk consistent visualization"""
        plt.style.use('default')
        sns.set_palette("husl")

        # Custom matplotlib parameters
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 14
        })

    def visualize_detection_comparison(
        self,
        image: np.ndarray,
        detections: Dict[str, Dict],
        title: str = "Detection Methods Comparison",
        save_path: Optional[Union[str, Path]] = None
    ) -> plt.Figure:
        """
        Visualize comparison antara multiple detection methods

        Args:
            image: Input image
            detections: Dictionary dengan detection results per method
            title: Plot title
            save_path: Path untuk save visualization

        Returns:
            matplotlib Figure object
        """
        num_methods = len(detections)
        fig, axes = plt.subplots(1, num_methods + 1, figsize=(5 * (num_methods + 1), 5))

        if num_methods == 0:
            axes = [axes]
        elif num_methods == 1:
            axes = [axes[0], axes[1]]

        # Original image
        axes[0].imshow(image, cmap='gray')
        axes[0].set_title('Original Image', fontweight='bold')
        axes[0].axis('off')

        # Detection results untuk each method
        for idx, (method_name, detection_data) in enumerate(detections.items(), 1):
            if idx < len(axes):
                axes[idx].imshow(image, cmap='gray')

                # Draw detection results
                self._draw_detection_result(axes[idx], detection_data, method_name)

                # Title dengan confidence score
                confidence = detection_data.get('confidence', 0.0)
                axes[idx].set_title(
                    f'{method_name.title()}\n(conf: {confidence:.3f})',
                    fontweight='bold',
                    color=self.detection_colors.get(method_name, 'black')
                )
                axes[idx].axis('off')

        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Visualization saved to {save_path}")

        return fig

    def _draw_detection_result(self, ax: plt.Axes, detection_data: Dict, method_name: str) -> None:
        """Draw detection result pada axes"""
        color = self.detection_colors.get(method_name, 'white')

        # Draw grid coordinates
        if 'grid_coordinates' in detection_data and detection_data['grid_coordinates'] is not None:
            coords = detection_data['grid_coordinates']
            if len(coords) == 4:  # [x1, y1, x2, y2]
                rect = patches.Rectangle(
                    (coords[0], coords[1]),
                    coords[2] - coords[0],
                    coords[3] - coords[1],
                    linewidth=2,
                    edgecolor=color,
                    facecolor='none',
                    alpha=0.8
                )
                ax.add_patch(rect)

        # Draw grid corners if available
        if 'grid_corners' in detection_data and detection_data['grid_corners'] is not None:
            corners = detection_data['grid_corners']
            for corner in corners:
                ax.plot(corner[0], corner[1], 'o', color=color, markersize=6)

        # Draw contours if available
        if 'contours' in detection_data and detection_data['contours'] is not None:
            contours = detection_data['contours']
            for contour in contours:
                contour_points = contour.reshape(-1, 2)
                ax.plot(contour_points[:, 0], contour_points[:, 1], color=color, linewidth=1, alpha=0.6)

        # Draw lines if available (for Hough transform)
        if 'detected_lines' in detection_data and detection_data['detected_lines'] is not None:
            lines = detection_data['detected_lines']
            for line in lines:
                if len(line) == 4:  # [x1, y1, x2, y2]
                    ax.plot([line[0], line[2]], [line[1], line[3]], color=color, linewidth=1, alpha=0.7)
                elif len(line) == 2:  # [rho, theta]
                    self._draw_hough_line(ax, line[0], line[1], color)

    def _draw_hough_line(self, ax: plt.Axes, rho: float, theta: float, color: str) -> None:
        """Draw Hough line pada axes"""
        # Convert polar coordinates ke cartesian
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho

        # Extend line across image
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))

        ax.plot([x1, x2], [y1, y2], color=color, linewidth=1, alpha=0.7)

    def visualize_segmentation_results(
        self,
        original_image: np.ndarray,
        grid_coordinates: Tuple[int, int, int, int],
        cell_regions: List[np.ndarray],
        title: str = "Grid Segmentation Results",
        max_cells_display: int = 20,
        save_path: Optional[Union[str, Path]] = None
    ) -> plt.Figure:
        """
        Visualize grid segmentation results

        Args:
            original_image: Original input image
            grid_coordinates: Detected grid coordinates [x1, y1, x2, y2]
            cell_regions: List extracted cell regions
            title: Plot title
            max_cells_display: Maximum number cells to display
            save_path: Path untuk save visualization

        Returns:
            matplotlib Figure object
        """
        num_cells = min(len(cell_regions), max_cells_display)
        cols = min(6, num_cells + 1)
        rows = (num_cells + cols) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
        if rows == 1:
            axes = axes.reshape(1, -1)

        # Original image dengan grid overlay
        axes[0, 0].imshow(original_image, cmap='gray')
        if grid_coordinates:
            x1, y1, x2, y2 = grid_coordinates
            rect = patches.Rectangle(
                (x1, y1), x2 - x1, y2 - y1,
                linewidth=2, edgecolor=self.detection_colors['segmentation'],
                facecolor='none', alpha=0.8
            )
            axes[0, 0].add_patch(rect)
        axes[0, 0].set_title('Grid Detection', fontweight='bold')
        axes[0, 0].axis('off')

        # Individual cell regions
        for idx, cell in enumerate(cell_regions[:max_cells_display]):
            row = (idx + 1) // cols
            col = (idx + 1) % cols

            if row < rows and col < cols:
                axes[row, col].imshow(cell, cmap='gray')
                axes[row, col].set_title(f'Cell {idx + 1}', fontsize=8)
                axes[row, col].axis('off')

        # Hide unused subplots
        for idx in range(num_cells + 1, rows * cols):
            row = idx // cols
            col = idx % cols
            if row < rows and col < cols:
                axes[row, col].axis('off')

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Segmentation visualization saved to {save_path}")

        return fig

    def visualize_quality_assessment(
        self,
        quality_metrics: Dict[str, float],
        title: str = "Quality Assessment Metrics",
        save_path: Optional[Union[str, Path]] = None
    ) -> plt.Figure:
        """
        Visualize quality assessment metrics

        Args:
            quality_metrics: Dictionary dengan quality metrics
            title: Plot title
            save_path: Path untuk save visualization

        Returns:
            matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Bar chart untuk individual metrics
        metrics_names = list(quality_metrics.keys())
        metrics_values = list(quality_metrics.values())

        bars = ax1.bar(metrics_names, metrics_values, color=sns.color_palette("husl", len(metrics_names)))
        ax1.set_title('Quality Metrics', fontweight='bold')
        ax1.set_ylabel('Score')
        ax1.set_ylim(0, 1)
        ax1.tick_params(axis='x', rotation=45)

        # Add value labels pada bars
        for bar, value in zip(bars, metrics_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.3f}', ha='center', va='bottom')

        # Radar chart untuk overall assessment
        categories = metrics_names
        values = metrics_values

        # Compute angle untuk each axis
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]

        ax2 = plt.subplot(122, projection='polar')
        ax2.plot(angles, values, 'o-', linewidth=2, color=self.detection_colors['fusion'])
        ax2.fill(angles, values, alpha=0.25, color=self.detection_colors['fusion'])
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(categories)
        ax2.set_ylim(0, 1)
        ax2.set_title('Quality Profile', fontweight='bold', pad=20)

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Quality assessment visualization saved to {save_path}")

        return fig

    def visualize_performance_metrics(
        self,
        performance_data: Dict[str, Dict],
        title: str = "Performance Analysis",
        save_path: Optional[Union[str, Path]] = None
    ) -> plt.Figure:
        """
        Visualize performance metrics comparison

        Args:
            performance_data: Dictionary dengan performance data per method
            title: Plot title
            save_path: Path untuk save visualization

        Returns:
            matplotlib Figure object
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

        methods = list(performance_data.keys())
        colors = [self.detection_colors.get(method, 'gray') for method in methods]

        # Processing time comparison
        processing_times = [performance_data[method].get('processing_time', 0) for method in methods]
        bars1 = ax1.bar(methods, processing_times, color=colors, alpha=0.7)
        ax1.set_title('Processing Time Comparison', fontweight='bold')
        ax1.set_ylabel('Time (seconds)')
        for bar, time in zip(bars1, processing_times):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{time:.3f}s', ha='center', va='bottom')

        # Accuracy comparison
        accuracies = [performance_data[method].get('accuracy', 0) for method in methods]
        bars2 = ax2.bar(methods, accuracies, color=colors, alpha=0.7)
        ax2.set_title('Detection Accuracy Comparison', fontweight='bold')
        ax2.set_ylabel('Accuracy')
        ax2.set_ylim(0, 1)
        for bar, acc in zip(bars2, accuracies):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{acc:.3f}', ha='center', va='bottom')

        # Confidence distribution
        confidences = [performance_data[method].get('confidence_scores', []) for method in methods]
        ax3.boxplot(confidences, labels=methods)
        ax3.set_title('Confidence Score Distribution', fontweight='bold')
        ax3.set_ylabel('Confidence')

        # Success rate
        success_rates = [performance_data[method].get('success_rate', 0) for method in methods]
        bars4 = ax4.bar(methods, success_rates, color=colors, alpha=0.7)
        ax4.set_title('Success Rate Comparison', fontweight='bold')
        ax4.set_ylabel('Success Rate')
        ax4.set_ylim(0, 1)
        for bar, rate in zip(bars4, success_rates):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{rate:.3f}', ha='center', va='bottom')

        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Performance visualization saved to {save_path}")

        return fig

    def create_detection_summary_report(
        self,
        image: np.ndarray,
        detections: Dict[str, Dict],
        quality_metrics: Dict[str, float],
        performance_metrics: Dict[str, Dict],
        filename: str,
        save_dir: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Create comprehensive detection summary report

        Args:
            image: Original image
            detections: Detection results per method
            quality_metrics: Quality assessment metrics
            performance_metrics: Performance metrics per method
            filename: Image filename
            save_dir: Directory untuk save report
        """
        if save_dir:
            save_dir = Path(save_dir)
            save_dir.mkdir(exist_ok=True)

            # Create individual visualizations
            det_fig = self.visualize_detection_comparison(
                image, detections, f"Detection Results - {filename}",
                save_dir / f"{filename}_detection_comparison.png"
            )

            qual_fig = self.visualize_quality_assessment(
                quality_metrics, f"Quality Assessment - {filename}",
                save_dir / f"{filename}_quality_assessment.png"
            )

            perf_fig = self.visualize_performance_metrics(
                performance_metrics, f"Performance Analysis - {filename}",
                save_dir / f"{filename}_performance_analysis.png"
            )

            # Close figures untuk free memory
            plt.close(det_fig)
            plt.close(qual_fig)
            plt.close(perf_fig)

            logger.info(f"Comprehensive report created for {filename} in {save_dir}")

    def show_detection_pipeline_flow(
        self,
        pipeline_stages: List[Tuple[str, np.ndarray]],
        title: str = "Detection Pipeline Flow",
        save_path: Optional[Union[str, Path]] = None
    ) -> plt.Figure:
        """
        Visualize detection pipeline flow dengan intermediate results

        Args:
            pipeline_stages: List of (stage_name, image) tuples
            title: Plot title
            save_path: Path untuk save visualization

        Returns:
            matplotlib Figure object
        """
        num_stages = len(pipeline_stages)
        cols = min(4, num_stages)
        rows = (num_stages + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows))
        if rows == 1:
            axes = axes.reshape(1, -1) if num_stages > 1 else [axes]
        elif cols == 1:
            axes = axes.reshape(-1, 1)

        for idx, (stage_name, stage_image) in enumerate(pipeline_stages):
            row = idx // cols
            col = idx % cols

            if rows == 1:
                ax = axes[col] if num_stages > 1 else axes
            else:
                ax = axes[row, col]

            ax.imshow(stage_image, cmap='gray')
            ax.set_title(stage_name, fontweight='bold')
            ax.axis('off')

        # Hide unused subplots
        for idx in range(num_stages, rows * cols):
            row = idx // cols
            col = idx % cols
            if rows > 1:
                axes[row, col].axis('off')
            elif num_stages > 1:
                axes[col].axis('off')

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Pipeline flow visualization saved to {save_path}")

        return fig