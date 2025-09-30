"""
Fix cell ordering issue in week6_template_detection_analysis.ipynb
Reorder cells so contour_detector is initialized before being used
"""

import json
from pathlib import Path
import shutil
from datetime import datetime

def fix_notebook_cell_order():
    """Fix cell ordering in Section 4 of the notebook"""

    nb_path = Path('D:/2-Project/Project_7/notebooks/week6_template_detection_analysis.ipynb')

    # Create backup
    backup_path = nb_path.parent / f"{nb_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
    shutil.copy2(nb_path, backup_path)
    print(f"Backup created: {backup_path.name}")

    # Read notebook
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    print(f"\nTotal cells: {len(nb['cells'])}")
    print("\nBefore reordering (cells 28-32):")
    for i in range(28, 33):
        cell = nb['cells'][i]
        cell_type = cell.get('cell_type')
        source = cell.get('source', [''])
        first_line = source[0][:50] if isinstance(source, list) else str(source)[:50]
        print(f"  Cell {i}: {cell_type:8} - {first_line}")

    # Extract cells that need reordering
    cells = nb['cells']
    cell_28 = cells[28]  # Section 4 header (keep)
    cell_29 = cells[29]  # Processing code (move to end)
    cell_30 = cells[30]  # Initialize code (move earlier)
    cell_31 = cells[31]  # "4.2 Implementation" header
    cell_32 = cells[32]  # "4.1 Theoretical Foundation" header

    # New order:
    # 28: Section 4 header (unchanged)
    # 29: "4.1 Theoretical Foundation" header (was cell 32)
    # 30: Theoretical Foundation content (create new markdown cell)
    # 31: "4.2 Implementation" header (was cell 31)
    # 32: Initialize contour_detector (was cell 30)
    # 33: Processing code (was cell 29)

    # Create new cell 30 (Theoretical Foundation content) from cell 32
    new_cell_30 = cell_32  # This already has the theoretical content

    # Reorder
    cells[28] = cell_28  # Keep Section 4 header
    cells[29] = cell_32  # Move theoretical foundation to 29
    cells[30] = cell_30  # Initialize detector
    cells[31] = cell_31  # Keep "4.2" header
    cells[32] = cell_29  # Move processing code to 32

    # Update notebook
    nb['cells'] = cells

    print("\nAfter reordering (cells 28-32):")
    for i in range(28, 33):
        cell = nb['cells'][i]
        cell_type = cell.get('cell_type')
        source = cell.get('source', [''])
        first_line = source[0][:50] if isinstance(source, list) else str(source)[:50]
        print(f"  Cell {i}: {cell_type:8} - {first_line}")

    # Write fixed notebook
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"\n✅ Notebook fixed successfully")
    print(f"   Backup saved: {backup_path.name}")
    print(f"   Fixed cells: 29-32 reordered")
    print(f"   Result: contour_detector initialized before use")

    return True

if __name__ == "__main__":
    fix_notebook_cell_order()