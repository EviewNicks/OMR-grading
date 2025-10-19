#!/usr/bin/env python3
"""
Template Extraction Script
Extract real OMR template from successful contour detection results
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

# Import contour detection functions from notebook
def load_image(image_path: str) -> np.ndarray:
    """Load image dari path"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot load image: {image_path}")
    return image

def preprocess_for_contour(image: np.ndarray) -> np.ndarray:
    """Preprocessing untuk contour detection"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, blockSize=11, C=2
    )
    return binary

def extract_contours(binary_image: np.ndarray) -> Tuple[List, np.ndarray]:
    """Ekstraksi kontur dengan hierarchical relationships"""
    contours, hierarchy = cv2.findContours(
        binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    return contours, hierarchy

def calculate_rotation_robust_properties(contour: np.ndarray) -> Dict:
    """Calculate properties using rotation-invariant minAreaRect"""
    min_rect = cv2.minAreaRect(contour)
    (center_x, center_y), (width, height), angle = min_rect

    box_points = cv2.boxPoints(min_rect)
    box_points = np.array(box_points, dtype=np.int32)

    contour_area = cv2.contourArea(contour)
    rect_area = width * height
    rectangularity = contour_area / rect_area if rect_area > 0 else 0.0

    if width > height:
        aspect_ratio = height / width if width > 0 else 0.0
    else:
        aspect_ratio = width / height if height > 0 else 0.0

    return {
        'area': contour_area,
        'aspect_ratio': aspect_ratio,
        'rectangularity': rectangularity,
        'angle': angle,
        'box_points': box_points,
        'center': (center_x, center_y),
        'dimensions': (width, height)
    }

def filter_contours_rotation_robust(
    contours: List,
    image_shape: Tuple[int, int],
    min_area_ratio: float = 0.05,
    max_area_ratio: float = 0.70,
    min_aspect_ratio: float = 0.05,
    max_aspect_ratio: float = 0.80,
    min_rectangularity: float = 0.60
) -> List[Dict]:
    """Filter kontur dengan rotation-robust properties"""
    h, w = image_shape[:2]
    image_area = h * w

    filtered = []

    for contour in contours:
        props = calculate_rotation_robust_properties(contour)
        area_ratio = props['area'] / image_area
        aspect_ratio = props['aspect_ratio']
        rectangularity = props['rectangularity']

        if not (min_area_ratio <= area_ratio <= max_area_ratio):
            continue
        if not (min_aspect_ratio <= aspect_ratio <= max_aspect_ratio):
            continue
        if rectangularity < min_rectangularity:
            continue

        filtered.append({
            'contour': contour,
            'area': props['area'],
            'area_ratio': area_ratio,
            'aspect_ratio': aspect_ratio,
            'rectangularity': rectangularity,
            'angle': props['angle'],
            'box_points': props['box_points'],
            'center': props['center'],
            'dimensions': props['dimensions']
        })

    return filtered

def detect_grid_rotation_robust(image: np.ndarray, use_binary_inv: bool = True) -> Dict:
    """Complete rotation-robust grid detection pipeline"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    if use_binary_inv:
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, blockSize=11, C=2
        )
    else:
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, blockSize=11, C=2
        )

    contours, hierarchy = extract_contours(binary)
    filtered = filter_contours_rotation_robust(contours, image.shape)

    # Simple scoring untuk template extraction
    if not filtered:
        return {
            'success': False,
            'confidence': 0.0,
            'message': 'No contours passed filtering'
        }

    # Score based on area ratio and rectangularity
    best_candidate = None
    best_score = 0.0

    for candidate in filtered:
        score = candidate['rectangularity'] * 0.6 + (1 - abs(candidate['area_ratio'] - 0.25)) * 0.4
        if score > best_score:
            best_score = score
            best_candidate = candidate
            best_candidate['confidence'] = score

    return {
        'success': True,
        'candidate': best_candidate,
        'confidence': best_score,
        'binary_image': binary,
        'threshold_method': 'BINARY_INV' if use_binary_inv else 'BINARY'
    }

def extract_template_from_detection(image: np.ndarray, detection_result: Dict) -> np.ndarray:
    """Extract clean OMR template dari detected grid region"""
    if not detection_result['success']:
        raise ValueError("Detection failed - cannot extract template")

    candidate = detection_result['candidate']
    box_points = candidate['box_points']

    # Create perspective transform untuk straighten the detected grid
    # Order points: top-left, top-right, bottom-right, bottom-left
    rect = cv2.minAreaRect(np.array(box_points))
    (center_x, center_y), (width, height), angle = rect

    # Create destination rectangle (straightened)
    dst_pts = np.array([
        [0, 0],
        [width-1, 0],
        [width-1, height-1],
        [0, height-1]
    ], dtype=np.float32)

    # Apply perspective transform
    M = cv2.getPerspectiveTransform(box_points.astype(np.float32), dst_pts)
    warped = cv2.warpPerspective(image, M, (int(width), int(height)))

    # Convert to grayscale for template
    template_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    # Enhance contrast untuk cleaner template
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(template_gray)

    # Apply threshold to get clean binary template
    _, binary_template = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary_template

def main():
    """Main extraction process"""
    # Dataset configuration
    DATASET_DIR = Path("../../datasets/train/")

    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found: {DATASET_DIR}")

    # Load sample images (gunakan yang sama seperti contour detection)
    image_paths = sorted(list(DATASET_DIR.glob("*.jpg")))[:10]

    print("Template Extraction Process")
    print("=" * 50)

    best_template = None
    best_result = None
    best_image_name = ""

    # Test each image untuk find best detection
    for img_path in image_paths:
        print(f"\nProcessing: {img_path.name}")
        image = load_image(str(img_path))

        # Try both threshold methods
        result_inv = detect_grid_rotation_robust(image, use_binary_inv=True)
        result_normal = detect_grid_rotation_robust(image, use_binary_inv=False)

        # Pick best result
        inv_confidence = result_inv.get('confidence', 0)
        normal_confidence = result_normal.get('confidence', 0)
        best_result_current = result_inv if inv_confidence >= normal_confidence else result_normal

        if best_result_current['success']:
            print(f"  SUCCESS: Detection successful (confidence: {best_result_current['confidence']:.3f})")

            try:
                template = extract_template_from_detection(image, best_result_current)

                if best_template is None or best_result_current['confidence'] > best_result['confidence']:
                    best_template = template
                    best_result = best_result_current
                    best_image_name = img_path.name
                    print(f"  NEW BEST: Template found")

            except Exception as e:
                print(f"  ERROR: Template extraction failed: {e}")
        else:
            print(f"  FAILED: Detection failed")

    if best_template is not None:
        print(f"\n" + "=" * 50)
        print(f"BEST TEMPLATE EXTRACTED")
        print(f"Source image: {best_image_name}")
        print(f"Template size: {best_template.shape[1]}x{best_template.shape[0]}")
        print(f"Detection confidence: {best_result['confidence']:.3f}")
        print(f"Grid angle: {best_result['candidate']['angle']:.1f}°")
        print("=" * 50)

        # Save template
        output_path = Path("real_template.png")
        cv2.imwrite(str(output_path), best_template)
        print(f"Template saved to: {output_path}")

        # Visualize extraction
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Original image with detection
        original_image = load_image(str(DATASET_DIR / best_image_name))
        original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        # Draw detection box
        box_points = best_result['candidate']['box_points']
        detection_vis = original_rgb.copy()
        cv2.drawContours(detection_vis, [box_points], 0, (0, 255, 0), 3)

        axes[0].imshow(detection_vis)
        axes[0].set_title(f"Original Image\n{best_image_name}")
        axes[0].axis('off')

        # Extracted template
        axes[1].imshow(best_template, cmap='gray')
        axes[1].set_title(f"Extracted Template\n{best_template.shape[1]}x{best_template.shape[0]}")
        axes[1].axis('off')

        # Template properties
        axes[2].axis('off')
        props_text = f"""Template Properties:

Source: {best_image_name}
Size: {best_template.shape[1]}x{best_template.shape[0]}
Confidence: {best_result['confidence']:.3f}
Angle: {best_result['candidate']['angle']:.1f}°
Aspect Ratio: {best_result['candidate']['aspect_ratio']:.3f}
Rectangularity: {best_result['candidate']['rectangularity']:.3f}
Area Ratio: {best_result['candidate']['area_ratio']:.3f}

Template ready for
enhanced template matching!
"""
        axes[2].text(0.1, 0.5, props_text, fontsize=10, verticalalignment='center',
                    family='monospace')
        axes[2].set_title("Template Information")

        plt.suptitle("Real OMR Template Extraction", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()

        return best_template, best_result, best_image_name
    else:
        print("ERROR: No successful template extraction found!")
        return None, None, None

if __name__ == "__main__":
    template, result, source_image = main()