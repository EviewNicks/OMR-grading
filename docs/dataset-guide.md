# Dataset Guide - Kaggle OMR Dataset

**Dataset Source:** [Kaggle OMR Dataset](https://www.kaggle.com/datasets/collinslemeke/omr-dataset)
**Dataset Size:** ~500+ images (various formats and conditions)
**Purpose:** Training dan testing untuk OMR bubble detection system

---

## 📊 Dataset Overview

### **Dataset Description:**

Koleksi gambar lembar jawaban OMR (Optical Mark Recognition) dengan berbagai kondisi dan kualitas. Dataset ini ideal untuk academic project karena menyediakan variasi yang cukup untuk testing algorithm image processing.

### **Dataset Characteristics:**

- **Format:** JPG, PNG images
- **Resolution:** Bervariasi (800x600 hingga 2000x1500 pixels)
- **Quality:** Good, fair, poor lighting conditions
- **Template Variations:** Multiple OMR sheet layouts
- **Total Size:** ~200MB compressed

### **Typical Use Cases:**

- ✅ Algorithm development dan testing
- ✅ Performance benchmarking
- ✅ Edge case identification
- ✅ Academic research dan demonstration

---

## 📥 Dataset Download & Setup

### **Step 1: Kaggle Account Setup**

1. **Create Kaggle Account:** [kaggle.com](https://kaggle.com)
2. **Verify Account:** Via email verification
3. **API Setup** (optional for automated download):

   ```bash
   # Install Kaggle CLI
   pip install kaggle

   # Get API credentials
   # Go to kaggle.com → Account → Create API Token
   # Download kaggle.json and place in ~/.kaggle/
   ```

### **Step 2: Download Dataset**

#### **Option A: Web Download (Recommended)**

1. Visit: [Kaggle OMR Dataset](https://www.kaggle.com/datasets/collinslemeke/omr-dataset)
2. Click **"Download"** (requires login)
3. Extract ZIP file ke project directory

#### **Option B: CLI Download**

```bash
# Using Kaggle CLI
kaggle datasets download -d collinslemeke/omr-dataset

# Extract
unzip omr-dataset.zip -d datasets/kaggle_omr/
```

#### **Option C: Python Script**

```python
# download_dataset.py
import kaggle
import zipfile
import os

def download_omr_dataset():
    """Download and extract Kaggle OMR dataset"""

    # Download dataset
    kaggle.api.dataset_download_files(
        'collinslemeke/omr-dataset',
        path='datasets/',
        unzip=True
    )

    print("✅ Dataset downloaded successfully!")
    print("📁 Location: datasets/omr-dataset/")

if __name__ == "__main__":
    download_omr_dataset()
```

### **Step 3: Organize Dataset Structure**

```bash
# Recommended directory structure
datasets/
├── kaggle_omr/              # Raw downloaded data
│   ├── good_quality/        # High quality images
│   ├── poor_quality/        # Low quality images
│   ├── rotated/            # Rotated/skewed images
│   └── metadata.csv        # Image annotations (if available)
├── processed/              # Preprocessed images
│   ├── train/              # Training set (70%)
│   ├── validation/         # Validation set (15%)
│   └── test/               # Test set (15%)
├── annotations/            # Manual annotations
│   ├── answer_keys/        # Ground truth answers
│   └── bubble_locations/   # Bubble coordinate annotations
└── sample_for_demo/        # Selected images for demonstration
    ├── easy_cases/         # Clear, good quality
    ├── medium_cases/       # Moderate challenges
    └── hard_cases/         # Difficult edge cases
```

---

## Overview

Curated dataset untuk demonstrasi sistem OMR grading dengan berbagai tingkat kesulitan.

## Categories

### Easy (Mudah)

- High quality images
- Good lighting dan contrast
- Template clearly visible
- Expected accuracy: >90%

### Medium (Sedang)

- Good quality dengan minor challenges
- Slight lighting variations
- Minor rotation/skew
- Expected accuracy: 80-90%

### Hard (Sulit)

- Challenging conditions
- Poor lighting atau low contrast
- Significant rotation atau distortion
- Expected accuracy: 60-80%

### Edge Cases (Kasus Ekstrem)

- Very difficult conditions
- Multiple challenges combined
- Testing system limits
- Expected accuracy: <60%

## Usage

```python
# Load demo image
import cv2
img = cv2.imread('datasets/demo/easy/demo_easy_01.jpg')

# Process with your OMR algorithm
result = omr_processor.process(img)
```

## Answer Keys

Answer keys untuk demo images tersedia di folder `answer_keys/`.
"""

        with open(self.demo_path / "README.md", 'w') as f:
            f.write(demo_readme)

# Usage

if **name** == "**main**":
preparer = DemoDataPreparer()
preparer.prepare_demo_dataset()

````

---

## 📋 Dataset Usage Best Practices

### **Academic Project Guidelines**

#### **1. Data Organization**
```bash
# Recommended structure for academic project
datasets/
├── raw/                    # Original Kaggle data (don't modify)
├── processed/             # Preprocessed for algorithm development
├── demo/                  # Curated samples for presentation
├── test_results/          # Algorithm output samples
└── documentation/         # Analysis and reports
````

#### **2. Version Control**

```bash
# .gitignore for dataset
datasets/raw/              # Too large for Git
datasets/processed/        # Generated files
*.jpg
*.png
!datasets/demo/sample_*.jpg  # Keep small demo samples
```

#### **3. Documentation Requirements**

- **Dataset source citation**
- **Preprocessing steps documentation**
- **Performance benchmarks**
- **Known limitations and edge cases**

### **Performance Optimization Tips**

#### **1. Image Loading Optimization**

#### **2. Batch Processing**

### **Quality Assurance Checklist**

- [ ] ✅ Dataset downloaded dan verified
- [ ] ✅ Data exploration completed
- [ ] ✅ Preprocessing pipeline established
- [ ] ✅ Train/validation/test split done
- [ ] ✅ Ground truth annotations prepared
- [ ] ✅ Demo dataset curated
- [ ] ✅ Performance benchmarks established
- [ ] ✅ Documentation completed

---

## 🔗 Integration with Project

### **Connect to Main System**

---

**Dataset Status:** Ready for Academic Use
**Total Setup Time:** ~2 hours including download
**Recommended Usage:** Development + Testing + Demo

**🎓 Perfect foundation untuk academic OMR project dengan real-world data!**
