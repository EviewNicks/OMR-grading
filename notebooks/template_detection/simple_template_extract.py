#!/usr/bin/env python3
"""
Simple Template Extraction from Successful Contour Detection
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_image(image_path):
    """Load image from path"""
    return cv2.imread(image_path)

def simple_template_extraction():
    """Extract template using best contour detection result"""

    # Load sample image
    img_path = Path("../../datasets/train/004-Copy-2-_jpg.rf.894f0db5590e30ae5ba5c536cc3dc581.jpg")

    if not img_path.exists():
        print(f"Image not found: {img_path}")
        return None

    image = load_image(str(img_path))
    if image is None:
        print(f"Failed to load image")
        return None

    # Simple preprocessing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, blockSize=11, C=2
    )

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort by area (largest first)
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)

    print(f"Found {len(contours)} contours")
    print(f"Processing top 5 largest contours...")

    best_template = None
    best_score = 0.0

    for i, contour in enumerate(contours_sorted[:5]):
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)

        # Check if this looks like OMR grid (aspect ratio ~0.15 for 3x20)
        aspect_ratio = w / h if h > 0 else 0

        # Extract region
        roi = image[y:y+h, x:x+w]

        if roi.size > 0:
            # Convert to grayscale
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Score based on aspect ratio and size
            aspect_score = max(0, 1 - abs(aspect_ratio - 0.15) / 0.15)
            size_score = min(1, (w * h) / (image.shape[0] * image.shape[1]) * 4)  # Expected ~25% of image
            total_score = aspect_score * 0.6 + size_score * 0.4

            print(f"Contour {i+1}: size={w}x{h}, aspect={aspect_ratio:.3f}, score={total_score:.3f}")

            if total_score > best_score:
                best_score = total_score
                best_template = roi_gray.copy()
                print(f"  -> New best template!")

    if best_template is not None:
        print(f"\nBest template extracted with score: {best_score:.3f}")

        # Enhance template
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(best_template)

        # Apply threshold for clean binary template
        _, binary_template = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Save template
        cv2.imwrite("real_template.png", binary_template)
        print("Template saved as 'real_template.png'")

        # Visualize
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Original
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        axes[0].imshow(image_rgb)
        axes[0].set_title("Original Image")
        axes[0].axis('off')

        # Binary with detection
        cv2.rectangle(image_rgb, (x, y), (x+w, y+h), (0, 255, 0), 3)
        axes[1].imshow(image_rgb)
        axes[1].set_title("Detected Region")
        axes[1].axis('off')

        # Extracted template
        axes[2].imshow(binary_template, cmap='gray')
        axes[2].set_title("Extracted Template")
        axes[2].axis('off')

        plt.suptitle("Real Template Extraction", fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.show()

        return binary_template
    else:
        print("No suitable template found!")
        return None

if __name__ == "__main__":
    template = simple_template_extraction()