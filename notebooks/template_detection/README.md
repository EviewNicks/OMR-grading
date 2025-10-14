# Template Detection - Jupyter Notebook Prototyping

**Week 6 - Phase 1**: Algorithm Development and Parameter Tuning

## Overview

Folder ini berisi 4 Jupyter notebooks untuk prototyping template detection algorithms. Tujuan: mengembangkan dan membandingkan 3 metode deteksi grid jawaban OMR (Optical Mark Recognition), kemudian mengintegrasikannya menjadi pipeline lengkap.

## Notebook Descriptions

### 01_contour_detection.ipynb
**Metode**: Hierarchical Contour Analysis

**Tujuan**: Deteksi grid jawaban berdasarkan analisis kontur hierarkis
- Ekstraksi kontur dengan `cv2.findContours()`
- Filtering geometris: aspect ratio, area, rectangularity
- Validasi struktur nested rectangles
- Confidence scoring

**Dataset**: `datasets/train/` (10 pre-preprocessed images)

**Output**: Optimal contour detection parameters

---

### 02_hough_detection.ipynb
**Metode**: Hough Line Transform

**Tujuan**: Rekonstruksi grid dari deteksi garis horizontal dan vertikal
- Edge detection dengan Canny
- Line detection dengan `cv2.HoughLines()`
- Filtering garis horizontal/vertikal
- Grid reconstruction dari intersections
- Confidence scoring

**Dataset**: `datasets/train/` (10 pre-preprocessed images)

**Output**: Optimal Hough parameters + grid reconstruction logic

---

### 03_template_matching.ipynb
**Metode**: Multi-Scale Template Matching

**Tujuan**: Template matching dengan rotation dan scale invariance
- Generate 3x20 OMR grid template
- Multi-scale variants (0.7x - 1.3x)
- Rotation variants (-20° to +20°)
- Correlation-based matching dengan `cv2.matchTemplate()`
- Confidence scoring

**Dataset**: `datasets/train/` (10 pre-preprocessed images)

**Output**: Template database + optimal matching parameters

---

### 04_fusion_and_segmentation.ipynb
**Metode**: Multi-Method Fusion + Complete Pipeline

**Tujuan**: Gabungkan 3 metode + complete end-to-end pipeline
- **Part A**: Weighted voting fusion dari 3 metode
- **Part B**: Grid segmentation dengan perspective transform
- **Part C**: Quality assessment (uniformity, clarity, completeness)
- **Part D**: Complete pipeline integration dengan Week 5 preprocessing

**Dataset**: `datasets/test/` (20 raw images) + `src/preprocessing/`

**Output**: Complete detection pipeline + performance benchmarks

---

## Setup Instructions

### 1. Prerequisites

Pastikan dependencies sudah terinstall:

```bash
# Core dependencies
pip install opencv-python numpy matplotlib jupyter

# Verify preprocessing pipeline tersedia
python -c "from src.preprocessing import preprocess_image; print('OK')"
```

### 2. Dataset Preparation

Notebooks 1-3 menggunakan **pre-preprocessed training set**:
```
datasets/train/
├── image_001.jpg
├── image_002.jpg
└── ... (minimal 10 images)
```

Notebook 4 menggunakan **raw test set**:
```
datasets/test/
├── test_001.jpg
├── test_002.jpg
└── ... (minimal 20 images)
```

### 3. Launch Jupyter

```bash
# Dari root project directory
jupyter notebook notebooks/template_detection/
```

---

## Execution Order

**Recommended sequence**:
1. `01_contour_detection.ipynb` → Dapatkan optimal contour parameters
2. `02_hough_detection.ipynb` → Dapatkan optimal Hough parameters
3. `03_template_matching.ipynb` → Dapatkan optimal template matching parameters
4. `04_fusion_and_segmentation.ipynb` → Integrate semua metode + complete pipeline

**Estimated Time**: 2-3 jam per notebook (total ~10-13 jam)

---

## Dataset Strategy

### Notebooks 1-3: Algorithm Development
- **Dataset**: `datasets/train/` (pre-preprocessed by Roboflow)
- **Sample Size**: 10 images
- **Rationale**: Fast iteration, focus on detection algorithm isolation
- **Preprocessing**: SKIP (already done externally)

### Notebook 4: Complete Integration
- **Dataset**: `datasets/test/` (raw images)
- **Sample Size**: 20 images
- **Rationale**: Real-world validation, Week 5 preprocessing integration
- **Preprocessing**: USE `src/preprocessing/` pipeline

---

## Success Metrics

### Technical Targets
- Detection accuracy: **85%+** on test set
- Processing time: **<3 seconds** per image
- Cell extraction quality: **90%+**
- Grid completeness: **90%+** cells extracted

### Academic Requirements
- Code documentation: Bahasa Indonesia
- Markdown explanations: Methodology + results
- Visualizations: Comprehensive comparison grids
- Quantitative analysis: Performance metrics tables

---

## Notebook Structure Pattern

Setiap notebook mengikuti struktur standar:

```markdown
# [Notebook Title]
**Goal**: Single sentence objective
**Dataset**: Source + sample size

## 1. Setup & Imports
[Libraries + helper functions]

## 2. Load Sample Images
[10 images from train/ or test/]

## 3. Implementation
[Core algorithm with inline comments]

## 4. Parameter Experiments
[Test different configurations]

## 5. Visualization
[Comparison grids + performance charts]

## 6. Results Analysis
**Metrics**: [Quantitative table]
**Observations**: [2-3 key insights]
**Optimal Parameters**: [For next phase]

## Success Criteria: [Achievement summary]
```

---

## Expected Outputs

Setelah Phase 1 complete:

1. **Optimal Parameters** untuk 3 detection methods
2. **Performance Comparison** antara 3 metode
3. **Fusion Algorithm** dengan weighted voting
4. **Complete Pipeline** preprocessing → detection → segmentation
5. **Benchmarks** pada 20 test images
6. **Ready for Phase 2** production module conversion

---

## Troubleshooting

### Issue: Import error `from src.preprocessing`
**Solution**: Pastikan running dari root project directory atau tambahkan:
```python
import sys
sys.path.append('../../')
from src.preprocessing import preprocess_image
```

### Issue: Dataset images tidak ditemukan
**Solution**: Verify path relatif dari notebook location:
```python
from pathlib import Path
dataset_path = Path("../../datasets/train/")
assert dataset_path.exists(), f"Dataset not found: {dataset_path}"
```

### Issue: Visualization tidak muncul
**Solution**: Tambahkan magic command di awal notebook:
```python
%matplotlib inline
import matplotlib.pyplot as plt
```

---

## Next Steps

Setelah Phase 1 notebooks complete:
- **Phase 2**: Convert notebooks ke production modules (`src/template_detection/`)
- **Phase 3**: Integration testing + validation + documentation

---

## References

- **Week 5 Preprocessing**: `docs/week5/implementation_summary.md`
- **Week 6 Task Planning**: `docs/task/template_detection_pipeline.md`
- **OpenCV Documentation**: https://docs.opencv.org/
- **Kaggle OMR Dataset**: (dataset source reference)

---

**Author**: Week 6 - Template Detection Team
**Created**: 2025-10-12
**Status**: Phase 1 - Notebook Prototyping
