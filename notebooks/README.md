# Week 6 Notebooks - Organization Guide

## 📁 File Structure

### Active Notebooks (Use These)

#### 1. `week6_part1_foundation_integration.ipynb`
**Scope**: Sections 1-3
- Section 1: Project Overview & Objectives
- Section 2: Environment Setup & Configuration
- Section 3: Week 5 Integration Validation

**Cells**: 30 cells (28 original + 2 state management)
**Size**: ~43% of original notebook
**Output**: `results/part1_foundation_state.pkl` (state file untuk Part 2)

**Execution**:
```bash
# Run di Jupyter
jupyter notebook week6_part1_foundation_integration.ipynb

# Atau via command line
jupyter nbconvert --execute --to notebook --inplace week6_part1_foundation_integration.ipynb
```

---

#### 2. `week6_part2_detection_methods.ipynb`
**Scope**: Sections 4-6
- Section 4: Detection Method 1 - Contour-Based Grid Detection
- Section 5: Hough Transform Detection
- Section 6: Detection Method 3 - Template Matching Multi-Scale

**Cells**: 41 cells (4 header/state loading + 37 original)
**Size**: ~57% of original notebook
**Input**: `results/part1_foundation_state.pkl` (dari Part 1)

**Prerequisites**: Part 1 harus dijalankan terlebih dahulu!

**Execution**:
```bash
# Pastikan Part 1 sudah dijalankan
# Check state file exists
ls results/part1_foundation_state.pkl

# Run Part 2
jupyter notebook week6_part2_detection_methods.ipynb
```

---

### Archive/Backup Notebooks

#### `week6_template_detection_analysis.ipynb`
**Status**: ❌ DEPRECATED - Original monolithic notebook (65 cells, 42K tokens)
**Reason**: Too large for optimal Jupyter performance
**Replaced by**: Part 1 + Part 2 notebooks
**Keep for**: Reference dan backup purposes

#### `week6_backup_template_detection_analysis.ipynb`
**Status**: Backup copy (if exists)

---

## 🔄 Execution Workflow

### Step-by-Step Execution Order

```
┌──────────────────────────────────────────────────────────┐
│ STEP 1: Run Part 1                                       │
│ File: week6_part1_foundation_integration.ipynb           │
│                                                           │
│ → Restart kernel                                         │
│ → Run all cells                                          │
│ → Verify state file created: results/part1_foundation... │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ STEP 2: Run Part 2                                       │
│ File: week6_part2_detection_methods.ipynb                │
│                                                           │
│ → Restart kernel                                         │
│ → Run all cells                                          │
│ → State loading cell akan load dari Part 1               │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ RESULT: Complete Week 6 Analysis (Sections 1-6)         │
│                                                           │
│ ✅ Foundation & Integration validated                    │
│ ✅ Detection methods analyzed                            │
│ ✅ Ready untuk Section 7-12 implementation               │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 State Management

### Part 1 → Part 2 State Transfer

**Saved Variables** (di `results/part1_foundation_state.pkl`):

```python
state_part1 = {
    'config': config,                      # Configuration object
    'sample_images': sample_images,        # List of sample images
    'sample_metadata': sample_metadata,    # Dict of image metadata
    'preprocessed_images': preprocessed_images,  # List of preprocessed results
    'quality_metrics': quality_metrics,    # Dict of quality scores
    'dataset_path': dataset_path,          # Path to dataset
    'output_dir': output_dir,              # Path to output directory
}
```

**Loading in Part 2**:

```python
import pickle
with open('results/part1_foundation_state.pkl', 'rb') as f:
    state_part1 = pickle.load(f)

# Variables automatically extracted
config = state_part1['config']
sample_images = state_part1['sample_images']
# ... etc
```

---

## 🎯 Performance Comparison

| Metric | Original | Part 1 | Part 2 |
|--------|----------|--------|--------|
| **Total Cells** | 65 | 30 | 41 |
| **File Size** | ~42K tokens | ~20K tokens | ~22K tokens |
| **Load Time** | Slow | Fast ⚡ | Fast ⚡ |
| **Navigation** | Difficult | Easy ✅ | Easy ✅ |
| **Execution** | Heavy | Moderate | Moderate |

**Benefits**:
- ✅ Better Jupyter performance
- ✅ Easier navigation dan debugging
- ✅ Better version control (smaller diffs)
- ✅ Modular development workflow
- ✅ Reduced kernel memory pressure

---

## 🚨 Troubleshooting

### Error: State file not found

```
FileNotFoundError: results/part1_foundation_state.pkl
```

**Solution**:
1. Make sure Part 1 sudah dijalankan completely
2. Check direktori `results/` exists
3. Re-run Part 1 sampai state saving cell

### Error: Variable not defined in Part 2

**Solution**:
1. Verify state loading cell executed successfully
2. Check variable names di state_part1 dict
3. Re-run state loading cell

### Error: Kernel restart issues

**Solution**:
1. Restart kernel: Kernel → Restart & Run All
2. Clear outputs: Cell → All Output → Clear
3. Run cells sequentially dari awal

---

## 📝 Notes

### For Development

- **Always run Part 1 first** sebelum Part 2
- **Check state file size** untuk ensure saving berhasil
- **Use "Restart & Run All"** untuk clean execution
- **Commit setelah changes** untuk version control

### For Future Sections (7-12)

Akan dibuat notebook Part 3 untuk Sections 7-12:
- `week6_part3_fusion_testing_results.ipynb`
- Load state dari Part 1 dan Part 2
- Complete full Week 6 implementation

---

## ✅ Validation Checklist

Sebelum melanjutkan ke Section 7-12:

- [ ] Part 1 executes tanpa errors
- [ ] State file `results/part1_foundation_state.pkl` created
- [ ] Part 2 loads state successfully
- [ ] All detection methods (Sections 4-6) complete
- [ ] Visualizations render correctly
- [ ] Performance metrics meet targets

---

**Created**: 2025-10-05
**Purpose**: Performance optimization via notebook splitting
**Reference**: `docs/dev/week6-continuation-strategy.md`
