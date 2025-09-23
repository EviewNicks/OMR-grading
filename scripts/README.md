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