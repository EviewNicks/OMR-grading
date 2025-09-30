"""
Validate Week 6 Notebook Structure
Quick validation script to verify notebook structure is correct
"""
import json
from pathlib import Path

def validate_structure():
    """Validate notebook structure and display summary"""

    notebook_path = Path("notebooks/week6_template_detection_analysis.ipynb")

    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("="*80)
    print("NOTEBOOK STRUCTURE VALIDATION")
    print("="*80)

    print(f"\nTotal Cells: {len(data['cells'])}")

    # Collect section headers
    sections = []
    for i, cell in enumerate(data['cells']):
        if cell['cell_type'] == 'markdown' and cell['source']:
            first_line = cell['source'][0] if cell['source'] else ''
            if '###' in first_line or '##' in first_line:
                sections.append((i, first_line.strip()))

    print(f"\nSection Headers Found: {len(sections)}")
    print("\nStructure:")
    print("-" * 80)

    current_major = None
    for cell_num, header in sections:
        if header.startswith('##') and not header.startswith('###'):
            current_major = header
            print(f"\n{header}")
        elif header.startswith('###'):
            section_num = header.split()[1] if len(header.split()) > 1 else ''
            print(f"  Cell {cell_num:2d}: {header[:70]}")

    # Validate expected sections
    print("\n" + "="*80)
    print("VALIDATION CHECKS")
    print("="*80)

    expected_sections = [
        "## 1.", "## 2.", "## 5.",
        "### 4.1", "### 4.2", "### 4.3", "### 4.4", "### 4.5",
        "### 5.1", "### 5.2", "### 5.3", "### 5.4", "### 5.5"
    ]

    found_sections = [h for _, h in sections]
    validation_results = []

    for expected in expected_sections:
        found = any(expected in section for section in found_sections)
        status = "[OK]" if found else "[MISSING]"
        validation_results.append((expected, found))
        print(f"{status} {expected}: {'Found' if found else 'MISSING'}")

    # Summary
    passed = sum(1 for _, found in validation_results if found)
    total = len(validation_results)

    print("\n" + "="*80)
    if passed == total:
        print(f"VALIDATION: PASSED ({passed}/{total} sections found)")
    else:
        print(f"VALIDATION: PARTIAL ({passed}/{total} sections found)")
    print("="*80)

    # Cell format check
    print("\nCell Format Validation:")
    sample_cells = [33, 39, 45]  # Check key cells
    all_valid = True

    for cell_idx in sample_cells:
        if cell_idx < len(data['cells']):
            cell = data['cells'][cell_idx]
            source_valid = all(isinstance(line, str) for line in cell['source'])
            char_per_line = any(len(line) == 2 and line[1] == '\n' for line in cell['source'][:5])

            if source_valid and not char_per_line:
                print(f"  Cell {cell_idx}: [OK] Valid format")
            else:
                print(f"  Cell {cell_idx}: [ERROR] Invalid format (character per line)")
                all_valid = False

    if all_valid:
        print("\n[OK] All cells properly formatted")
    else:
        print("\n[ERROR] Some cells have formatting issues")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Cells: {len(data['cells'])}")
    print(f"Section Headers: {len(sections)}")
    print(f"Validation: {'PASSED' if passed == total and all_valid else 'NEEDS REVIEW'}")
    print("="*80)

if __name__ == "__main__":
    validate_structure()