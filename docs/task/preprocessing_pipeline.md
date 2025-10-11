# Preprocessing Pipeline - Evidence-Based Implementation

**Project**: OMR Grading System
**Target Dataset**: datasets/test/ (raw images)
**Strategy**: Replicate datasets/train success (97.4% readiness)
**Duration**: 2 phases (Notebook → Production)

---

## 🎯 Goal

Build preprocessing pipeline berdasarkan analysis results:
- **Primary**: Contrast Enhancement (100% detection di datasets/train)
- **Secondary**: Morphological Operations (80% detection)
- **Validation**: Quality assessment framework (97.4% readiness target)

---

## 📊 Evidence-Based Pipeline

Berdasarkan Week 5 analysis results:

```
Quality Assessment → Contrast Enhancement → Morphology → Validation
       ↓                    ↓                   ↓            ↓
   Score 0-1          CLAHE/Hist Eq      Opening/Closing   Ready?
```

**Key Insight**: Minimal blur (0% detection) = preserve edges untuk template detection!

---

## 🔬 Phase 1: Jupyter Notebook Prototyping

### Notebook 1: Quality Assessment Framework
**File**: `notebooks/preprocessing/01_quality_assessment.ipynb`

**What to implement:**
- Load sample images dari datasets/test/
- Implement quality scoring (laplacian variance, edge density, RMS contrast)
- Visualize quality metrics dengan matplotlib
- Test quality flags (sufficient contrast, acceptable blur, sufficient edges)
- Generate quality report untuk sample images

**Success criteria:**
- Quality assessment framework working
- Visual analysis clear dan informative
- Can identify low-quality images

**Output**: Quality scoring system + visual analysis

---

### Notebook 2: Contrast Enhancement
**File**: `notebooks/preprocessing/02_contrast_enhancement.ipynb`

**What to implement:**
- **CLAHE** (Contrast Limited Adaptive Histogram Equalization)
  - Parameter experiments (clipLimit, tileGridSize)
  - Before/after visualization
- **Histogram Equalization**
  - Standard cv2.equalizeHist()
  - Comparison dengan CLAHE
- **RMS Contrast Normalization**
  - Calculate current RMS contrast
  - Normalize to target range (60-80)
- **Comparison Analysis**
  - Visual side-by-side comparison
  - Quality metrics improvement measurement

**Success criteria:**
- Contrast enhancement working
- Clear improvement dalam quality metrics
- Can handle different lighting conditions

**Output**: Optimal contrast enhancement technique + parameters

---

### Notebook 3: Morphological Operations
**File**: `notebooks/preprocessing/03_morphological_ops.ipynb`

**What to implement:**
- **Opening Operation** (erosion → dilation)
  - Remove small noise/artifacts
  - Kernel size experiments (3x3, 5x5)
- **Closing Operation** (dilation → erosion)
  - Fill small holes
  - Connect broken lines
- **Combined Pipeline**
  - Opening untuk noise removal
  - Closing untuk shape enhancement
- **Visual Validation**
  - Before/after comparisons
  - Edge preservation check

**Success criteria:**
- Noise removed without losing bubble details
- Grid lines preserved/enhanced
- No over-processing artifacts

**Output**: Optimal morphological parameters

---

### Notebook 4: Complete Pipeline Integration
**File**: `notebooks/preprocessing/04_full_pipeline.ipynb`

**What to implement:**
- **Pipeline Integration**
  - Quality assessment → Contrast → Morphology → Validation
  - Process multiple test images
  - Batch processing capability
- **Performance Testing**
  - Processing time per image (<2 seconds target)
  - Success rate calculation
  - Quality improvement metrics
- **Visual Documentation**
  - Stage-by-stage visualization
  - Before/after comparisons
  - Quality metrics dashboard
- **Export Results**
  - Save preprocessed images
  - Generate performance report
  - Document optimal parameters

**Success criteria:**
- Complete pipeline working end-to-end
- 90%+ success rate target
- Processing time <2 seconds/image
- Clear quality improvement demonstrated

**Output**:
- Working preprocessing pipeline
- Performance metrics
- Optimal parameter documentation

---

## 🏗️ Phase 2: Production Module Implementation

### Module Structure
```
src/preprocessing/
├── __init__.py
├── quality_assessment.py
├── contrast_enhancement.py
├── morphological_ops.py
├── pipeline.py
└── README.md
```

### Module 1: quality_assessment.py
```python
def assess_image_quality(image: np.ndarray) -> QualityMetrics
def calculate_readiness_score(metrics: QualityMetrics) -> float
def generate_quality_flags(metrics: QualityMetrics) -> Dict[str, bool]
```

### Module 2: contrast_enhancement.py
```python
def apply_clahe(image: np.ndarray, clip_limit: float, tile_size: tuple) -> np.ndarray
def normalize_rms_contrast(image: np.ndarray, target_contrast: float) -> np.ndarray
def enhance_contrast(image: np.ndarray, method: str) -> np.ndarray
```

### Module 3: morphological_ops.py
```python
def apply_opening(image: np.ndarray, kernel_size: int) -> np.ndarray
def apply_closing(image: np.ndarray, kernel_size: int) -> np.ndarray
def apply_morphology(image: np.ndarray, operations: List[str]) -> np.ndarray
```

### Module 4: pipeline.py
```python
def preprocess_image(image_path: str, config: PreprocessConfig) -> PreprocessResult
def batch_preprocess(image_paths: List[str], config: PreprocessConfig) -> List[PreprocessResult]
def validate_preprocessing(result: PreprocessResult) -> bool
```

**Success criteria:**
- Clean, documented Python modules
- Type hints dan docstrings complete
- Unit tests untuk each function
- FastAPI integration ready

---

## 📋 Implementation Checklist

### Phase 1: Notebooks (Days 1-3)
- [ ] Setup notebooks/preprocessing/ directory
- [ ] Implement 01_quality_assessment.ipynb
- [ ] Implement 02_contrast_enhancement.ipynb
- [ ] Implement 03_morphological_ops.ipynb
- [ ] Implement 04_full_pipeline.ipynb
- [ ] Test pada datasets/test/ samples
- [ ] Document optimal parameters
- [ ] Generate performance report

### Phase 2: Production Modules (Days 4-5)
- [ ] Create src/preprocessing/ module structure
- [ ] Convert quality_assessment.py
- [ ] Convert contrast_enhancement.py
- [ ] Convert morphological_ops.py
- [ ] Implement pipeline.py
- [ ] Write unit tests
- [ ] Update src/preprocessing/README.md
- [ ] Verify FastAPI compatibility

### Validation & Documentation (Day 6)
- [ ] Test complete pipeline pada datasets/test/
- [ ] Measure performance metrics
- [ ] Compare dengan datasets/train quality (97.4% target)
- [ ] Document results untuk academic paper
- [ ] Prepare Week 6 handoff

---

## 🎯 Success Metrics

**Technical:**
- Processing time: <2 seconds per image
- Success rate: 90%+ images processed
- Quality score: 0.8+ readiness (match datasets/train)
- Contrast improvement: measurable RMS increase

**Academic:**
- Working Jupyter notebooks dengan visualizations
- Production-ready Python modules
- Performance documentation
- Methodology section ready

**Integration:**
- FastAPI-compatible modules
- Clean API untuk Week 6
- Testing framework complete

---

## 🔧 Technical Requirements

**Development Environment:**
```bash
# Core dependencies
pip install opencv-python numpy matplotlib jupyter

# Visualization tools
pip install seaborn plotly pandas

# Testing tools
pip install pytest pytest-cov
```

**Key OpenCV Functions:**
- `cv2.createCLAHE()` - Contrast enhancement
- `cv2.equalizeHist()` - Histogram equalization
- `cv2.morphologyEx()` - Morphological operations
- `cv2.Laplacian()` - Quality assessment
- `cv2.Canny()` - Edge detection

---

## 📊 Expected Results

**Quality Metrics Improvement:**
- RMS Contrast: +30-50% increase
- Edge Density: maintained or improved
- Laplacian Variance: maintained (sharp edges)
- Overall Readiness: 0.8+ (match datasets/train)

**Pipeline Validation:**
- Before preprocessing: variable quality
- After preprocessing: consistent 90%+ readiness
- Processing speed: 1-2 seconds per image
- Batch capability: 10+ images per run

---

## 🚀 Next Steps After Completion

1. **Week 6 Integration**: Preprocessed images ready untuk template detection
2. **API Endpoint**: FastAPI integration untuk preprocessing service
3. **Academic Documentation**: Methodology section dengan evidence
4. **Performance Optimization**: Further tuning berdasarkan Week 6 feedback

---

**Ready to start Phase 1?**
Begin dengan setup notebooks/preprocessing/ directory + quality assessment implementation.
