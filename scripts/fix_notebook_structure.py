"""
Fix Week 6 Notebook Structure
Removes corrupted cells (33-48) and prepares for proper re-implementation
"""
import json
from pathlib import Path

def fix_notebook_structure():
    """Remove corrupted cells and restore clean structure"""

    notebook_path = Path("notebooks/week6_template_detection_analysis.ipynb")

    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Original notebook: {len(data['cells'])} cells")

    # Keep only cells 0-32 (up to Section 4.2 implementation code)
    # Remove corrupted cells 33-48
    clean_cells = data['cells'][:33]

    print(f"After cleanup: {len(clean_cells)} cells")
    print("\nRemaining structure:")
    for i, cell in enumerate(clean_cells):
        if cell['cell_type'] == 'markdown' and cell['source']:
            first_line = cell['source'][0] if isinstance(cell['source'][0], str) else ''
            if '###' in first_line or '##' in first_line:
                print(f"  Cell {i}: {first_line.strip()}")

    # Update notebook
    data['cells'] = clean_cells

    # Save cleaned notebook
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

    print(f"\nNotebook cleaned successfully!")
    print(f"Backup saved as: {notebook_path}.backup")
    print("\nReady for proper Section 4.3-4.5 and Section 5.0-5.5 implementation")

if __name__ == "__main__":
    fix_notebook_structure()