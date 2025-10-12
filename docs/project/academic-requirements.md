# Academic Requirements Checklist - OMR Grading System

**Course:** Pengolahan Citra Digital (Digital Image Processing)
**Project Type:** Tugas Akhir (Final Project)
**Duration:** 8 Weeks
**Assessment Focus:** Technical Implementation + Academic Documentation

---

## 📋 Overview

Panduan lengkap untuk memenuhi semua requirements akademik dalam pengembangan sistem OMR grading sebagai tugas akhir mata kuliah Pengolahan Citra Digital. Checklist ini memastikan project memenuhi standar akademik dan kriteria penilaian.

---

## ⚠️ Batasan Project Saat Ini

### **Scope Terbatas (By Design):**

**Template Format:**
- ✅ **Support:** Single fixed template (3×20 grid = 60 soal)
- ❌ **Tidak Support:** Multi-template flexibility (50, 80 soal, multiple grids)
- 📝 **Alasan:** Academic simplicity - fokus pada CV fundamentals, bukan config engineering

**Target Detection:**
- ✅ **Support:** Answer grid detection ONLY
- ❌ **Tidak Support:** Student information grid, exam metadata, registration marks
- 📝 **Alasan:** Simplified scope untuk academic timeline (8 weeks)

**Processing Capability:**
- ✅ **Support:** Single image processing (1 sheet at a time)
- ❌ **Tidak Support:** Batch processing, real-time processing
- 📝 **Alasan:** Prototype-level implementation, bukan production system

### **Future Enhancement (Optional - Week 10+):**

Jika waktu development tersedia setelah core implementation:
- Template configuration system untuk multi-format support
- Dynamic grid detection untuk flexible layouts
- Multiple grid detection dalam single sheet

**Prioritas:** Solid single-template implementation > Flexible multi-template system

---

## 🎯 Learning Objectives Assessment

### **Primary Learning Objectives:**

- [ ] ✅ **Image Processing Mastery:** Implementasi teknik preprocessing, filtering, dan feature extraction
- [ ] ✅ **Algorithm Development:** Pengembangan algorithm untuk bubble detection dan classification
- [ ] ✅ **Problem Solving:** Solusi teknis untuk real-world problem
- [ ] ✅ **Software Engineering:** Full-stack development dengan best practices
- [ ] ✅ **Academic Writing:** Technical documentation dan research methodology

### **Technical Skills Demonstrated:**

- [ ] ✅ OpenCV untuk image processing
- [ ] ✅ Python programming dengan libraries scientific
- [ ] ✅ Web development (frontend + backend)
- [ ] ✅ Database design dan integration
- [ ] ✅ Testing dan validation methodologies

---

## 📚 Academic Deliverables Checklist

### **1. Technical Implementation (40% of Grade)**

#### **Core System Requirements:**

- [ ] ✅ **Working Prototype:** End-to-end functional system
- [ ] ✅ **Image Processing Pipeline:** Complete OpenCV implementation
- [ ] ✅ **Web Interface:** User-friendly frontend dengan responsive design
- [ ] ✅ **Database Integration:** Proper data storage dan retrieval
- [ ] ✅ **Error Handling:** Robust error management dan user feedback

#### **Code Quality Standards:**

- [ ] ✅ **Clean Code:** Readable, well-structured, dan maintainable
- [ ] ✅ **Documentation:** Comprehensive code comments dalam Bahasa Indonesia
- [ ] ✅ **Modularity:** Proper separation of concerns dan reusable components
- [ ] ✅ **Version Control:** Regular Git commits dengan descriptive messages
- [ ] ✅ **Testing:** Unit tests untuk critical functions

**Code Quality Checklist:**

```python
# Example of well-documented function
def detect_bubbles(image_region, threshold=0.3):
    """
    Mendeteksi bubble yang terisi dalam region gambar tertentu.

    Args:
        image_region (numpy.ndarray): Region gambar yang berisi bubble
        threshold (float): Threshold untuk menentukan bubble terisi (0.0-1.0)

    Returns:
        dict: Hasil deteksi dengan format:
            {
                'answer': str,           # A, B, C, D, E, BLANK, atau INVALID
                'confidence': float,     # Confidence score (0.0-1.0)
                'flag': str atau None    # Flag untuk manual review jika ada
            }

    Raises:
        ValueError: Jika image_region tidak valid
        TypeError: Jika threshold bukan numeric

    Example:
        >>> region = cv2.imread('bubble_region.jpg', cv2.IMREAD_GRAYSCALE)
        >>> result = detect_bubbles(region, threshold=0.3)
        >>> print(result['answer'])  # Output: 'A'
    """
    # Implementation dengan proper error handling
    if image_region is None or image_region.size == 0:
        raise ValueError("Image region tidak valid atau kosong")

    # Algorithm implementation...
```

### **2. Academic Report (30% of Grade)**

#### **Report Structure (20-30 Pages dalam Bahasa Indonesia):**

##### **Halaman Judul**

```
SISTEM PENILAIAN OTOMATIS UJIAN PILIHAN GANDA
MENGGUNAKAN PENGOLAHAN CITRA DIGITAL

Tugas Akhir
Mata Kuliah Pengolahan Citra Digital

Oleh:
[Nama Lengkap]
[NPM]

Program Studi [Program Studi]
Fakultas [Fakultas]
Universitas [Universitas]
[Tahun]
```

##### **Abstract (Bahasa Indonesia + English)**

- [ ] ✅ **Abstrak Bahasa Indonesia** (200-250 kata)
- [ ] ✅ **Abstract English** (200-250 kata)
- [ ] ✅ **Keywords:** 5-7 kata kunci relevante

##### **BAB I: PENDAHULUAN**

- [ ] ✅ **1.1 Latar Belakang**

  - Problem statement yang jelas
  - Motivasi pengembangan sistem
  - Kebutuhan akan automation dalam penilaian

- [ ] ✅ **1.2 Rumusan Masalah**

  - Minimal 3 pertanyaan penelitian spesifik
  - Fokus pada aspek technical dan implementasi

- [ ] ✅ **1.3 Tujuan Penelitian**

  - Tujuan umum dan khusus
  - Outcome yang diharapkan

- [ ] ✅ **1.4 Batasan Masalah**

  - Scope yang jelas dan realistis
  - Limitations yang diakui

- [ ] ✅ **1.5 Manfaat Penelitian**
  - Academic contribution
  - Practical application

##### **BAB II: TINJAUAN PUSTAKA**

- [ ] ✅ **2.1 Optical Mark Recognition (OMR)**

  - Literature review minimal 10 referensi
  - Historical background dan evolution

- [ ] ✅ **2.2 Pengolahan Citra Digital**

  - Theoretical foundation
  - Image preprocessing techniques
  - Feature extraction methods

- [ ] ✅ **2.3 Teknologi Web Modern**

  - Full-stack development overview
  - API design principles
  - Database design concepts

- [ ] ✅ **2.4 Penelitian Terkait**
  - Comparison dengan existing solutions
  - Gap analysis

##### **BAB III: METODOLOGI**

- [ ] ✅ **3.1 Desain Penelitian**

  - Research methodology explanation
  - Development approach (incremental, iterative)

- [ ] ✅ **3.2 Arsitektur Sistem**

  - System architecture diagram
  - Component interaction explanation
  - Technology stack justification

- [ ] ✅ **3.3 Algoritma Pengolahan Citra**
  - Detailed algorithm explanation dengan flowchart
  - Mathematical formulation jika diperlukan
  - Pseudocode untuk key algorithms

```
Contoh Algorithm Documentation:

Algorithm 1: Bubble Detection Pipeline
Input: Grayscale image I, template coordinates T
Output: Answer classification result R

1. Preprocessing Phase:
   a. Apply Gaussian blur dengan kernel 5x5
   b. Adaptive thresholding dengan THRESH_BINARY
   c. Noise reduction dengan morphological operations

2. Template Detection:
   a. Find contours dengan RETR_EXTERNAL
   b. Filter rectangular contours berdasarkan area
   c. Apply perspective transform untuk normalization

3. Bubble Extraction:
   a. Calculate bubble positions berdasarkan grid layout
   b. Extract ROI untuk each bubble
   c. Resize ke standard dimensions

4. Classification:
   a. Calculate fill ratio = black_pixels / total_pixels
   b. Apply threshold untuk determine filled status
   c. Implement rules untuk handle multiple marks

5. Post-processing:
   a. Confidence calculation
   b. Ambiguity detection dan flagging
   c. Result formatting dan validation
```

- [ ] ✅ **3.4 Implementasi Sistem**

  - Development tools dan environment
  - Database schema design
  - API endpoint specification

- [ ] ✅ **3.5 Metodologi Pengujian**
  - Testing strategy
  - Performance metrics definition
  - Validation approach

##### **BAB IV: IMPLEMENTASI DAN PENGUJIAN**

- [ ] ✅ **4.1 Implementasi Sistem**

  - Development process description
  - Key implementation challenges dan solutions
  - Code snippets untuk critical functions

- [ ] ✅ **4.2 Antarmuka Pengguna**

  - UI/UX design explanation
  - User workflow description
  - Screenshots dengan annotations

- [ ] ✅ **4.3 Pengujian Sistem**

  - Test cases dan scenarios
  - Performance benchmarks
  - Accuracy measurements

- [ ] ✅ **4.4 Analisis Hasil**
  - Quantitative results dengan tables dan charts
  - Qualitative analysis
  - Error analysis dan edge cases

##### **BAB V: KESIMPULAN DAN SARAN**

- [ ] ✅ **5.1 Kesimpulan**

  - Summary of achievements
  - Research questions answered
  - Objectives met assessment

- [ ] ✅ **5.2 Kontribusi Penelitian**

  - Technical contributions
  - Academic value

- [ ] ✅ **5.3 Keterbatasan**

  - Honest assessment of limitations
  - Known issues dan workarounds

- [ ] ✅ **5.4 Saran Pengembangan**
  - Future work recommendations
  - Improvement opportunities
  - Research directions

##### **Appendices**

- [ ] ✅ **Appendix A:** Source code listings (key functions)
- [ ] ✅ **Appendix B:** Database schema
- [ ] ✅ **Appendix C:** API documentation
- [ ] ✅ **Appendix D:** Test results data
- [ ] ✅ **Appendix E:** User manual

### **3. Demonstration & Presentation (20% of Grade)**

#### **Live Demo Requirements:**

- [ ] ✅ **Duration:** 10-15 minutes presentation + 5-10 minutes Q&A
- [ ] ✅ **Technical Demo:** Working system demonstration
- [ ] ✅ **Presentation Slides:** Maximum 15 slides
- [ ] ✅ **Preparation:** Backup plans untuk technical issues

#### **Demo Script Structure:**

```
Slide 1: Title & Student Information
Slide 2: Problem Statement & Motivation
Slide 3: System Architecture Overview
Slide 4: Key Technical Challenges
Slide 5: Algorithm Pipeline Explanation
Slide 6: [LIVE DEMO] Answer Key Input
Slide 7: [LIVE DEMO] Image Upload & Processing
Slide 8: [LIVE DEMO] Results Analysis
Slide 9: Performance Metrics & Accuracy
Slide 10: Technical Implementation Highlights
Slide 11: Testing Results & Validation
Slide 12: Conclusions & Achievements
Slide 13: Limitations & Future Work
Slide 14: Questions & Discussion
Slide 15: Thank You & Contact Information
```

#### **Demo Preparation Checklist:**

- [ ] ✅ **Live System:** Deployed dan accessible online
- [ ] ✅ **Test Data:** Various quality sample images prepared
- [ ] ✅ **Answer Keys:** Pre-configured untuk demo scenarios
- [ ] ✅ **Backup:** Video recording jika technical issues
- [ ] ✅ **Timing:** Rehearsed presentation within time limits

### **4. Source Code & Documentation (10% of Grade)**

#### **Code Submission Requirements:**

- [ ] ✅ **Repository:** Clean Git repository dengan proper structure
- [ ] ✅ **README.md:** Comprehensive setup dan usage instructions
- [ ] ✅ **Installation Guide:** Step-by-step setup process
- [ ] ✅ **Dependencies:** Complete requirements.txt atau package.json
- [ ] ✅ **Environment Setup:** Docker atau virtual environment instructions

#### **Repository Structure:**

```
omr-grading-system/
├── README.md                 # Project overview & setup
├── SETUP.md                  # Detailed installation guide
├── requirements.txt          # Python dependencies
├── package.json             # Node.js dependencies
├── docker-compose.yml       # Docker setup (optional)
├── .env.example             # Environment variables template
├── backend/                 # FastAPI backend
│   ├── main.py
│   ├── image_processing/
│   ├── database/
│   └── tests/
├── frontend/                # Next.js frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── docs/                    # Project documentation
│   ├── technical-specs.md
│   ├── api-docs.md
│   └── deployment-guide.md
├── datasets/                # Sample data & annotations
│   ├── demo/
│   └── test_results/
└── scripts/                 # Utility scripts
    ├── deploy.sh
    └── test.sh
```

#### **README.md Template:**

```markdown
# Sistem Penilaian Otomatis Ujian Pilihan Ganda

Tugas Akhir - Pengolahan Citra Digital

## 🎯 Overview

[Brief description dalam 2-3 sentences]

## 🛠️ Tech Stack

- Backend: FastAPI (Python)
- Frontend: Next.js (TypeScript)
- Database: Supabase PostgreSQL
- Image Processing: OpenCV

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### Installation

1. Clone repository
2. Setup backend
3. Setup frontend
4. Configure environment variables
5. Run application

[Detailed step-by-step instructions]

## 📚 Documentation

- [Technical Specifications](docs/technical-specs.md)
- [API Documentation](docs/api-docs.md)
- [Deployment Guide](docs/deployment-guide.md)

## 🧪 Testing

[Instructions untuk running tests]

## 🎥 Demo

[Link to live demo atau video]

## 📊 Performance

- Accuracy: 85% pada test dataset
- Processing Time: 3.2s average
- Supported Formats: JPG, PNG

## 👤 Author

[Your Name] - [NPM] - [Email]

## 📄 License

Academic project untuk [University Name]
```

---

## 🎓 Assessment Criteria

### **Grading Rubric:**

| Criteria                     | Excellent (90-100%)                     | Good (80-89%)                      | Satisfactory (70-79%)         | Needs Improvement (<70%)                 |
| ---------------------------- | --------------------------------------- | ---------------------------------- | ----------------------------- | ---------------------------------------- |
| **Technical Implementation** | Fully functional with advanced features | Working system with minor issues   | Basic functionality achieved  | Significant technical problems           |
| **Code Quality**             | Clean, well-documented, modular         | Good structure with adequate docs  | Acceptable code organization  | Poor code quality or documentation       |
| **Academic Report**          | Comprehensive, well-researched          | Good content with proper structure | Adequate research and writing | Insufficient research or poor writing    |
| **Innovation**               | Creative solutions, original approach   | Good problem-solving skills        | Standard implementation       | Limited innovation or creativity         |
| **Presentation**             | Professional, clear, engaging           | Good presentation skills           | Adequate communication        | Poor presentation or unclear explanation |

### **Minimum Passing Requirements:**

- [ ] ✅ **Functionality:** Basic end-to-end system working
- [ ] ✅ **Accuracy:** >70% bubble detection accuracy
- [ ] ✅ **Documentation:** Complete academic report dengan proper citations
- [ ] ✅ **Code Quality:** Readable code dengan basic comments
- [ ] ✅ **Presentation:** Successful live demonstration

### **Excellence Indicators:**

- [ ] 🌟 **Advanced Features:** Error recovery, confidence scoring, batch processing
- [ ] 🌟 **Performance Optimization:** <2s processing time, efficient algorithms
- [ ] 🌟 **Professional Deployment:** Live system dengan proper monitoring
- [ ] 🌟 **Comprehensive Testing:** Unit tests, integration tests, performance benchmarks
- [ ] 🌟 **Research Contribution:** Novel approach atau significant improvement over existing methods

---

## 📅 Timeline & Milestones

### **Week-by-Week Checklist:**

#### **Week 1-2: Foundation**

- [ ] ✅ Project planning completed
- [ ] ✅ Literature review started
- [ ] ✅ Development environment setup
- [ ] ✅ Dataset acquired dan analyzed

#### **Week 3-4: Core Development**

- [ ] ✅ Image processing pipeline implemented
- [ ] ✅ Basic bubble detection working
- [ ] ✅ Initial accuracy measurements
- [ ] ✅ Database schema designed

#### **Week 5-6: Integration**

- [ ] ✅ Web interface developed
- [ ] ✅ Backend API completed
- [ ] ✅ End-to-end integration working
- [ ] ✅ Initial testing completed

#### **Week 7: Testing & Optimization**

- [ ] ✅ Comprehensive testing conducted
- [ ] ✅ Performance optimization
- [ ] ✅ Bug fixes dan improvements
- [ ] ✅ Documentation started

#### **Week 8: Finalization**

- [ ] ✅ Academic report completed
- [ ] ✅ Presentation prepared
- [ ] ✅ System deployed
- [ ] ✅ Final testing dan validation

### **Submission Deadlines:**

- [ ] ✅ **Draft Report:** Week 7 (for supervisor feedback)
- [ ] ✅ **Final Submission:** Week 8 (all deliverables)
- [ ] ✅ **Presentation:** Week 8 (scheduled by instructor)

---

## 🔍 Quality Assurance Checklist

### **Pre-Submission Review:**

#### **Technical Review:**

- [ ] ✅ System passes all test cases
- [ ] ✅ Performance meets target metrics
- [ ] ✅ Code review completed (self atau peer)
- [ ] ✅ Security considerations addressed
- [ ] ✅ Error handling tested

#### **Academic Review:**

- [ ] ✅ Report proofread untuk grammar dan spelling
- [ ] ✅ Citations properly formatted (APA atau IEEE style)
- [ ] ✅ Figures dan tables properly numbered dan referenced
- [ ] ✅ Technical terms consistent throughout document
- [ ] ✅ Appendices complete dan referenced

#### **Presentation Review:**

- [ ] ✅ Slides checked untuk readability dan consistency
- [ ] ✅ Demo rehearsed dan timing verified
- [ ] ✅ Technical setup tested
- [ ] ✅ Q&A preparation completed
- [ ] ✅ Backup materials prepared

### **Final Submission Package:**

- [ ] ✅ **Academic Report** (PDF format)
- [ ] ✅ **Source Code** (ZIP atau Git repository link)
- [ ] ✅ **Demo Video** (if required)
- [ ] ✅ **Presentation Slides** (PowerPoint atau PDF)
- [ ] ✅ **User Manual** (PDF format)
- [ ] ✅ **Installation Guide** (README.md)

---

## 📞 Support Resources

### **Academic Support:**

- [ ] 📧 **Supervisor Consultation:** Regular meetings untuk progress updates
- [ ] 📚 **Library Resources:** Access to academic databases dan journals
- [ ] 🤝 **Peer Review:** Study group atau pair programming sessions
- [ ] 💻 **Technical Support:** University IT help desk

### **Technical Resources:**

- [ ] 📖 **Documentation:** OpenCV, FastAPI, Next.js official docs
- [ ] 🎥 **Tutorials:** Online courses dan video tutorials
- [ ] 💬 **Communities:** Stack Overflow, Reddit, Discord communities
- [ ] 🔧 **Tools:** GitHub, VS Code, Docker, Postman

### **Common Issues & Solutions:**

#### **Technical Issues:**

```
Issue: OpenCV installation problems
Solution: Use conda atau pre-built wheels
Command: pip install opencv-python-headless

Issue: Database connection errors
Solution: Check environment variables dan network access
Debug: Test connection separately from main application

Issue: Frontend build failures
Solution: Clear node_modules dan package-lock.json
Commands: rm -rf node_modules package-lock.json && npm install

Issue: CORS errors dalam development
Solution: Configure CORS properly dalam FastAPI
Code: app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

#### **Academic Issues:**

- **Writer's Block:** Start dengan outline, write in small sections
- **Citation Management:** Use Zotero atau Mendeley
- **Time Management:** Break large tasks into smaller milestones
- **Technical Writing:** Focus on clarity, use active voice

---

## 🎯 Success Tips

### **Technical Development:**

1. **Start Simple:** Build MVP first, add features incrementally
2. **Test Early:** Implement testing from beginning
3. **Document as You Go:** Don't leave documentation untuk last minute
4. **Version Control:** Regular commits dengan meaningful messages
5. **Performance Focus:** Measure dan optimize continuously

### **Academic Writing:**

1. **Structure First:** Create detailed outline before writing
2. **Citations:** Keep track of sources from beginning
3. **Visual Aids:** Use diagrams dan charts to explain concepts
4. **Peer Review:** Get feedback from classmates atau friends
5. **Professional Tone:** Use formal academic language

### **Presentation Preparation:**

1. **Practice:** Rehearse multiple times
2. **Time Management:** Stick to allocated time slots
3. **Technical Demo:** Have backup plans
4. **Audience Engagement:** Prepare for questions
5. **Professional Appearance:** Dress appropriately

---

## ✅ Final Checklist

### **Before Submission:**

- [ ] ✅ All technical requirements met
- [ ] ✅ Academic report completed dan reviewed
- [ ] ✅ Source code clean dan documented
- [ ] ✅ Presentation materials prepared
- [ ] ✅ Demo environment tested
- [ ] ✅ Backup copies of all materials
- [ ] ✅ Submission deadlines confirmed

### **Academic Integrity:**

- [ ] ✅ Original work dengan proper citations
- [ ] ✅ No plagiarism dalam code atau report
- [ ] ✅ Collaboration properly acknowledged
- [ ] ✅ External resources properly attributed
- [ ] ✅ University academic guidelines followed

### **Professional Development:**

- [ ] ✅ LinkedIn profile updated dengan project
- [ ] ✅ GitHub repository public dan polished
- [ ] ✅ Portfolio entry prepared
- [ ] ✅ Skills dan technologies learned documented
- [ ] ✅ Future learning goals identified

---

**Academic Status:** Ready for Submission
**Estimated Completion Time:** 8 Weeks
**Success Probability:** High (dengan proper planning dan execution)

**🎓 Selamat mengerjakan tugas akhir! Ikuti checklist ini untuk memastikan kesuksesan academic project Anda.**
