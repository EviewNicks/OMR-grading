# Preprocessing Pipeline - Validation Report

**Date**: 2025-10-11 14:23:57
**Dataset**: datasets/test/

---

## 📊 Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total Images | 42 | - |
| Success Rate | 100.0% | ✅ |
| Failed Images | 0 | ✅ |
| Avg Processing Time | 0.056s | ✅ |

---

## 🎯 Quality Metrics

### Readiness Score
| Statistic | Value |
|-----------|-------|
| Average | 0.902 |
| Std Dev | 0.055 |
| Min | 0.810 |
| Max | 1.000 |

### Other Metrics
| Metric | Average Value |
|--------|---------------|
| RMS Contrast | 46.07 |
| Edge Density | 0.0881 |
| Laplacian Variance | 1680.91 |

---

## 🚦 Quality Flags

| Flag | Pass Count | Pass Rate | Status |
|------|------------|-----------|--------|
| Sufficient Contrast | 42/42 | 100.0% | ✅ |
| Sufficient Edges | 42/42 | 100.0% | ✅ |
| Meets Readiness | 42/42 | 100.0% | ✅ |

---

## 📈 Baseline Comparison

**Target**: datasets/train/ baseline = 97.4%

| Metric | Value | Status |
|--------|-------|--------|
| Baseline Readiness | 97.4% | - |
| Achieved Readiness | 90.2% | - |
| Difference | -7.2% | ⚠️ |
| % of Baseline | 92.6% | ✅ |
| Meets Target (≥90%) | Yes | ✅ |

---

## ⏱️ Performance Statistics

| Metric | Value |
|--------|-------|
| Total Processing Time | 2.37s |
| Average Time per Image | 0.056s |
| Min Time | 0.032s |
| Max Time | 0.114s |

---

## ❌ Failed Images

**No failed images** ✅

---

## ✅ Validation Status

**Status**: ✅ **PASSED** - All validation criteria met

- Success rate ≥90%
- Processing time <2s per image
- Quality ≥90% of baseline
