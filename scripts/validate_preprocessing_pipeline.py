"""Validation Script untuk Preprocessing Pipeline

Script ini melakukan validasi preprocessing pipeline pada datasets/test/
dan membandingkan hasil dengan baseline datasets/train/ (97.4% readiness).

Usage:
    python scripts/validate_preprocessing_pipeline.py
    python scripts/validate_preprocessing_pipeline.py --input datasets/test --output results/
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import time
import argparse
from typing import List, Dict
from glob import glob
import numpy as np

# Import preprocessing pipeline
from src.preprocessing import (
    batch_preprocess,
    PreprocessResult,
    PreprocessConfig,
    OPTIMAL_CONFIG
)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Validate preprocessing pipeline pada datasets/test/"
    )

    parser.add_argument(
        "--input",
        type=str,
        default="datasets/test",
        help="Input directory dengan test images (default: datasets/test)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="results",
        help="Output directory untuk validation results (default: results)"
    )

    parser.add_argument(
        "--baseline",
        type=float,
        default=0.974,
        help="Baseline readiness score dari datasets/train (default: 0.974)"
    )

    parser.add_argument(
        "--min-success-rate",
        type=float,
        default=0.90,
        help="Minimum success rate target (default: 0.90)"
    )

    return parser.parse_args()


def validate_dataset(input_dir: Path, config: PreprocessConfig = None) -> List[PreprocessResult]:
    """Process semua images dalam dataset directory

    Args:
        input_dir: Directory dengan test images
        config: Preprocessing configuration (default: OPTIMAL_CONFIG)

    Returns:
        List of PreprocessResult objects
    """
    print(f"\n📂 Loading images from: {input_dir}")

    # Find all images
    image_patterns = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]
    image_paths = []

    for pattern in image_patterns:
        image_paths.extend(glob(str(input_dir / pattern)))

    if not image_paths:
        raise FileNotFoundError(f"No images found in {input_dir}")

    print(f"✅ Found {len(image_paths)} images")

    # Use optimal config if not provided
    if config is None:
        config = OPTIMAL_CONFIG

    # Batch process
    print(f"\n🔄 Processing images with optimal configuration...")
    start_time = time.time()

    results = batch_preprocess(image_paths, config, show_progress=True)

    total_time = time.time() - start_time
    print(f"\n⏱️  Total processing time: {total_time:.2f}s")

    return results


def calculate_aggregate_metrics(results: List[PreprocessResult]) -> Dict:
    """Calculate aggregate metrics dari batch processing results

    Args:
        results: List of PreprocessResult objects

    Returns:
        Dictionary dengan aggregate metrics
    """
    print(f"\n📊 Calculating aggregate metrics...")

    total = len(results)
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    # Basic statistics
    success_rate = len(successful) / total if total > 0 else 0

    # Processing time statistics
    processing_times = [r.processing_time for r in results]
    avg_time = np.mean(processing_times)
    max_time = np.max(processing_times)
    min_time = np.min(processing_times)

    # Quality metrics (only from successful results)
    if successful:
        readiness_scores = [r.metrics.readiness_score for r in successful]
        rms_contrasts = [r.metrics.rms_contrast for r in successful]
        edge_densities = [r.metrics.edge_density for r in successful]
        laplacian_vars = [r.metrics.laplacian_variance for r in successful]

        avg_readiness = np.mean(readiness_scores)
        std_readiness = np.std(readiness_scores)
        min_readiness = np.min(readiness_scores)
        max_readiness = np.max(readiness_scores)

        avg_rms_contrast = np.mean(rms_contrasts)
        avg_edge_density = np.mean(edge_densities)
        avg_laplacian = np.mean(laplacian_vars)
    else:
        avg_readiness = std_readiness = min_readiness = max_readiness = 0
        avg_rms_contrast = avg_edge_density = avg_laplacian = 0

    # Quality flags statistics
    if successful:
        contrast_pass = sum(r.quality_flags['sufficient_contrast'] for r in successful)
        edges_pass = sum(r.quality_flags['sufficient_edges'] for r in successful)
        readiness_pass = sum(r.quality_flags['meets_readiness'] for r in successful)
    else:
        contrast_pass = edges_pass = readiness_pass = 0

    metrics = {
        'total_images': total,
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': success_rate,

        'processing_time': {
            'average': avg_time,
            'min': min_time,
            'max': max_time,
            'total': sum(processing_times)
        },

        'quality_metrics': {
            'readiness_score': {
                'average': avg_readiness,
                'std': std_readiness,
                'min': min_readiness,
                'max': max_readiness
            },
            'rms_contrast': {
                'average': avg_rms_contrast
            },
            'edge_density': {
                'average': avg_edge_density
            },
            'laplacian_variance': {
                'average': avg_laplacian
            }
        },

        'quality_flags': {
            'sufficient_contrast': {
                'count': contrast_pass,
                'rate': contrast_pass / len(successful) if successful else 0
            },
            'sufficient_edges': {
                'count': edges_pass,
                'rate': edges_pass / len(successful) if successful else 0
            },
            'meets_readiness': {
                'count': readiness_pass,
                'rate': readiness_pass / len(successful) if successful else 0
            }
        },

        'failed_images': [
            {
                'index': i,
                'error': r.error_message
            }
            for i, r in enumerate(results) if not r.success
        ]
    }

    return metrics


def compare_with_baseline(metrics: Dict, baseline: float) -> Dict:
    """Compare validation results dengan baseline dari datasets/train

    Args:
        metrics: Aggregate metrics dari validation
        baseline: Baseline readiness score (0.974 dari datasets/train)

    Returns:
        Dictionary dengan comparison results
    """
    print(f"\n🔍 Comparing with baseline (target: {baseline:.1%})")

    avg_readiness = metrics['quality_metrics']['readiness_score']['average']

    comparison = {
        'baseline_readiness': float(baseline),
        'achieved_readiness': float(avg_readiness),
        'difference': float(avg_readiness - baseline),
        'percentage_of_baseline': float((avg_readiness / baseline * 100) if baseline > 0 else 0),
        'meets_target': bool(avg_readiness >= (baseline * 0.90))  # 90% of baseline
    }

    return comparison


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder untuk handle numpy types"""
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def generate_json_report(metrics: Dict, comparison: Dict, output_path: Path):
    """Generate JSON report dengan validation results

    Args:
        metrics: Aggregate metrics
        comparison: Baseline comparison results
        output_path: Output file path
    """
    report = {
        'validation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'metrics': metrics,
        'baseline_comparison': comparison
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, cls=NumpyEncoder)

    print(f"\n💾 JSON report saved: {output_path}")


def generate_markdown_report(metrics: Dict, comparison: Dict, output_path: Path):
    """Generate markdown report dengan validation results

    Args:
        metrics: Aggregate metrics
        comparison: Baseline comparison results
        output_path: Output file path
    """
    # Build markdown content
    md_content = f"""# Preprocessing Pipeline - Validation Report

**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Dataset**: datasets/test/

---

## 📊 Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total Images | {metrics['total_images']} | - |
| Success Rate | {metrics['success_rate']:.1%} | {'✅' if metrics['success_rate'] >= 0.90 else '⚠️'} |
| Failed Images | {metrics['failed']} | {'✅' if metrics['failed'] == 0 else '⚠️'} |
| Avg Processing Time | {metrics['processing_time']['average']:.3f}s | {'✅' if metrics['processing_time']['average'] < 2.0 else '⚠️'} |

---

## 🎯 Quality Metrics

### Readiness Score
| Statistic | Value |
|-----------|-------|
| Average | {metrics['quality_metrics']['readiness_score']['average']:.3f} |
| Std Dev | {metrics['quality_metrics']['readiness_score']['std']:.3f} |
| Min | {metrics['quality_metrics']['readiness_score']['min']:.3f} |
| Max | {metrics['quality_metrics']['readiness_score']['max']:.3f} |

### Other Metrics
| Metric | Average Value |
|--------|---------------|
| RMS Contrast | {metrics['quality_metrics']['rms_contrast']['average']:.2f} |
| Edge Density | {metrics['quality_metrics']['edge_density']['average']:.4f} |
| Laplacian Variance | {metrics['quality_metrics']['laplacian_variance']['average']:.2f} |

---

## 🚦 Quality Flags

| Flag | Pass Count | Pass Rate | Status |
|------|------------|-----------|--------|
| Sufficient Contrast | {metrics['quality_flags']['sufficient_contrast']['count']}/{metrics['successful']} | {metrics['quality_flags']['sufficient_contrast']['rate']:.1%} | {'✅' if metrics['quality_flags']['sufficient_contrast']['rate'] >= 0.90 else '⚠️'} |
| Sufficient Edges | {metrics['quality_flags']['sufficient_edges']['count']}/{metrics['successful']} | {metrics['quality_flags']['sufficient_edges']['rate']:.1%} | {'✅' if metrics['quality_flags']['sufficient_edges']['rate'] >= 0.90 else '⚠️'} |
| Meets Readiness | {metrics['quality_flags']['meets_readiness']['count']}/{metrics['successful']} | {metrics['quality_flags']['meets_readiness']['rate']:.1%} | {'✅' if metrics['quality_flags']['meets_readiness']['rate'] >= 0.90 else '⚠️'} |

---

## 📈 Baseline Comparison

**Target**: datasets/train/ baseline = {comparison['baseline_readiness']:.1%}

| Metric | Value | Status |
|--------|-------|--------|
| Baseline Readiness | {comparison['baseline_readiness']:.1%} | - |
| Achieved Readiness | {comparison['achieved_readiness']:.1%} | - |
| Difference | {comparison['difference']:+.1%} | {'✅' if comparison['difference'] >= 0 else '⚠️'} |
| % of Baseline | {comparison['percentage_of_baseline']:.1f}% | {'✅' if comparison['percentage_of_baseline'] >= 90 else '⚠️'} |
| Meets Target (≥90%) | {'Yes' if comparison['meets_target'] else 'No'} | {'✅' if comparison['meets_target'] else '❌'} |

---

## ⏱️ Performance Statistics

| Metric | Value |
|--------|-------|
| Total Processing Time | {metrics['processing_time']['total']:.2f}s |
| Average Time per Image | {metrics['processing_time']['average']:.3f}s |
| Min Time | {metrics['processing_time']['min']:.3f}s |
| Max Time | {metrics['processing_time']['max']:.3f}s |

---

## ❌ Failed Images

"""

    if metrics['failed'] > 0:
        md_content += "| Index | Error Message |\n"
        md_content += "|-------|---------------|\n"
        for failed in metrics['failed_images']:
            md_content += f"| {failed['index']} | {failed['error']} |\n"
    else:
        md_content += "**No failed images** ✅\n"

    md_content += "\n---\n\n## ✅ Validation Status\n\n"

    # Overall validation status
    validation_passed = (
        metrics['success_rate'] >= 0.90 and
        metrics['processing_time']['average'] < 2.0 and
        comparison['meets_target']
    )

    if validation_passed:
        md_content += "**Status**: ✅ **PASSED** - All validation criteria met\n\n"
        md_content += "- Success rate ≥90%\n"
        md_content += "- Processing time <2s per image\n"
        md_content += "- Quality ≥90% of baseline\n"
    else:
        md_content += "**Status**: ⚠️ **NEEDS REVIEW** - Some criteria not met\n\n"
        if metrics['success_rate'] < 0.90:
            md_content += f"- ⚠️ Success rate below 90% ({metrics['success_rate']:.1%})\n"
        if metrics['processing_time']['average'] >= 2.0:
            md_content += f"- ⚠️ Processing time exceeds 2s ({metrics['processing_time']['average']:.3f}s)\n"
        if not comparison['meets_target']:
            md_content += f"- ⚠️ Quality below 90% of baseline ({comparison['percentage_of_baseline']:.1f}%)\n"

    # Save markdown report
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"📄 Markdown report saved: {output_path}")


def main():
    """Main validation workflow"""
    print("=" * 70)
    print("🔬 Preprocessing Pipeline Validation")
    print("=" * 70)

    # Parse arguments
    args = parse_arguments()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    baseline = args.baseline

    print(f"\n📋 Configuration:")
    print(f"   Input: {input_dir}")
    print(f"   Output: {output_dir}")
    print(f"   Baseline: {baseline:.1%}")
    print(f"   Min Success Rate: {args.min_success_rate:.1%}")

    # Validate input directory exists
    if not input_dir.exists():
        print(f"\n❌ Error: Input directory not found: {input_dir}")
        sys.exit(1)

    try:
        # Step 1: Process dataset
        results = validate_dataset(input_dir)

        # Step 2: Calculate aggregate metrics
        metrics = calculate_aggregate_metrics(results)

        # Step 3: Compare with baseline
        comparison = compare_with_baseline(metrics, baseline)

        # Step 4: Generate reports
        print(f"\n📝 Generating reports...")

        json_path = output_dir / "preprocessing_validation.json"
        generate_json_report(metrics, comparison, json_path)

        md_path = output_dir / "preprocessing_validation_report.md"
        generate_markdown_report(metrics, comparison, md_path)

        # Print summary
        print("\n" + "=" * 70)
        print("✅ Validation Complete")
        print("=" * 70)
        print(f"\n📊 Results Summary:")
        print(f"   Success Rate: {metrics['success_rate']:.1%}")
        print(f"   Avg Readiness: {metrics['quality_metrics']['readiness_score']['average']:.3f}")
        print(f"   Avg Time: {metrics['processing_time']['average']:.3f}s")
        print(f"   Baseline Comparison: {comparison['percentage_of_baseline']:.1f}%")

        validation_status = "✅ PASSED" if comparison['meets_target'] and metrics['success_rate'] >= args.min_success_rate else "⚠️ REVIEW"
        print(f"\n   Overall Status: {validation_status}")

    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
