# Week 5: Preprocessing Mastery - Simple Task Plan

**Project**: OMR Grading System
**Duration**: 7 hari (3/10/2025 - 9/10/2025)
**Target**: Preprocessing pipeline + Academic Milestone (Coding 1 + Metode tahap 1)

---

## 🎯 Goals

- Build preprocessing pipeline: Quality Assessment → OTSU → Gaussian Blur → Morphology
- Process 90%+ image types dengan <2 detik per image
- Complete academic deliverable: working code + methodology paper section

---

## 📅 Daily Tasks

### **Setup + Image Quality**

**What to do:**

- Setup notebooks/ folder structure
- Create Day1_quality_assessment.ipynb
- Implement quality scoring experiments (blur detection, contrast, lighting)
- Test dengan sample images dan visualize results

**Output:**

- Working image quality assessment notebook
- Visual analysis dan parameter exploration
- Basic testing framework dengan inline visualizations

### **OTSU Thresholding**

**What to do:**

- Create Day2_otsu_thresholding.ipynb
- Implement cv2.threshold(THRESH_OTSU) dengan parameter experiments
- Add adaptive parameter selection dan confidence scoring
- Test pada different lighting conditions dengan visualizations

**Output:**

- OTSU thresholding notebook dengan parameter analysis
- Confidence scoring system dengan visual validation
- Comparative analysis berbagai lighting conditions

### ** Gaussian Blur**

**What to do:**

- Create Day3_gaussian_blur.ipynb
- Implement cv2.GaussianBlur() dengan kernel size experiments
- Add adaptive kernel size selection based on image characteristics
- Integrate dengan OTSU pipeline dan test effectiveness

**Output:**

- Gaussian blur notebook dengan kernel optimization
- Integrated blur-threshold pipeline dengan visual comparisons
- Noise reduction effectiveness measurements

### **Morphological Operations**

**What to do:**

- Create Day4_morphological_ops.ipynb
- Implement cv2.morphologyEx() opening + closing dengan kernel experiments
- Add adaptive kernel optimization untuk different image types
- Complete full pipeline integration dengan all previous steps

**Output:**

- Morphological operations notebook dengan shape enhancement analysis
- Complete preprocessing pipeline integrated dalam notebook
- Visual comparison semua pipeline stages

### **Testing + Validation**

**What to do:**

- Test complete pipeline pada all dataset categories
- Measure performance metrics dan create validation notebook
- Validate 90%+ success target dengan comprehensive testing
- Begin extraction ke .py modules untuk proven algorithms

**Output:**

- Comprehensive testing notebook dengan performance metrics
- Performance analysis dan success rate documentation
- Initial .py module versions untuk stable algorithms

### **Academic Documentation + Conversion**

**What to do:**

- Convert stable algorithms dari notebooks ke backend/preprocessing/ modules
- Write "Metode Preprocessing" paper section (Indonesian) using notebook findings
- Include mathematical explanations dari notebook experiments
- Create before/after examples dari visualization results

**Output:**

- Complete academic methodology section dengan notebook evidence
- Production-ready .py modules extracted dari notebooks
- Mathematical documentation dengan experimental backing

### ** Finalization + API Integration**

**What to do:**

- Complete conversion ke FastAPI-compatible modules
- Create preprocessing API documentation
- Final testing pada both notebook dan module versions
- Prepare Week 6 handoff materials dengan clean API interface

**Output:**

- Ready preprocessing module untuk FastAPI integration
- Complete notebook documentation untuk academic reference
- Week 6 preparation dengan dual format (research + production)

---

## 🔧 Technical Requirements

### Development Approach: Notebook-First Strategy

**Recommended Approach**: Start dengan Jupyter Notebooks untuk rapid prototyping dan akademik documentation, kemudian convert ke FastAPI modules untuk production integration.

### Phase 1: Notebook Development

### Phase 2: Production Modules

### Benefits of Hybrid Approach:

### Key Functions

- `assess_image_quality()` → quality score (0-1)
- `apply_otsu_threshold()` → binary image
- `reduce_noise()` → blurred image
- `enhance_shapes()` → morphologically processed image
- `preprocess_image()` → complete pipeline

---

## 📊 Success Criteria

**Technical:**

- 90%+ images processed successfully
- <2 detik processing time per image
- Measurable quality improvement

**Academic:**

- Working preprocessing module (Coding 1)
- Complete methodology paper section (Metode tahap 1)
- Performance documentation

**Integration:**

- Clean API untuk Week 6
- Preprocessed samples ready
- Testing framework complete

---

- Measure quality improvement quantitatively

### Development Environment Setup

```bash
# Install Jupyter dan dependencies
pip install jupyter opencv-python numpy matplotlib pillow

# Start notebook server
jupyter notebook

# Optional: Install additional visualization tools
pip install seaborn plotly
```

---

**Ready to start Day 1?**
Begin dengan setup backend structure + image quality assessment implementation.
