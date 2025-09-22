# Week 1 Design Decisions - OMR Grading System

## Dataset Organization Strategy

### Context
The Kaggle OMR dataset contains 500+ images with varying quality, lighting conditions, and template layouts. We need to establish a systematic approach for organizing and sampling these images for development and testing.

### Current Challenge
- Mixed image qualities (high resolution scans vs phone photos)
- Different template layouts and orientations
- Varying lighting conditions and contrast levels
- Need for systematic sampling for development workflow

### Options Considered

#### Option 1: Quality-Based Organization
```
datasets/
├── raw/                 # Original Kaggle dataset
├── quality-high/        # Clean, high-resolution scans
├── quality-medium/      # Acceptable quality with minor issues
├── quality-low/         # Poor quality, challenging images
└── samples/
    ├── development/     # 20 high-quality images for development
    ├── testing/         # 30 mixed-quality images for validation
    └── challenge/       # 10 difficult cases for edge testing
```

#### Option 2: Template-Based Organization
```
datasets/
├── raw/
├── template-standard/   # Standard TOEFL layout
├── template-rotated/    # Rotated or skewed sheets
├── template-partial/    # Partially visible sheets
└── samples/
    ├── by-template/     # Organized by detected template type
    └── by-difficulty/   # Organized by processing difficulty
```

#### Option 3: Development Phase Organization
```
datasets/
├── raw/
├── phase1-setup/       # Perfect images for initial development
├── phase2-robust/      # Images with real-world challenges
├── phase3-edge/        # Edge cases and difficult scenarios
└── samples/
    ├── daily-tests/    # Small set for daily validation
    └── benchmarks/     # Standard set for performance measurement
```

### TODO(human)
Based on your academic timeline and learning objectives, which dataset organization strategy would best support your Week 1-8 development workflow? Consider:
- How you prefer to approach development (perfect cases first vs mixed challenges)
- Your experience level with image processing challenges
- Time constraints and learning goals
- Team collaboration needs (if applicable)

Please implement your chosen organization strategy in the `organize_dataset()` function below and explain your reasoning.

```python
def organize_dataset(kaggle_dataset_path, target_organization_path):
    """
    Organize the Kaggle OMR dataset according to chosen strategy.

    Args:
        kaggle_dataset_path: Path to downloaded Kaggle dataset
        target_organization_path: Path where organized dataset will be created

    TODO(human): Implement organization logic based on your chosen strategy
    """
    # Your implementation here
    pass
```

### Success Criteria
- Clear categorization supporting development workflow
- Sample sets ready for each week's experiments
- Systematic approach that scales to full dataset
- Documentation of categorization criteria and rationale

### Timeline Impact
This decision affects:
- Week 1: Dataset exploration and initial experiments
- Week 2-3: Algorithm development and testing approach
- Week 4-6: Integration testing strategy
- Week 7-8: Comprehensive validation methodology