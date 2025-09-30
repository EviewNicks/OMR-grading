"""
Fix Cell [32] KeyError Issue
Changes 'original_image' to 'original' for consistency with Cell [34]
"""
import json
from pathlib import Path

def fix_cell_32():
    """Fix key name inconsistency in Cell [32]"""

    notebook_path = Path("notebooks/week6_template_detection_analysis.ipynb")

    # Read notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Fixing Cell [32] key name issue...")
    print("="*60)

    # Find Cell [32] - Should be the code cell in Section 4.2
    # Cell [32] is the implementation cell that stores contour_results
    cell_32 = data['cells'][32]

    if cell_32['cell_type'] == 'code':
        # Get current source
        source = cell_32['source']

        # Find and replace 'original_image' with 'original'
        fixed = False
        for i, line in enumerate(source):
            if "'original_image':" in line or '"original_image":' in line:
                # Replace the line
                source[i] = line.replace("'original_image':", "'original':")
                source[i] = source[i].replace('"original_image":', '"original":')
                print(f"Line {i}: Fixed 'original_image' to 'original'")
                fixed = True

        if fixed:
            # Update the cell
            cell_32['source'] = source

            # Save notebook
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=1, ensure_ascii=False)

            print("\nCell [32] fixed successfully!")
            print("   Changed: 'original_image' to 'original'")
            print("   Notebook saved.")
        else:
            print("\nWarning: Could not find 'original_image' in Cell [32]")
            print("   Cell may have already been fixed or structure is different")
    else:
        print(f"\nError: Cell [32] is not a code cell (type: {cell_32['cell_type']})")
        print("   Please check cell numbering")

    print("="*60)

if __name__ == "__main__":
    fix_cell_32()