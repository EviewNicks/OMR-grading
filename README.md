# OMR Grading System

Sistem grading otomatis untuk lembar jawaban OMR (Optical Mark Recognition) menggunakan Computer Vision dan OpenCV.

## 📋 Project Overview

Project ini dikembangkan dalam timeline 8 minggu dengan fokus progressive learning dan implementation systematic.

**Week 1:** Environment Foundation & Strategic Planning
**Current Status:** Day 1 Implementation - Environment Setup dengan UV Modern

## 🚀 Quick Start

### Prerequisites
- Python 3.9 atau lebih tinggi
- UV package installer (recommended)
- Windows 10/11 (current environment)

### Environment Setup

1. **Install UV Package Installer**
   ```bash
   winget install --id=astral-sh.uv -e
   ```

2. **Clone dan Setup Project**
   ```bash
   git clone <repository-url>
   cd Project_7
   ```

3. **Create Virtual Environment dengan UV**
   ```bash
   uv venv omr_env
   ```

4. **Activate Environment**
   ```bash
   # Windows PowerShell
   .\omr_env\Scripts\Activate.ps1

   # Windows Command Prompt
   omr_env\Scripts\activate.bat
   ```

5. **Install Dependencies**
   ```bash
   uv pip install opencv-python==4.8.1.78 numpy==1.24.3 matplotlib pandas
   ```

6. **Validate Environment**
   ```bash
   python scripts\validate_environment.py
   ```

## 📂 Project Structure

```
Project_7/
├── docs/                    # Project documentation
│   └── week1/              # Week 1 workflow dan planning
├── scripts/                # Utility scripts
│   ├── validate_environment.py  # Environment validation
│   └── README.md           # Scripts documentation
├── src/                    # Source code
│   └── image_processing/   # Core OMR processing modules
├── tests/                  # Test files
├── datasets/               # Dataset organization
│   └── samples/           # Sample datasets
├── claudedocs/            # Analysis dan reports
├── omr_env/               # Virtual environment
└── README.md              # This file
```

## 🔧 Development Workflow

### Week 1 Implementation
- [x] **Day 1:** Environment Foundation & Strategic Planning
  - [x] UV package installer setup
  - [x] Virtual environment creation
  - [x] Dependencies installation
  - [x] Environment validation script
  - [x] Project structure initialization
  - [x] Strategic documentation

- [ ] **Day 2:** Dataset Acquisition & Organization
- [ ] **Day 3:** Dataset Analysis & Characterization
- [ ] **Day 4:** OpenCV Foundation & Basic Experiments
- [ ] **Day 5:** Grid Detection & Bubble Extraction
- [ ] **Day 6:** Performance Optimization & Validation
- [ ] **Day 7:** Documentation & Week 2 Preparation

## 🛠️ Key Technologies

- **Python 3.11+** - Core programming language
- **UV** - Ultra-fast package installer dan dependency management
- **OpenCV 4.8.1** - Computer vision dan image processing
- **NumPy 1.24.3** - Numerical computing
- **Matplotlib 3.10+** - Data visualization
- **Pandas 2.3+** - Data analysis dan manipulation

## 📊 Environment Validation

Gunakan script validation untuk memastikan environment siap:

```bash
python scripts\validate_environment.py
```

**Expected Output:**
- Success Rate 100%: Environment siap untuk development
- Total Checks: 9 (UV, Python, VEnv, Packages, Functionality)

## 🎯 Strategic Decisions

### Dataset Organization Strategy: Quality-Based
- **Rationale:** Optimal untuk academic learning progression
- **Benefit:** Build confidence dengan perfect images terlebih dahulu
- **Timeline:** Selaras dengan 8-week incremental complexity

**Structure:**
- `quality-high/` - Perfect scans, optimal lighting
- `quality-medium/` - Minor issues, development-ready
- `quality-low/` - Challenging cases, robustness testing

## 📖 Documentation

- **Week 1 Workflow:** [`docs/week1/workflow_week1.md`](docs/week1/workflow_week1.md)
- **Scripts Documentation:** [`scripts/README.md`](scripts/README.md)
- **API Documentation:** [`docs/api-documentation.md`](docs/api-documentation.md)

## 🚧 Development Status

**Current Phase:** Week 1 - Day 1 Implementation
**Next Milestone:** Dataset Acquisition & Organization (Day 2)

**Environment Status:** ✅ Validated (100% success rate)
**Dependencies:** ✅ All core packages installed
**UV Integration:** ✅ Implemented dan tested

## 🤝 Contributing

Project ini dikembangkan untuk tujuan akademik dengan focus pada learning progression dan best practices implementation.

## 📝 License

Academic Project - OMR Grading System Development

---

**Last Updated:** Week 1 Day 1 - Environment Setup Completion
**Next Update:** Week 1 Day 2 - Dataset Organization Implementation