# Phase 2: Production Modules - Task Plan

**Target**: Convert notebooks → production-ready Python modules
**Duration**: 2-3 days
**Strategy**: Systematic (sequential dependencies)
**Output**: FastAPI-ready modules + unit tests + documentation

---

## 🎯 Goal

Convert proven notebook algorithms → production code di `src/preprocessing/`:

```
notebooks/preprocessing/          src/preprocessing/
├── 01_quality_assessment.ipynb  →  quality_assessment.py
├── 02_contrast_enhancement.ipynb →  contrast_enhancement.py
├── 03_morphological_ops.ipynb   →  morphological_ops.py
└── 04_full_pipeline.ipynb       →  pipeline.py
```

---

## 📋 Execution Sequence

```
M1: Quality Assessment → M2: Contrast Enhancement → M3: Morphology → M4: Pipeline
        ↓                        ↓                       ↓               ↓
   Foundation metrics      Proven technique          Noise handling    Integration
```

**Dependencies**: M4 requires M1-M3 complete + tested

---

## 🔧 Module 1: Quality Assessment

**File**: `src/preprocessing/quality_assessment.py`
**Source**: `notebooks/preprocessing/01_quality_assessment.ipynb`
**Duration**: ⏱️ 60 menit

### Implementation Checklist
- [ ] Extract proven algorithms dari notebook
- [ ] Implement core functions:
  * `assess_image_quality(image: np.ndarray) -> QualityMetrics`
  * `calculate_readiness_score(metrics: QualityMetrics) -> float`
  * `generate_quality_flags(metrics: QualityMetrics) -> Dict[str, bool]`
- [ ] Add production standards:
  * Type hints (numpy types, custom dataclasses)
  * Docstrings (Google style, ringkas)
  * Error handling (invalid images, edge cases)
- [ ] Create QualityMetrics dataclass:
```python
@dataclass
class QualityMetrics:
    laplacian_variance: float
    edge_density: float
    rms_contrast: float
    dynamic_range: float
    readiness_score: float
    quality_flags: Dict[str, bool]
```

### Unit Tests
**File**: `tests/preprocessing/test_quality_assessment.py`
- [ ] Test `assess_image_quality()` dengan known images
- [ ] Test `calculate_readiness_score()` edge cases (0, 1, invalid)
- [ ] Test `generate_quality_flags()` threshold logic
- [ ] Coverage target: 90%+

### Documentation
```python
"""Quality Assessment Module

Provides image quality metrics dan readiness scoring untuk preprocessing pipeline.

Functions:
    assess_image_quality: Calculate comprehensive quality metrics
    calculate_readiness_score: Generate weighted readiness score
    generate_quality_flags: Binary quality indicators

Example:
    >>> metrics = assess_image_quality(image)
    >>> score = calculate_readiness_score(metrics)
    >>> print(f"Readiness: {score:.2f}")
"""
```

✅ **Success**: Module imports cleanly + unit tests pass + docstrings complete

---

## 🔧 Module 2: Contrast Enhancement

**File**: `src/preprocessing/contrast_enhancement.py`
**Source**: `notebooks/preprocessing/02_contrast_enhancement.ipynb`
**Duration**: ⏱️ 60 menit
**Depends on**: M1 (untuk quality validation)

### Implementation Checklist
- [ ] Extract optimal technique dari notebook results
- [ ] Implement core functions:
  * `apply_clahe(image: np.ndarray, clip_limit: float, tile_size: Tuple[int, int]) -> np.ndarray`
  * `apply_histogram_equalization(image: np.ndarray) -> np.ndarray`
  * `normalize_rms_contrast(image: np.ndarray, target_contrast: float) -> np.ndarray`
  * `enhance_contrast(image: np.ndarray, method: str, **params) -> np.ndarray`
- [ ] Add configuration dataclass:
```python
@dataclass
class ContrastConfig:
    method: str  # "clahe" | "hist_eq" | "rms_norm"
    clip_limit: float = 2.0
    tile_size: Tuple[int, int] = (8, 8)
    target_contrast: float = 70.0
```
- [ ] Integrate M1 metrics untuk validation

### Unit Tests
**File**: `tests/preprocessing/test_contrast_enhancement.py`
- [ ] Test each enhancement technique independently
- [ ] Test `enhance_contrast()` method routing
- [ ] Test parameter validation (clip_limit range, tile_size validity)
- [ ] Test quality improvement (before/after RMS contrast)
- [ ] Coverage target: 90%+

### Documentation
```python
"""Contrast Enhancement Module

Implements proven contrast enhancement techniques untuk preprocessing pipeline.

Supported Methods:
    - CLAHE: Contrast Limited Adaptive Histogram Equalization
    - HistEq: Standard histogram equalization
    - RMS Normalization: Target contrast normalization

Example:
    >>> config = ContrastConfig(method="clahe", clip_limit=2.0)
    >>> enhanced = enhance_contrast(image, config.method, clip_limit=config.clip_limit)
"""
```

✅ **Success**: Optimal technique implemented + measurable improvement + tests pass

---

## 🔧 Module 3: Morphological Operations

**File**: `src/preprocessing/morphological_ops.py`
**Source**: `notebooks/preprocessing/03_morphological_ops.ipynb`
**Duration**: ⏱️ 45 menit

### Implementation Checklist
- [ ] Extract optimal operations dari notebook results
- [ ] Implement core functions:
  * `apply_opening(image: np.ndarray, kernel_size: int) -> np.ndarray`
  * `apply_closing(image: np.ndarray, kernel_size: int) -> np.ndarray`
  * `apply_morphology(image: np.ndarray, operations: List[str], kernel_size: int) -> np.ndarray`
- [ ] Add configuration:
```python
@dataclass
class MorphologyConfig:
    operations: List[str]  # ["opening", "closing"]
    kernel_size: int = 5
    kernel_shape: str = "ellipse"  # "rect" | "ellipse" | "cross"
```

### Unit Tests
**File**: `tests/preprocessing/test_morphological_ops.py`
- [ ] Test opening operation (noise removal)
- [ ] Test closing operation (hole filling)
- [ ] Test combined operations sequence
- [ ] Test edge preservation (compare edge density before/after)
- [ ] Coverage target: 90%+

### Documentation
```python
"""Morphological Operations Module

Noise removal dan shape enhancement untuk preprocessing pipeline.

Operations:
    - Opening: Erosion → Dilation (remove small artifacts)
    - Closing: Dilation → Erosion (fill holes, connect lines)

Example:
    >>> config = MorphologyConfig(operations=["opening", "closing"], kernel_size=5)
    >>> cleaned = apply_morphology(image, config.operations, config.kernel_size)
"""
```

✅ **Success**: Noise removed + edges preserved + parameters optimal

---

## 🔧 Module 4: Pipeline Integration

**File**: `src/preprocessing/pipeline.py`
**Source**: `notebooks/preprocessing/04_full_pipeline.ipynb`
**Duration**: ⏱️ 90 menit
**Depends on**: M1, M2, M3 complete + tested

### Implementation Checklist
- [ ] Compile optimal parameters dari M1-M3
- [ ] Implement pipeline functions:
  * `preprocess_image(image_path: str, config: PreprocessConfig) -> PreprocessResult`
  * `batch_preprocess(image_paths: List[str], config: PreprocessConfig) -> List[PreprocessResult]`
  * `validate_preprocessing(result: PreprocessResult) -> bool`
- [ ] Create unified configuration:
```python
@dataclass
class PreprocessConfig:
    contrast: ContrastConfig
    morphology: MorphologyConfig
    quality_threshold: float = 0.8

@dataclass
class PreprocessResult:
    success: bool
    processed_image: np.ndarray
    metrics: QualityMetrics
    processing_time: float
    error_message: Optional[str] = None
```
- [ ] Add performance tracking (processing time per step)

### Unit Tests
**File**: `tests/preprocessing/test_pipeline.py`
- [ ] Test `preprocess_image()` end-to-end
- [ ] Test `batch_preprocess()` dengan multiple images
- [ ] Test `validate_preprocessing()` quality gates
- [ ] Test error handling (invalid paths, corrupted images)
- [ ] Integration test: full pipeline pada datasets/test/ samples
- [ ] Coverage target: 90%+

### Documentation
```python
"""Preprocessing Pipeline Module

Complete end-to-end preprocessing pipeline untuk OMR grading system.

Pipeline Steps:
    1. Quality Assessment (baseline metrics)
    2. Contrast Enhancement (optimal technique)
    3. Morphological Operations (noise removal)
    4. Validation (quality gates)

Example:
    >>> config = PreprocessConfig(
    ...     contrast=ContrastConfig(method="clahe"),
    ...     morphology=MorphologyConfig(operations=["opening", "closing"])
    ... )
    >>> result = preprocess_image("image.jpg", config)
    >>> print(f"Success: {result.success}, Quality: {result.metrics.readiness_score:.2f}")
"""
```

✅ **Success**: Complete pipeline working + 90%+ success rate + <2s per image

---

## 🧪 Testing Layer

**Duration**: ⏱️ 60 menit
**Depends on**: All modules M1-M4 complete

### Implementation Checklist
- [ ] Create `tests/preprocessing/` structure:
  * `test_quality_assessment.py`
  * `test_contrast_enhancement.py`
  * `test_morphological_ops.py`
  * `test_pipeline.py`
  * `conftest.py` (pytest fixtures untuk sample images)
- [ ] Add pytest fixtures:
```python
@pytest.fixture
def sample_image():
    """Load sample image dari datasets/test/"""
    return cv2.imread("datasets/test/sample.jpg")

@pytest.fixture
def low_quality_image():
    """Sample dengan low contrast untuk testing enhancement"""
    return cv2.imread("datasets/test/low_quality.jpg")
```
- [ ] Run full test suite:
  * `pytest tests/preprocessing/ -v --cov=src/preprocessing`
  * Target: 90%+ coverage + all tests pass

### Performance Benchmarks
**File**: `tests/preprocessing/test_performance.py`
- [ ] Benchmark processing time per module
- [ ] Benchmark complete pipeline (<2s target)
- [ ] Compare dengan notebook results (<10% overhead allowed)

✅ **Success**: All tests pass + 90%+ coverage + performance maintained

---

## 📄 Documentation Layer

**Duration**: ⏱️ 45 menit

### src/preprocessing/README.md
**Content**:
```markdown
# Preprocessing Module

Production preprocessing pipeline untuk OMR Grading System.

## Modules
- `quality_assessment`: Image quality metrics dan readiness scoring
- `contrast_enhancement`: CLAHE dan histogram equalization
- `morphological_ops`: Noise removal dengan edge preservation
- `pipeline`: Complete preprocessing pipeline integration

## Usage
[Include basic usage example]

## Configuration
[Document PreprocessConfig options]

## Performance
- Processing time: <2 seconds per image
- Success rate: 90%+ (quality_score >= 0.8)
- Quality improvement: +30-50% RMS contrast

## Testing
[Document test commands]
```

### Academic Summary
**File**: `docs/week5/preprocessing_implementation_summary.md`
**Content** (Indonesian, ringkas):
```markdown
# Implementasi Preprocessing Pipeline - Ringkasan

## Metodologi
Pipeline berbasis evidence dari analisis datasets/train:
- Quality Assessment: Laplacian variance, edge density, RMS contrast
- Contrast Enhancement: CLAHE dengan clip_limit=2.0, tile_size=(8,8)
- Morphological Operations: Opening + Closing, kernel_size=5

## Hasil Phase 1 (Notebooks)
[Compile results dari 4 notebooks - 2-3 bullet points each]

## Hasil Phase 2 (Production)
- Modules: 4 production-ready Python modules
- Testing: 90%+ coverage, all tests pass
- Performance: <2s per image, 90%+ success rate
- Quality improvement: +X% average RMS contrast

## Kesimpulan
Pipeline siap untuk Week 6 template detection integration.
```

✅ **Success**: Documentation complete + academic summary ready

---

## ✅ Validation Gates

**Before marking Phase 2 complete, verify:**

| Gate | Criteria | Command |
|------|----------|---------|
| **Import** | All modules import cleanly | `python -c "from src.preprocessing import *"` |
| **Type Safety** | No type errors | `mypy src/preprocessing/ --strict` |
| **Linting** | Code quality pass | `flake8 src/preprocessing/` |
| **Testing** | 90%+ coverage + pass | `pytest tests/preprocessing/ --cov` |
| **Performance** | <2s per image | Run benchmark test |
| **FastAPI** | Import compatible | `python -c "from src.preprocessing.pipeline import preprocess_image"` |

---

## 🎯 Phase 2 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Modules complete | 4/4 | ✅ All import cleanly |
| Unit tests | 90%+ coverage | 📊 pytest report |
| Type safety | mypy --strict pass | 🔧 No type errors |
| Performance | <2s per image | ⏱️ Benchmark test |
| Documentation | Complete | 📄 README + docstrings |
| Academic summary | Ready | 📄 methodology_preprocessing.md updated |

---

## 📦 Deliverables

**Production Modules** (4 files):
- `src/preprocessing/quality_assessment.py`
- `src/preprocessing/contrast_enhancement.py`
- `src/preprocessing/morphological_ops.py`
- `src/preprocessing/pipeline.py`

**Testing** (4 test files + fixtures):
- `tests/preprocessing/test_*.py`
- `tests/preprocessing/conftest.py`

**Documentation**:
- `src/preprocessing/README.md` (usage + API reference)
- `docs/week5/preprocessing_implementation_summary.md` (academic)

**Configuration**:
- Optimal parameters embedded in dataclasses
- FastAPI-ready structure

---

## 🚀 Next Steps After Phase 2

✅ Phase 2 Complete → Week 6: Template Detection Integration
- FastAPI endpoint: `POST /api/preprocess-image`
- Integration dengan template detection pipeline
- Academic paper: Methodology section complete

---

**Ready to Start?**
Begin dengan Module 1: `src/preprocessing/quality_assessment.py`

**Execution Pattern**:
```
M1 → Test M1 → M2 → Test M2 → M3 → Test M3 → M4 → Test M4 → Validation Gates
```
