# Task Plan: Split Week 6 Notebook (42K Tokens → 2 Manageable Files)

**Objective**: Memisahkan `week6_template_detection_analysis.ipynb` menjadi 2 notebook terpisah untuk performance optimization dan better maintainability

**Reference**: `docs/dev/week6-continuation-strategy.md`

**Current Issue**:
- File size: ~42K tokens (65 cells)
- Performance degradation risk untuk large Jupyter notebooks
- Difficult navigation dan version control

**Target Structure**:
```
notebooks/
├── week6_part1_foundation_integration.ipynb (Section 1-3)
└── week6_part2_detection_methods.ipynb (Section 4-6)
```

---

## 📋 Task Breakdown

### **Task 1: Analyze Current Notebook Structure**
**Priority**: Critical | **Estimated Time**: 15 minutes

**Actions**:
1. Read current notebook file completely
2. Identify cell boundaries untuk each section:
   - Section 1: Project Overview & Objectives
   - Section 2: Environment Setup & Configuration
   - Section 3: Week 5 Integration Validation
   - Section 4: Contour-Based Detection Analysis
   - Section 5: Hough Transform Detection Analysis
   - Section 6: Template Matching Detection Analysis
3. Document cell ranges untuk each section
4. Identify shared variables/state yang perlu di-transfer

**Deliverable**:
- ✅ Cell range mapping untuk Section 1-3 dan 4-6
- ✅ List of variables/state untuk state management

---

### **Task 2: Create Part 1 Notebook (Foundation & Integration)**
**Priority**: High | **Estimated Time**: 30 minutes

**Scope**: Section 1-3
- Project Overview & Objectives
- Environment Setup & Configuration
- Week 5 Integration Validation

**Actions**:
1. **Extract cells** untuk Section 1-3 dari current notebook
2. **Create new file**: `notebooks/week6_part1_foundation_integration.ipynb`
3. **Add metadata**:
   ```json
   {
     "metadata": {
       "kernelspec": {
         "display_name": "Python 3",
         "language": "python",
         "name": "python3"
       }
     }
   }
   ```
4. **Add final cell** untuk state saving:
   ```python
   # === STATE MANAGEMENT: Save for Part 2 ===
   import pickle
   from pathlib import Path

   # Create results directory
   results_dir = Path('results')
   results_dir.mkdir(exist_ok=True)

   # Save preprocessing results and configuration
   state_part1 = {
       'preprocessed_images': preprocessed_images,
       'sample_metadata': sample_metadata,
       'config': config,
       'quality_metrics': quality_metrics,
       'week5_validation_results': week5_validation_results
   }

   with open('results/part1_foundation_state.pkl', 'wb') as f:
       pickle.dump(state_part1, f)

   print("✅ Part 1 state saved successfully!")
   print(f"   - Preprocessed images: {len(preprocessed_images)}")
   print(f"   - Saved to: results/part1_foundation_state.pkl")
   ```

**Deliverable**:
- ✅ `week6_part1_foundation_integration.ipynb` created
- ✅ Section 1-3 content properly transferred
- ✅ State management cell added
- ✅ Notebook executes without errors

---

### **Task 3: Create Part 2 Notebook (Detection Methods)**
**Priority**: High | **Estimated Time**: 45 minutes

**Scope**: Section 4-6
- Contour-Based Detection Analysis
- Hough Transform Detection Analysis
- Template Matching Detection Analysis

**Actions**:
1. **Extract cells** untuk Section 4-6 dari current notebook
2. **Create new file**: `notebooks/week6_part2_detection_methods.ipynb`
3. **Add initialization cell** untuk state loading:
   ```python
   # === STATE MANAGEMENT: Load from Part 1 ===
   import pickle
   from pathlib import Path

   # Load state from Part 1
   with open('results/part1_foundation_state.pkl', 'rb') as f:
       state_part1 = pickle.load(f)

   # Extract variables
   preprocessed_images = state_part1['preprocessed_images']
   sample_metadata = state_part1['sample_metadata']
   config = state_part1['config']
   quality_metrics = state_part1['quality_metrics']
   week5_validation_results = state_part1['week5_validation_results']

   print("✅ Part 1 state loaded successfully!")
   print(f"   - Preprocessed images: {len(preprocessed_images)}")
   print(f"   - Configuration loaded")
   print("\n🚀 Ready to continue with detection methods analysis...")
   ```
4. **Add all Section 4-6 cells** after state loading
5. **Add final summary cell**:
   ```python
   # === SECTION 1-6 COMPLETION SUMMARY ===
   print("\n" + "="*60)
   print("📊 WEEK 6 PART 1-2 COMPLETION SUMMARY")
   print("="*60)
   print("\n✅ Completed Sections:")
   print("   - Section 1: Project Overview & Objectives")
   print("   - Section 2: Environment Setup & Configuration")
   print("   - Section 3: Week 5 Integration Validation")
   print("   - Section 4: Contour-Based Detection Analysis")
   print("   - Section 5: Hough Transform Detection Analysis")
   print("   - Section 6: Template Matching Detection Analysis")

   print("\n📈 Performance Summary:")
   print(f"   - Contour Detection: {contour_accuracy:.1%} accuracy")
   print(f"   - Hough Transform: {hough_accuracy:.1%} accuracy")
   print(f"   - Template Matching: {template_accuracy:.1%} accuracy")

   print("\n🔜 Next Steps:")
   print("   - Section 7: Comparative Analysis")
   print("   - Section 8: Detection Fusion Algorithm")
   print("   - Section 9: Grid Segmentation Pipeline")
   print("\n" + "="*60)
   ```

**Deliverable**:
- ✅ `week6_part2_detection_methods.ipynb` created
- ✅ Section 4-6 content properly transferred
- ✅ State loading cell working correctly
- ✅ Summary cell added
- ✅ Notebook executes without errors

---

### **Task 4: Validate Split Notebooks**
**Priority**: Critical | **Estimated Time**: 20 minutes

**Actions**:
1. **Execute Part 1 completely**:
   - Restart kernel
   - Run all cells
   - Verify state file created: `results/part1_foundation_state.pkl`
   - Check all visualizations render correctly

2. **Execute Part 2 completely**:
   - Restart kernel
   - Run all cells
   - Verify state loading successful
   - Check all detection methods execute correctly
   - Validate visualizations consistent

3. **Cross-validation**:
   - Compare results antara original vs split notebooks
   - Verify numerical consistency
   - Check visualization quality

**Deliverable**:
- ✅ Both notebooks execute without errors
- ✅ State transfer working correctly
- ✅ Results consistent dengan original notebook
- ✅ No data loss or corruption

---

### **Task 5: Update Documentation & References**
**Priority**: Medium | **Estimated Time**: 15 minutes

**Actions**:
1. **Update strategy document**:
   - Add completion checkmarks untuk split notebooks
   - Document actual file sizes post-split

2. **Update task plan** (`docs/task/task_notebook_implementation.md`):
   - Mark Section 1-6 as completed across 2 notebooks
   - Update file references

3. **Create README** in `notebooks/` directory:
   ```markdown
   # Week 6 Notebooks Organization

   ## Structure
   - `week6_part1_foundation_integration.ipynb` - Section 1-3
   - `week6_part2_detection_methods.ipynb` - Section 4-6
   - `week6_template_detection_analysis.ipynb` - DEPRECATED (original monolithic)

   ## Execution Order
   1. Run Part 1 → generates `results/part1_foundation_state.pkl`
   2. Run Part 2 → loads state from Part 1

   ## File Sizes
   - Part 1: ~20-25K tokens (~30 cells)
   - Part 2: ~20-25K tokens (~35 cells)
   - Total: ~45K tokens (manageable split)
   ```

4. **Optional**: Rename original file untuk backup:
   - `week6_template_detection_analysis.ipynb` →
   - `week6_template_detection_analysis_BACKUP.ipynb`

**Deliverable**:
- ✅ Documentation updated
- ✅ README created
- ✅ File references consistent across docs
- ✅ Original file preserved as backup

---

## 📊 Success Criteria

- ✅ **Performance**: Both notebooks <25K tokens each (vs 42K original)
- ✅ **Functionality**: All cells execute without errors
- ✅ **State Transfer**: Variables properly saved/loaded between notebooks
- ✅ **Results Consistency**: Identical output vs original notebook
- ✅ **Documentation**: Clear execution instructions dan file organization
- ✅ **Maintainability**: Easier navigation, editing, version control

---

## 🔄 Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ TASK 1: Analyze Current Notebook (15 min)                  │
│ → Identify section boundaries & shared state               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ TASK 2: Create Part 1 Notebook (30 min)                    │
│ → Extract Section 1-3 + Add state saving                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ TASK 3: Create Part 2 Notebook (45 min)                    │
│ → Extract Section 4-6 + Add state loading                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ TASK 4: Validate Split Notebooks (20 min)                  │
│ → Execute both → Verify consistency → Test state transfer  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ TASK 5: Update Documentation (15 min)                      │
│ → Update docs → Create README → Archive original           │
└─────────────────────────────────────────────────────────────┘
```

**Total Estimated Time**: ~2 hours

---

## 🛡️ Risk Mitigation

### **Risk 1: State Transfer Failure**
**Mitigation**:
- Use pickle untuk binary serialization (robust)
- Add explicit validation setelah load
- Include error handling dengan clear messages

### **Risk 2: Cell Dependencies**
**Mitigation**:
- Carefully analyze variable dependencies
- Include all necessary imports in Part 2
- Test execution dengan fresh kernel

### **Risk 3: Visualization Inconsistency**
**Mitigation**:
- Use same matplotlib/seaborn configuration
- Preserve figure settings across notebooks
- Validate visual output quality

### **Risk 4: Data Loss**
**Mitigation**:
- **NEVER delete original file until validation complete**
- Keep backup: `week6_template_detection_analysis_BACKUP.ipynb`
- Use version control (git commit before split)

---

## ✅ Completion Checklist

- [ ] Task 1: Section boundaries identified
- [ ] Task 2: Part 1 notebook created dan validated
- [ ] Task 3: Part 2 notebook created dan validated
- [ ] Task 4: Cross-validation successful
- [ ] Task 5: Documentation updated
- [ ] Original file backed up
- [ ] Git commit dengan descriptive message

---

**Status**: Ready for Execution
**Next Action**: Begin Task 1 - Analyze current notebook structure
**Expected Outcome**: 2 manageable notebooks (~25K tokens each) dengan proper state management
