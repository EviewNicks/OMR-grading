"""
Performance Monitor untuk Template Detection system
Real-time performance tracking, benchmarking, dan optimization monitoring
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from datetime import datetime
import psutil
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Data structure untuk performance metrics"""
    processing_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    accuracy: float
    confidence: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BenchmarkResults:
    """Data structure untuk benchmark results"""
    total_images: int
    successful_detections: int
    failed_detections: int
    average_processing_time: float
    std_processing_time: float
    average_accuracy: float
    average_confidence: float
    memory_peak_mb: float
    cpu_average_percent: float
    success_rate: float
    errors_by_type: Dict[str, int]
    performance_distribution: Dict[str, List[float]]


class PerformanceMonitor:
    """Performance monitoring system untuk template detection"""

    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor

        Args:
            max_history: Maximum number of performance records to keep
        """
        self.max_history = max_history
        self.performance_history = deque(maxlen=max_history)
        self.method_statistics = defaultdict(list)
        self.benchmark_results = {}
        self.monitoring_active = False
        self.start_time = None

        # System monitoring
        self.system_monitor_thread = None
        self.system_metrics = deque(maxlen=100)

    def start_monitoring(self) -> None:
        """Start performance monitoring session"""
        self.monitoring_active = True
        self.start_time = time.time()

        # Start system monitoring thread
        self.system_monitor_thread = threading.Thread(target=self._monitor_system_resources)
        self.system_monitor_thread.daemon = True
        self.system_monitor_thread.start()

        logger.info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring session"""
        self.monitoring_active = False

        if self.system_monitor_thread:
            self.system_monitor_thread.join(timeout=1)

        logger.info("Performance monitoring stopped")

    def _monitor_system_resources(self) -> None:
        """Monitor system resources dalam background thread"""
        while self.monitoring_active:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()

                self.system_metrics.append({
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_usage_mb': memory_info.used / (1024 * 1024),
                    'memory_percent': memory_info.percent
                })
            except Exception as e:
                logger.warning(f"Error monitoring system resources: {str(e)}")

            time.sleep(1)

    def time_operation(self, operation_name: str):
        """Context manager untuk timing operations"""
        return OperationTimer(self, operation_name)

    def record_detection_performance(
        self,
        method_name: str,
        processing_time: float,
        accuracy: float,
        confidence: float,
        success: bool,
        error_message: Optional[str] = None,
        additional_metrics: Optional[Dict] = None
    ) -> None:
        """
        Record performance metrics untuk detection operation

        Args:
            method_name: Name detection method
            processing_time: Processing time dalam seconds
            accuracy: Detection accuracy (0-1)
            confidence: Detection confidence (0-1)
            success: Whether operation was successful
            error_message: Error message if failed
            additional_metrics: Additional metrics to record
        """
        # Get current system metrics
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)
        cpu_usage = psutil.cpu_percent()

        # Create performance metrics
        metrics = PerformanceMetrics(
            processing_time=processing_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            accuracy=accuracy,
            confidence=confidence,
            success=success,
            error_message=error_message
        )

        # Add to history
        self.performance_history.append((method_name, metrics))

        # Add to method-specific statistics
        self.method_statistics[method_name].append({
            'processing_time': processing_time,
            'accuracy': accuracy,
            'confidence': confidence,
            'success': success,
            'memory_usage_mb': memory_usage,
            'cpu_usage_percent': cpu_usage,
            'timestamp': metrics.timestamp
        })

        # Add additional metrics if provided
        if additional_metrics:
            self.method_statistics[method_name][-1].update(additional_metrics)

        logger.debug(f"Recorded performance untuk {method_name}: "
                    f"time={processing_time:.3f}s, accuracy={accuracy:.3f}, "
                    f"confidence={confidence:.3f}, success={success}")

    def get_method_statistics(self, method_name: str) -> Dict:
        """Get statistics untuk specific detection method"""
        if method_name not in self.method_statistics:
            return {}

        data = self.method_statistics[method_name]
        if not data:
            return {}

        processing_times = [d['processing_time'] for d in data]
        accuracies = [d['accuracy'] for d in data]
        confidences = [d['confidence'] for d in data]
        successes = [d['success'] for d in data]

        return {
            'total_operations': len(data),
            'success_count': sum(successes),
            'success_rate': sum(successes) / len(successes),
            'average_processing_time': np.mean(processing_times),
            'std_processing_time': np.std(processing_times),
            'min_processing_time': np.min(processing_times),
            'max_processing_time': np.max(processing_times),
            'average_accuracy': np.mean(accuracies),
            'std_accuracy': np.std(accuracies),
            'average_confidence': np.mean(confidences),
            'std_confidence': np.std(confidences),
            'percentile_95_time': np.percentile(processing_times, 95),
            'percentile_99_time': np.percentile(processing_times, 99)
        }

    def get_overall_statistics(self) -> Dict:
        """Get overall performance statistics across all methods"""
        if not self.performance_history:
            return {}

        all_metrics = [metrics for _, metrics in self.performance_history]

        processing_times = [m.processing_time for m in all_metrics]
        accuracies = [m.accuracy for m in all_metrics]
        confidences = [m.confidence for m in all_metrics]
        successes = [m.success for m in all_metrics]
        memory_usages = [m.memory_usage_mb for m in all_metrics]
        cpu_usages = [m.cpu_usage_percent for m in all_metrics]

        return {
            'total_operations': len(all_metrics),
            'success_count': sum(successes),
            'success_rate': sum(successes) / len(successes),
            'average_processing_time': np.mean(processing_times),
            'std_processing_time': np.std(processing_times),
            'average_accuracy': np.mean(accuracies),
            'average_confidence': np.mean(confidences),
            'average_memory_usage_mb': np.mean(memory_usages),
            'average_cpu_usage_percent': np.mean(cpu_usages),
            'performance_trends': self._calculate_performance_trends()
        }

    def _calculate_performance_trends(self) -> Dict:
        """Calculate performance trends over time"""
        if len(self.performance_history) < 10:
            return {}

        # Recent vs historical comparison
        recent_count = min(50, len(self.performance_history) // 4)
        recent_metrics = list(self.performance_history)[-recent_count:]
        historical_metrics = list(self.performance_history)[:-recent_count]

        recent_times = [m[1].processing_time for m in recent_metrics]
        historical_times = [m[1].processing_time for m in historical_metrics]

        recent_accuracies = [m[1].accuracy for m in recent_metrics]
        historical_accuracies = [m[1].accuracy for m in historical_metrics]

        return {
            'time_trend': {
                'recent_average': np.mean(recent_times),
                'historical_average': np.mean(historical_times),
                'improvement_percent': (np.mean(historical_times) - np.mean(recent_times)) / np.mean(historical_times) * 100
            },
            'accuracy_trend': {
                'recent_average': np.mean(recent_accuracies),
                'historical_average': np.mean(historical_accuracies),
                'improvement_percent': (np.mean(recent_accuracies) - np.mean(historical_accuracies)) / np.mean(historical_accuracies) * 100
            }
        }

    def run_benchmark(
        self,
        detection_function: callable,
        test_images: List,
        ground_truth: Optional[List] = None,
        benchmark_name: str = "default"
    ) -> BenchmarkResults:
        """
        Run comprehensive benchmark untuk detection function

        Args:
            detection_function: Function to benchmark
            test_images: List test images
            ground_truth: Optional ground truth untuk accuracy calculation
            benchmark_name: Name untuk benchmark session

        Returns:
            BenchmarkResults object
        """
        logger.info(f"Starting benchmark '{benchmark_name}' dengan {len(test_images)} images")

        # Reset statistics untuk clean benchmark
        benchmark_metrics = []
        errors_by_type = defaultdict(int)
        peak_memory = 0.0

        start_time = time.time()

        for idx, image in enumerate(test_images):
            try:
                # Monitor memory before operation
                memory_before = psutil.virtual_memory().used / (1024 * 1024)

                # Time the detection operation
                operation_start = time.time()
                result = detection_function(image)
                operation_time = time.time() - operation_start

                # Monitor memory after operation
                memory_after = psutil.virtual_memory().used / (1024 * 1024)
                peak_memory = max(peak_memory, memory_after)

                # Calculate accuracy if ground truth available
                accuracy = 0.0
                if ground_truth and idx < len(ground_truth):
                    accuracy = self._calculate_detection_accuracy(result, ground_truth[idx])

                # Extract confidence
                confidence = result.get('confidence', 0.0) if isinstance(result, dict) else 0.0

                # Record metrics
                benchmark_metrics.append({
                    'processing_time': operation_time,
                    'accuracy': accuracy,
                    'confidence': confidence,
                    'memory_usage_mb': memory_after - memory_before,
                    'success': True,
                    'image_index': idx
                })

                logger.debug(f"Benchmark image {idx + 1}/{len(test_images)}: "
                           f"time={operation_time:.3f}s, accuracy={accuracy:.3f}")

            except Exception as e:
                error_type = type(e).__name__
                errors_by_type[error_type] += 1

                benchmark_metrics.append({
                    'processing_time': 0.0,
                    'accuracy': 0.0,
                    'confidence': 0.0,
                    'memory_usage_mb': 0.0,
                    'success': False,
                    'error_message': str(e),
                    'image_index': idx
                })

                logger.warning(f"Benchmark image {idx + 1} failed: {str(e)}")

        total_time = time.time() - start_time

        # Calculate benchmark results
        successful_metrics = [m for m in benchmark_metrics if m['success']]

        if successful_metrics:
            processing_times = [m['processing_time'] for m in successful_metrics]
            accuracies = [m['accuracy'] for m in successful_metrics]
            confidences = [m['confidence'] for m in successful_metrics]

            results = BenchmarkResults(
                total_images=len(test_images),
                successful_detections=len(successful_metrics),
                failed_detections=len(test_images) - len(successful_metrics),
                average_processing_time=np.mean(processing_times),
                std_processing_time=np.std(processing_times),
                average_accuracy=np.mean(accuracies),
                average_confidence=np.mean(confidences),
                memory_peak_mb=peak_memory,
                cpu_average_percent=np.mean([m.get('cpu_usage_percent', 0) for m in self.system_metrics]),
                success_rate=len(successful_metrics) / len(test_images),
                errors_by_type=dict(errors_by_type),
                performance_distribution={
                    'processing_times': processing_times,
                    'accuracies': accuracies,
                    'confidences': confidences
                }
            )
        else:
            results = BenchmarkResults(
                total_images=len(test_images),
                successful_detections=0,
                failed_detections=len(test_images),
                average_processing_time=0.0,
                std_processing_time=0.0,
                average_accuracy=0.0,
                average_confidence=0.0,
                memory_peak_mb=peak_memory,
                cpu_average_percent=0.0,
                success_rate=0.0,
                errors_by_type=dict(errors_by_type),
                performance_distribution={'processing_times': [], 'accuracies': [], 'confidences': []}
            )

        # Store benchmark results
        self.benchmark_results[benchmark_name] = results

        logger.info(f"Benchmark '{benchmark_name}' completed: "
                   f"success_rate={results.success_rate:.3f}, "
                   f"avg_time={results.average_processing_time:.3f}s, "
                   f"avg_accuracy={results.average_accuracy:.3f}")

        return results

    def _calculate_detection_accuracy(self, detection_result: Dict, ground_truth: Dict) -> float:
        """Calculate accuracy berdasarkan detection result dan ground truth"""
        if not isinstance(detection_result, dict) or not isinstance(ground_truth, dict):
            return 0.0

        # Check if grid coordinates exist
        if 'grid_coordinates' not in detection_result or 'grid_coordinates' not in ground_truth:
            return 0.0

        detected_coords = detection_result['grid_coordinates']
        true_coords = ground_truth['grid_coordinates']

        if detected_coords is None or true_coords is None:
            return 0.0

        # Calculate IoU (Intersection over Union)
        return self._calculate_iou(detected_coords, true_coords)

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

    def export_performance_data(self, filepath: Union[str, Path]) -> None:
        """Export performance data ke file"""
        filepath = Path(filepath)

        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'monitoring_session': {
                'start_time': self.start_time,
                'duration_seconds': time.time() - self.start_time if self.start_time else 0,
                'total_operations': len(self.performance_history)
            },
            'overall_statistics': self.get_overall_statistics(),
            'method_statistics': {
                method: self.get_method_statistics(method)
                for method in self.method_statistics.keys()
            },
            'benchmark_results': {
                name: {
                    'total_images': results.total_images,
                    'successful_detections': results.successful_detections,
                    'failed_detections': results.failed_detections,
                    'average_processing_time': results.average_processing_time,
                    'std_processing_time': results.std_processing_time,
                    'average_accuracy': results.average_accuracy,
                    'average_confidence': results.average_confidence,
                    'success_rate': results.success_rate,
                    'errors_by_type': results.errors_by_type
                }
                for name, results in self.benchmark_results.items()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Performance data exported to {filepath}")

    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        overall_stats = self.get_overall_statistics()

        report = {
            'summary': {
                'monitoring_duration_hours': (time.time() - self.start_time) / 3600 if self.start_time else 0,
                'total_operations': overall_stats.get('total_operations', 0),
                'overall_success_rate': overall_stats.get('success_rate', 0.0),
                'average_processing_time': overall_stats.get('average_processing_time', 0.0),
                'average_accuracy': overall_stats.get('average_accuracy', 0.0)
            },
            'method_breakdown': {},
            'performance_analysis': self._analyze_performance(),
            'recommendations': self._generate_recommendations()
        }

        # Method-specific breakdown
        for method in self.method_statistics.keys():
            method_stats = self.get_method_statistics(method)
            report['method_breakdown'][method] = {
                'operations': method_stats.get('total_operations', 0),
                'success_rate': method_stats.get('success_rate', 0.0),
                'avg_time': method_stats.get('average_processing_time', 0.0),
                'avg_accuracy': method_stats.get('average_accuracy', 0.0)
            }

        return report

    def _analyze_performance(self) -> Dict:
        """Analyze performance patterns dan identify issues"""
        analysis = {
            'bottlenecks': [],
            'trends': {},
            'outliers': [],
            'efficiency_metrics': {}
        }

        # Identify performance bottlenecks
        for method, stats in self.method_statistics.items():
            method_stats = self.get_method_statistics(method)

            if method_stats.get('average_processing_time', 0) > 3.0:
                analysis['bottlenecks'].append({
                    'method': method,
                    'issue': 'slow_processing',
                    'avg_time': method_stats.get('average_processing_time', 0)
                })

            if method_stats.get('success_rate', 0) < 0.8:
                analysis['bottlenecks'].append({
                    'method': method,
                    'issue': 'low_success_rate',
                    'success_rate': method_stats.get('success_rate', 0)
                })

        # Calculate efficiency metrics
        overall_stats = self.get_overall_statistics()
        if overall_stats:
            analysis['efficiency_metrics'] = {
                'operations_per_minute': (overall_stats.get('total_operations', 0) * 60) /
                                        ((time.time() - self.start_time) if self.start_time else 1),
                'average_throughput': 1.0 / overall_stats.get('average_processing_time', 1.0),
                'resource_efficiency': overall_stats.get('average_accuracy', 0) /
                                     max(overall_stats.get('average_processing_time', 1), 0.1)
            }

        return analysis

    def _generate_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        overall_stats = self.get_overall_statistics()

        # Processing time recommendations
        avg_time = overall_stats.get('average_processing_time', 0)
        if avg_time > 3.0:
            recommendations.append(
                f"Processing time is high ({avg_time:.2f}s). Consider optimizing algorithms atau reducing image resolution."
            )

        # Accuracy recommendations
        avg_accuracy = overall_stats.get('average_accuracy', 0)
        if avg_accuracy < 0.8:
            recommendations.append(
                f"Detection accuracy is low ({avg_accuracy:.2f}). Consider parameter tuning atau improved preprocessing."
            )

        # Success rate recommendations
        success_rate = overall_stats.get('success_rate', 0)
        if success_rate < 0.9:
            recommendations.append(
                f"Success rate is low ({success_rate:.2f}). Review error handling dan edge cases."
            )

        # Method-specific recommendations
        for method in self.method_statistics.keys():
            method_stats = self.get_method_statistics(method)

            if method_stats.get('std_processing_time', 0) > method_stats.get('average_processing_time', 0) * 0.5:
                recommendations.append(
                    f"Method '{method}' shows high time variance. Consider consistent parameter optimization."
                )

        return recommendations


class OperationTimer:
    """Context manager untuk timing operations"""

    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        self.result = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        processing_time = time.time() - self.start_time

        success = exc_type is None
        error_message = str(exc_val) if exc_val else None

        # Record performance dengan default values
        self.monitor.record_detection_performance(
            method_name=self.operation_name,
            processing_time=processing_time,
            accuracy=0.0,  # Will be updated if result is available
            confidence=0.0,  # Will be updated if result is available
            success=success,
            error_message=error_message
        )

    def update_result(self, accuracy: float, confidence: float):
        """Update result dengan accuracy dan confidence scores"""
        if self.monitor.performance_history:
            # Update last recorded performance
            last_entry = self.monitor.performance_history[-1]
            if last_entry[0] == self.operation_name:
                last_entry[1].accuracy = accuracy
                last_entry[1].confidence = confidence