# Scripts Directory - OMR Grading System

Direktori ini berisi utility scripts untuk setup, validasi, dan maintenance OMR Grading System.

## 📂 Daftar Scripts

### validate_environment.py

**Fungsi:** Comprehensive environment validation untuk OMR development setup

**Deskripsi:**
Script ini melakukan validasi lengkap terhadap environment development, termasuk:
- Validasi instalasi UV package installer
- Pengecekan versi Python (minimal 3.9+)
- Deteksi virtual environment status
- Validasi instalasi dependencies (OpenCV, NumPy, Matplotlib, Pandas)
- Testing fungsionalitas basic OpenCV operations
- Testing fungsionalitas Matplotlib
- Comprehensive reporting dengan success rate

**Usage:**
```bash
# Aktivasi virtual environment terlebih dahulu
.\omr_env\Scripts\activate

# Jalankan validation script
python scripts\validate_environment.py
```

**Expected Output:**
- Success Rate 100%: Environment siap untuk development
- Success Rate 80-99%: Environment mostly ready, perlu review
- Success Rate <80%: Environment validation failed, perlu perbaikan

**Exit Codes:**
- 0: Validation successful (100%)
- 1: Mostly ready (80-99%)
- 2: Validation failed (<80%)

**Dependencies:**
- Python 3.9+
- UV package installer
- Virtual environment (omr_env)
- Core packages: opencv-python, numpy, matplotlib, pandas

**Author:** OMR Development Team
**Created:** Week 1 - Day 1 Implementation
**Last Updated:** Day 1 Environment Setup

### organize_dataset.py

**Fungsi:** Enhanced dataset organization dengan Hybrid Strategy implementation

**Deskripsi:**
Script untuk mengorganisir dataset OMR menggunakan Enhanced Hybrid Strategy yang menggabungkan:
- Professional ML splits (train/test/valid) - mempertahankan existing structure
- Quality-based sub-organization dalam each split untuk academic learning progression
- Curated sample sets untuk development efficiency dan systematic testing

**Features:**
- Quality assessment algorithm dengan multiple metrics (contrast, clarity, brightness consistency)
- Automatic organization ke quality sub-folders (high/medium/low)
- Sample set creation (development, benchmark, testing, challenge)
- Comprehensive reporting dan statistics
- Error handling dan validation
- Backup strategy untuk original dataset

**Usage:**
```bash
# Basic usage
python scripts/organize_dataset.py

# Custom paths
python scripts/organize_dataset.py --source Datasets --target datasets

# With validation
python scripts/organize_dataset.py --validate
```

**Expected Output:**
- Organized dataset structure dengan ML splits + quality organization
- 4 curated sample sets untuk different purposes
- Comprehensive organization report (JSON)
- Statistics dan quality distribution analysis

**Quality Thresholds:**
- High Quality: ≥0.8 (Perfect scans, optimal lighting, clear bubbles)
- Medium Quality: 0.5-0.8 (Good quality dengan minor issues)
- Low Quality: <0.5 (Challenging conditions untuk edge testing)

**Sample Sets Created:**
- development/: 20 best images untuk daily algorithm work
- benchmark/: 15 balanced images untuk performance measurement
- testing/: 30 representative images untuk validation
- challenge/: 10 most difficult images untuk robustness testing

**Dependencies:**
- OpenCV (cv2) untuk image processing
- NumPy untuk numerical operations
- Standard library (pathlib, shutil, json, argparse)

**Author:** OMR Development Team
**Created:** Week 1 - Day 2 Implementation
**Strategy:** Enhanced Hybrid Strategy (ML Standards + Quality-Based Learning)