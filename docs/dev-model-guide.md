# Development Model Guide - OMR Grading System

**Project:** Sistem Penilaian Otomatis Ujian Pilihan Ganda
**Focus:** MVP Implementation dengan Traditional Computer Vision
**Timeline:** Sesuai Academic Schedule (Week 4 - Week 16)
**Current Status:** Week 4 (28/09/2025) - Dataset Finalization Phase

---

## Traditional Computer Vision Model Development (Week 1-4)

### **Objective:** Membangun foundation solid dengan traditional CV methods

**Target Accuracy:** 85-92% (berdasarkan evidence dari academic research)
**Processing Time:** 1-3 detik per image
**Focus:** Deep understanding fundamental image processing techniques

#### **1. Advanced Preprocessing Module Development**

**What:** Implementasi pipeline preprocessing yang robust untuk handling variasi kualitas image
**Why:** Image preprocessing adalah foundation critical untuk accuracy bubble detection
**How:**

- **Week 1-2:** Implementasi adaptive OTSU thresholding dengan quality assessment
- **Quality Assessment Algorithm:** Analyze noise level, contrast, dan lighting conditions
- **Dynamic Parameter Adjustment:** Automatic tuning preprocessing parameters berdasarkan image quality
- **Morphological Operations:** Noise reduction dan contour enhancement optimization
- **Validation Method:** Testing pada diverse image conditions dari Kaggle dataset

**Expected Outcome:** Preprocessing pipeline yang dapat handle 90%+ image variations dengan consistent quality output

#### **2. Multi-Scale Template Detection Implementation**

**What:** Robust algorithm untuk detect answer grid template dengan perspective correction
**Why:** Template detection adalah critical step yang menentukan keakuratan extraction bubble regions
**How:**

- **Contour-Based Detection:** Menggunakan contour analysis untuk identify potential grid regions
- **Aspect Ratio Validation:** Academic template validation berdasarkan TOEFL-style dimensions
- **Perspective Correction:** Automatic correction untuk rotated atau skewed images
- **Confidence Scoring:** Reliability assessment untuk template detection results
- **Multi-Scale Approach:** Handle template dalam berbagai sizes dan orientations

**Expected Outcome:** Template detection success rate 90%+ dengan automatic perspective correction

#### **3. Intelligent Bubble Detection & Classification System**

**What:** Advanced bubble extraction dan classification dengan confidence scoring
**Why:** Core functionality untuk accurate answer determination dengan error handling
**How:**

- **Grid-Based Extraction:** Systematic extraction 60 bubble regions (3x20 grid layout)
- **Dynamic Thresholding:** Adaptive threshold calculation berdasarkan local image conditions
- **Pixel Density Analysis:** Mathematical calculation fill ratio dengan noise filtering
- **Multiple Mark Detection:** Automatic flagging untuk multiple atau unclear marks
- **Confidence Framework:** Statistical confidence scoring untuk each detected answer

**Expected Outcome:** Bubble classification accuracy 85-90% dengan comprehensive error flagging

### **Phase 1 Validation & Testing Framework**

**Testing Methodology:**

- **Dataset Segregation:** 70% training/optimization, 30% validation testing
- **Performance Benchmarking:** Systematic accuracy measurement pada diverse image conditions
- **Error Pattern Analysis:** Identification common failure modes untuk future improvement
- **Statistical Validation:** Confidence interval calculation untuk accuracy metrics

---

## =� Current Development Status & Priority

### **Current Week (Week 4: 26/9 - 3/10/2025)**

**Milestone:** Koreksi dan pengambilan ulang Dataset + Latar belakang fix

**Priority Tasks:**

-  Dataset collection dari Kaggle OMR
- = Dataset quality assessment dan sample selection
- � Basic preprocessing experiments dengan sample images
- � Development environment setup validation
- � Paper: Penyusunan Latar belakang tahap 3

**Deliverable:** Dataset berkualitas + draft latar belakang final

---

## <� MVP Development Strategy

### **Strategic Decision: Option A - Traditional Computer Vision MVP**

**Rationale:**

- **Academic Timeline Alignment:** Traditional CV phases sesuai dengan coding milestone mingguan
- **Risk Mitigation:** Proven techniques dengan predictable results
- **Learning Focus:** Deep understanding fundamental image processing
- **Resource Efficiency:** Minimal computational requirements untuk academic environment

**Success Metrics MVP:**

- Processing accuracy: 75-85% (realistic untuk academic prototype)
- Processing time: 3-5 detik per image
- Template detection: 80%+ success rate
- End-to-end functionality: Upload � Process � Results � Export CSV

---

## =' Technical Implementation Roadmap

### **Phase 1: Traditional Computer Vision Implementation (Week 5-9)**

#### **Week 5 (3/10/2025): Preprocessing Mastery**

**Academic Milestone:** Coding 1 (Preprocessing) + Metode tahap 1

**Technical Focus:**

- **Image Quality Assessment:** Implementasi scoring algorithm untuk adaptive processing
- **OTSU Thresholding:** Adaptive threshold selection berdasarkan image characteristics
- **Gaussian Blur:** Noise reduction preprocessing untuk template detection
- **Morphological Operations:** Opening dan closing untuk contour enhancement

**Expected Output:**

- Preprocessing pipeline yang robust untuk 90%+ variasi image
- Metode preprocessing dijelaskan dalam draft paper
- Testing framework untuk validation systematic

#### **Week 6 (10/10/2025): Template Detection & Segmentasi**

**Academic Milestone:** Coding 2 (Segmentasi) + Metode tahap 2

**Technical Focus:**

- **Contour-Based Detection:** Identifikasi potential grid regions menggunakan contour analysis
- **Aspect Ratio Validation:** Template validation berdasarkan TOEFL-style dimensions (3x20 grid)
- **Region of Interest (ROI):** Extraction area jawaban dari detected template
- **Basic Perspective Correction:** Handling rotated atau skewed images

**Expected Output:**

- Template detection success rate 85%+ pada diverse image conditions
- ROI extraction yang accurate untuk bubble regions
- Metode segmentasi dijelaskan dalam draft paper

#### **Week 7 (17/10/2025): Bubble Extraction & Morfologi**

**Academic Milestone:** Coding 3 (Operasi Morfologi) + Metode tahap 3

**Technical Focus:**

- **Grid-Based Extraction:** Systematic extraction 60 bubble regions (layout 3x20)
- **Morphological Processing:** Erosion dan dilation untuk bubble cleanup
- **Noise Filtering:** Removal artifacts dari extraction process
- **Boundary Detection:** Precise bubble boundary identification

**Expected Output:**

- Systematic extraction semua 60 bubble regions
- Clean bubble images untuk classification
- Morphological operations dijelaskan dalam draft paper

#### **Week 8 (24/10/2025): Feature Extraction & Analisis**

**Academic Milestone:** Coding 4 (Ekstraksi Fitur) + Metode tahap 4

**Technical Focus:**

- **Pixel Density Analysis:** Mathematical calculation fill ratio
- **Threshold Determination:** Dynamic threshold untuk filled/empty classification
- **Confidence Scoring:** Statistical confidence framework untuk each detection
- **Feature Vector Creation:** Numeric representation bubble characteristics

**Expected Output:**

- Reliable feature extraction dari bubble regions
- Confidence scoring system untuk quality assessment
- Feature extraction methods dijelaskan dalam draft paper

#### **Week 9 (31/10/2025): Classification & Answer Mapping**

**Academic Milestone:** Coding 5 (Klasifikasi) + Metode tahap 5

**Technical Focus:**

- **Binary Classification:** Filled vs empty bubble determination
- **Answer Mapping:** Convert bubble selections ke format A-E answers
- **Multiple Mark Detection:** Flagging untuk multiple atau unclear marks
- **Scoring Algorithm:** Compare dengan answer key dan calculate results

**Expected Output:**

- Working classification system dengan error handling
- Complete answer extraction dan scoring functionality
- Classification methods dijelaskan dalam draft paper

---

### **Phase 2: Testing & Validation (Week 10-12)**

#### **Week 10-12: Comprehensive System Validation**

**Academic Milestone:** Pengujian, evaluasi, dan penyempurnaan

**Technical Focus:**

- **Performance Testing:** Systematic accuracy measurement pada diverse conditions
- **Error Analysis:** Identification common failure patterns
- **Optimization:** Code performance improvement untuk target metrics
- **Statistical Validation:** Confidence interval calculation untuk accuracy metrics

**Expected Output:**

- Comprehensive testing results dengan statistical analysis
- System optimization untuk target performance metrics
- Draft hasil dan pembahasan untuk academic paper

---

## <� Technical Architecture

### **Backend System Design**

**FastAPI Application Structure:**

- **Upload Endpoint:** Image file handling dengan validation
- **Processing Engine:** Traditional CV pipeline implementation
- **Results API:** JSON response dengan processing results
- **Storage Integration:** Answer keys management dan results persistence

**Core Modules:**

- `image_processor.py`: Main processing pipeline
- `template_detector.py`: Grid detection dan ROI extraction
- `bubble_classifier.py`: Fill detection dan answer mapping
- `scoring_engine.py`: Answer comparison dan result calculation

---

## =� Performance Monitoring & Validation

### **Key Performance Indicators (KPIs)**

**Accuracy Metrics:**

- Question-Level Accuracy: Success rate per individual question
- Overall System Accuracy: End-to-end processing accuracy
- Template Detection Rate: Success percentage template identification
- Bubble Classification Rate: Accuracy bubble fill determination

**Performance Metrics:**

- Processing Time: Average time per image processing
- Resource Utilization: Memory dan CPU usage monitoring
- Error Rate: Frequency processing failures atau unclear results
- User Experience: Interface responsiveness dan reliability

**Testing Framework:**

- Unit Testing: Individual component validation
- Integration Testing: End-to-end pipeline verification
- Performance Testing: Load dan stress testing untuk academic demonstration
- Acceptance Testing: User workflow validation

---

## =� Contingency Planning - Phase 2 ML Enhancement

### **Optional YOLO Integration (Conditional)**

**Decision Criteria:**

- MVP completion status by Week 12
- Available time buffer after interface completion
- Computational resources availability (GPU access)
- Academic performance assessment

**Implementation Approach (If Proceeded):**

- **Week 15-16:** Basic YOLO model training untuk bubble detection
- **Comparative Analysis:** Traditional CV vs ML performance comparison
- **Documentation:** Enhanced academic analysis dengan dual methodology

**Risk Management:**

- MVP remains primary deliverable regardless Phase 2 status
- Phase 2 treated as enhancement, tidak essential untuk academic success
- Documentation includes both successful MVP dan Phase 2 attempts

---

##  Development Checklist

### **Immediate Actions (Week 4 - Current)**

- [ ] Complete dataset quality assessment
- [ ] Select representative sample images untuk testing
- [ ] Setup complete development environment (Python, OpenCV, FastAPI)
- [ ] Create basic project structure dan repository organization
- [ ] Finalize latar belakang paper section

### **Phase 1 Milestones**

- [ ] Week 5: Preprocessing pipeline complete dan tested
- [ ] Week 6: Template detection working dengan 85%+ success rate
- [ ] Week 7: Bubble extraction systematic untuk all 60 regions
- [ ] Week 8: Feature extraction reliable dengan confidence scoring
- [ ] Week 9: Classification working dengan answer mapping complete

### **Integration Milestones**

- [ ] Week 10-12: System testing complete dengan performance validation
- [ ] Week 13-14: Web interface functional dengan end-to-end workflow
- [ ] Week 15-16: Final optimization dan academic demonstration ready

---

## <� Academic Integration

### **Paper Development Alignment**

**Methodology Section:**

- Detailed explanation Traditional CV approach dengan mathematical foundation
- Preprocessing techniques dengan parameter optimization rationale
- Template detection algorithms dengan accuracy validation
- Classification methodology dengan statistical analysis

**Results Section:**

- Performance metrics dengan confidence intervals
- Comparative analysis dengan existing OMR systems (literature review)
- Error analysis dengan improvement recommendations
- Statistical validation dengan academic rigor

**Innovation Assessment:**

- Original implementation dengan academic contribution
- Optimization techniques untuk specific OMR challenges
- Performance improvements dengan systematic approach

---

**Document Status:** MVP Implementation Guide
**Version:** 1.0
**Last Updated:** 28/09/2025
**Focus:** Practical Implementation dengan Academic Timeline Compliance
