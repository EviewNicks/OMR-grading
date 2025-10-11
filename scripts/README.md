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

---

## Notebook Structure Scripts (Week 6)

### fix_notebook_structure.py
**Purpose**: Cleanup corrupted cells dari notebook

**Usage**:
```bash
python scripts/fix_notebook_structure.py
```

**Function**:
- Removes corrupted cells (33-48) yang mengalami formatting issues
- Retains clean cells (0-32) up to Section 4.2
- Creates backup sebelum modifications
- Validates structure setelah cleanup

**Output**:
- Cleaned notebook dengan proper structure
- Backup file: `notebooks/week6_template_detection_analysis.ipynb.backup`

---

### add_section_4_5_cells.py
**Purpose**: Add Section 4.3-4.5 (Contour Detection Analysis) cells

**Usage**:
```bash
python scripts/add_section_4_5_cells.py
```

**Cells Added**:
- **Section 4.3**: Visual Step-by-Step Analysis (2 cells)
- **Section 4.4**: Performance Testing & Metrics (2 cells)
- **Section 4.5**: Strengths & Limitations (1 cell)

**Features**:
- Proper cell formatting (source as array of lines)
- 6-stage visualization pipeline
- Statistical analysis dengan confidence intervals
- Academic documentation dalam Bahasa Indonesia

---

### add_section_5_cells.py
**Purpose**: Add Section 5.0-5.5 (Hough Transform Detection) cells

**Usage**:
```bash
python scripts/add_section_5_cells.py
```

**Cells Added**:
- **Section 5.0**: Main Header (1 cell)
- **Section 5.1**: Theoretical Foundation dengan LaTeX (1 cell)
- **Section 5.2**: Implementation & Parameters (3 cells)
- **Section 5.3**: Visualization of Process (2 cells)
- **Section 5.4**: Performance Testing & Comparison (2 cells)
- **Section 5.5**: Strengths & Limitations (1 cell)

**Features**:
- Mathematical formulas dengan LaTeX notation
- 8-stage visualization pipeline
- Comparative analysis (Contour vs Hough)
- Statistical significance testing (t-test)

---

### fix_cell_32_key_error.py
**Purpose**: Fix KeyError in Section 4.3 caused by inconsistent dictionary key naming

**Usage**:
```bash
python scripts/fix_cell_32_key_error.py
```

**Problem**:
- Cell [32] stored data dengan key `'original_image'`
- Cell [34] tried to access dengan key `'original'`
- Menyebabkan KeyError saat execute visualization

**Solution**:
- Changes key name dari `'original_image'` ke `'original'` di Cell [32]
- Ensures consistency dengan Cell [34] expectation

**Output**:
```
Fixing Cell [32] key name issue...
============================================================
Line 16: Fixed 'original_image' to 'original'

Cell [32] fixed successfully!
   Changed: 'original_image' to 'original'
   Notebook saved.
============================================================
```

**Documentation**: See `docs/cell_32_keyerror_fix_summary.md` for detailed analysis

---

### fix_notebook_errors.py
**Purpose**: Automated fix untuk critical errors di Week 6 notebook (AttributeError & KeyError)

**Usage**:
```bash
python scripts/fix_notebook_errors.py
```

**Problems Fixed**:
1. **Cell 34 - AttributeError**: `detection.grid_contour` tidak exist
   - Fix: Gunakan `detection.grid_coordinates` untuk calculate area
   - Area calculation: `(x2 - x1) * (y2 - y1)` dari bounding box

2. **Cell 36 - KeyError**: `result['processing_time']` tidak ada di dictionary
   - Fix: Access dari detection object: `det.processing_time`

3. **Cell 60 - KeyError**: Same issue sebagai Cell 36
   - Fix: Consistent attribute access pattern

**Features**:
- JSON-based notebook manipulation
- Pattern-based automatic fixes
- Comprehensive error detection scan
- Windows-compatible output (no Unicode issues)
- Built-in verification
- Change tracking and reporting

**Output Example**:
```
[1/3] Checking Cell 34...
   [OK] Fixed: grid_contour -> grid_coordinates calculation

[2/3] Checking Cell 36...
   [OK] Fixed: result['processing_time'] -> det.processing_time

[3/3] Checking for additional processing_time errors...
   Found error in Cell 60...
   [OK] Fixed Cell 60: result['processing_time'] -> det.processing_time

[SUCCESS] Changes applied: 3
   1. Cell 34: Fixed grid_contour AttributeError
   2. Cell 36: Fixed processing_time KeyError
   3. Cell 60: Fixed processing_time KeyError
```

**Documentation**:
- Analysis Report: `docs/dev/analyze.md`
- Verification Report: `docs/dev/fix_verification_report.md`

**Testing**:
```bash
# After running fix, verify in Jupyter:
# 1. Restart kernel
# 2. Run all cells
# 3. Verify Cell 34, 36, 60 execute without errors
```

---

### validate_notebook_structure.py
**Purpose**: Validate Week 6 Notebook structure and formatting

**Usage**:
```bash
python scripts/validate_notebook_structure.py
```

**Function**:
- Validates notebook structure completeness
- Checks all expected sections (1.x, 2.x, 4.x, 5.x)
- Verifies cell formatting (no character-per-line corruption)
- Provides comprehensive validation report

**Output**:
- Section headers found
- Validation checks for each section
- Cell format validation
- Overall PASS/FAIL status

---

## Week 6 Notebook Restructure Workflow

### Complete Process:

```bash
# 1. Cleanup corrupted cells
python scripts/fix_notebook_structure.py

# 2. Add Section 4 cells (Contour Detection)
python scripts/add_section_4_5_cells.py

# 3. Add Section 5 cells (Hough Transform)
python scripts/add_section_5_cells.py

# 4. Verify final structure
python -c "import json; data=json.load(open('notebooks/week6_template_detection_analysis.ipynb')); print(f'Total cells: {len(data[\"cells\"])}')"
```

### Expected Cell Count:
- Original: 49 cells (dengan corruption)
- After cleanup: 33 cells (clean)
- After Section 4: 38 cells
- After Section 5: 48 cells (final)

---

## Related Documentation

- **Restructure Summary**: `docs/notebook_restructure_summary.md`
- **Task Plan**: `docs/task/task_notebook_implementation.md`
- **Week 6 Overview**: `docs/task/task_template_detection.md`