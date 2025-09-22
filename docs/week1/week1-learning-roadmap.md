# Week 1 Learning Roadmap - OMR Academic Project

**Course:** Pengolahan Citra Digital (Digital Image Processing)
**Project:** Sistem Penilaian Otomatis Ujian Pilihan Ganda
**Week Focus:** Environment Setup & Dataset Analysis
**Target Audience:** Students learning computer vision and full-stack development

---

## 🎯 Week 1 Learning Objectives

By the end of Week 1, students will be able to:

1. **Understand Project Scope:** Comprehend OMR system requirements and technical challenges
2. **Setup Development Environment:** Configure Python, OpenCV, and web development tools
3. **Analyze OMR Dataset:** Understand image characteristics and processing challenges
4. **Create Basic OpenCV Experiments:** Implement fundamental image processing operations
5. **Document Learning Process:** Maintain academic documentation standards

---

## 📅 Day-by-Day Learning Plan

### **Day 1: Project Understanding & Environment Foundations**

#### **Morning Session (3-4 hours): Project Analysis**

**Learning Goals:**
- Understand what OMR systems are and their real-world applications
- Analyze project requirements and technical constraints
- Identify key challenges in bubble detection

**Activities:**
1. **Project Documentation Review** (60 minutes)
   - Read `project.md` and `academic-requirements.md`
   - Understand TOEFL-style answer sheet format (60 questions, A-E options)
   - Review 8-week timeline and deliverables

2. **OMR System Research** (60 minutes)
   - Research existing OMR solutions and their approaches
   - Understand the difference between simple rule-based vs ML approaches
   - Document 3-5 key technical challenges you identify

3. **Template Analysis** (60 minutes)
   - Study TOEFL answer sheet layouts
   - Understand grid structure (3 columns × 20 rows)
   - Sketch the coordinate system for bubble detection

**Knowledge Checkpoint:**
- Can you explain what an OMR system does in 2-3 sentences?
- What are the main technical challenges in bubble detection?
- Why is this project using OpenCV instead of machine learning?

#### **Afternoon Session (2-3 hours): Python Environment Setup**

**Learning Goals:**
- Setup Python development environment with proper dependency management
- Understand virtual environments and package management
- Install and verify OpenCV installation

**Activities:**
1. **Python Environment Setup** (90 minutes)
   ```bash
   # Create project directory
   mkdir omr-grading-system
   cd omr-grading-system

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment (Windows)
   venv\Scripts\activate

   # Install core dependencies
   pip install opencv-python numpy matplotlib jupyter
   ```

2. **OpenCV Verification** (30 minutes)
   ```python
   # test_opencv.py
   import cv2
   import numpy as np

   print(f"OpenCV Version: {cv2.__version__}")

   # Create simple test image
   img = np.zeros((300, 300, 3), dtype=np.uint8)
   cv2.rectangle(img, (50, 50), (250, 250), (0, 255, 0), 2)
   cv2.imshow('Test', img)
   cv2.waitKey(0)
   cv2.destroyAllWindows()
   ```

3. **IDE Configuration** (30 minutes)
   - Setup VS Code with Python extensions
   - Configure debugging for OpenCV projects
   - Install useful extensions: Python, Jupyter, GitLens

**Knowledge Checkpoint:**
- Can you successfully run the OpenCV test script?
- Do you understand the purpose of virtual environments?
- Is your IDE properly configured for Python development?

**Daily Deliverable:**
- Create `day1-setup-notes.md` documenting your environment setup process

---

### **Day 2: Dataset Acquisition & Initial Analysis**

#### **Morning Session (3 hours): Dataset Download & Organization**

**Learning Goals:**
- Download and organize the Kaggle OMR dataset
- Understand dataset structure and image variations
- Setup proper data organization for academic projects

**Activities:**
1. **Kaggle Account & Dataset Download** (60 minutes)
   - Create Kaggle account if needed
   - Download OMR dataset (follow `dataset-guide.md`)
   - Verify download completion (~200MB)

2. **Dataset Organization** (60 minutes)
   ```bash
   # Create dataset structure
   datasets/
   ├── kaggle_omr/         # Raw downloaded data
   ├── analysis/           # Your analysis results
   ├── samples/           # Selected samples for testing
   └── processed/         # Future preprocessed images
   ```

3. **Initial Dataset Exploration** (60 minutes)
   ```python
   # dataset_explorer.py
   import os
   import cv2
   import matplotlib.pyplot as plt

   def explore_dataset(dataset_path):
       """Initial dataset exploration"""
       images = []
       for file in os.listdir(dataset_path):
           if file.lower().endswith(('.jpg', '.png')):
               images.append(file)

       print(f"Total images found: {len(images)}")

       # Load and display first few images
       fig, axes = plt.subplots(2, 3, figsize=(15, 10))
       for i, img_file in enumerate(images[:6]):
           img = cv2.imread(os.path.join(dataset_path, img_file))
           img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

           axes[i//3, i%3].imshow(img_rgb)
           axes[i//3, i%3].set_title(f"{img_file} - {img.shape}")
           axes[i//3, i%3].axis('off')

       plt.tight_layout()
       plt.savefig('datasets/analysis/initial_exploration.png')
       plt.show()

   if __name__ == "__main__":
       explore_dataset("datasets/kaggle_omr/")
   ```

**Knowledge Checkpoint:**
- How many images are in your dataset?
- What are the typical image dimensions and formats?
- Can you identify different quality levels in the images?

#### **Afternoon Session (2 hours): Image Quality Analysis**

**Learning Goals:**
- Categorize images by quality and difficulty
- Understand various image conditions (lighting, rotation, contrast)
- Document findings for academic analysis

**Activities:**
1. **Quality Categorization** (90 minutes)
   ```python
   # quality_analyzer.py
   import cv2
   import numpy as np

   def analyze_image_quality(img_path):
       """Analyze image quality metrics"""
       img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

       # Calculate basic quality metrics
       mean_brightness = np.mean(img)
       contrast = np.std(img)

       # Calculate blur detection (Laplacian variance)
       laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()

       return {
           'brightness': mean_brightness,
           'contrast': contrast,
           'sharpness': laplacian_var,
           'resolution': img.shape
       }

   def categorize_images(dataset_path):
       """Categorize images by quality"""
       categories = {'high': [], 'medium': [], 'low': []}

       for filename in os.listdir(dataset_path):
           if filename.lower().endswith(('.jpg', '.png')):
               img_path = os.path.join(dataset_path, filename)
               metrics = analyze_image_quality(img_path)

               # Simple categorization rules
               if metrics['contrast'] > 50 and metrics['sharpness'] > 100:
                   categories['high'].append((filename, metrics))
               elif metrics['contrast'] > 30 and metrics['sharpness'] > 50:
                   categories['medium'].append((filename, metrics))
               else:
                   categories['low'].append((filename, metrics))

       return categories
   ```

2. **Document Findings** (30 minutes)
   - Create quality analysis report
   - Select 3 images from each quality category
   - Document specific challenges you observe

**Daily Deliverable:**
- Create `day2-dataset-analysis.md` with quality categorization results

---

### **Day 3: OpenCV Fundamentals - Image Preprocessing**

#### **Morning Session (3 hours): Core Image Processing Concepts**

**Learning Goals:**
- Understand fundamental image processing operations
- Learn OpenCV basic functions for OMR preprocessing
- Implement grayscale conversion, blurring, and thresholding

**Activities:**
1. **Theoretical Foundation** (45 minutes)
   - Study grayscale conversion and its importance
   - Understand Gaussian blur for noise reduction
   - Learn about thresholding techniques

2. **Basic Preprocessing Pipeline** (90 minutes)
   ```python
   # preprocessing_basics.py
   import cv2
   import numpy as np
   import matplotlib.pyplot as plt

   def basic_preprocessing(image_path):
       """Implement basic preprocessing pipeline"""

       # Step 1: Load image
       original = cv2.imread(image_path)

       # Step 2: Convert to grayscale
       gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

       # Step 3: Apply Gaussian blur
       blurred = cv2.GaussianBlur(gray, (5, 5), 0)

       # Step 4: Apply threshold
       _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

       # Step 5: Adaptive threshold (better for varying lighting)
       adaptive_thresh = cv2.adaptiveThreshold(
           blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
           cv2.THRESH_BINARY, 11, 2
       )

       return {
           'original': original,
           'grayscale': gray,
           'blurred': blurred,
           'threshold': thresh,
           'adaptive_threshold': adaptive_thresh
       }

   def visualize_preprocessing_steps(results):
       """Visualize each preprocessing step"""
       fig, axes = plt.subplots(2, 3, figsize=(15, 10))

       # Original (convert BGR to RGB for matplotlib)
       axes[0, 0].imshow(cv2.cvtColor(results['original'], cv2.COLOR_BGR2RGB))
       axes[0, 0].set_title('Original')
       axes[0, 0].axis('off')

       # Grayscale
       axes[0, 1].imshow(results['grayscale'], cmap='gray')
       axes[0, 1].set_title('Grayscale')
       axes[0, 1].axis('off')

       # Blurred
       axes[0, 2].imshow(results['blurred'], cmap='gray')
       axes[0, 2].set_title('Gaussian Blur')
       axes[0, 2].axis('off')

       # Binary threshold
       axes[1, 0].imshow(results['threshold'], cmap='gray')
       axes[1, 0].set_title('Binary Threshold')
       axes[1, 0].axis('off')

       # Adaptive threshold
       axes[1, 1].imshow(results['adaptive_threshold'], cmap='gray')
       axes[1, 1].set_title('Adaptive Threshold')
       axes[1, 1].axis('off')

       # Hide last subplot
       axes[1, 2].axis('off')

       plt.tight_layout()
       plt.savefig('datasets/analysis/preprocessing_steps.png', dpi=300)
       plt.show()

   # Test with sample image
   if __name__ == "__main__":
       sample_path = "datasets/samples/sample_image.jpg"
       results = basic_preprocessing(sample_path)
       visualize_preprocessing_steps(results)
   ```

3. **Experiment with Parameters** (45 minutes)
   - Test different blur kernel sizes (3x3, 5x5, 7x7)
   - Try various threshold values
   - Compare binary vs adaptive thresholding results

**Knowledge Checkpoint:**
- Why do we convert images to grayscale for OMR processing?
- What's the difference between binary and adaptive thresholding?
- When would you use adaptive thresholding over binary thresholding?

#### **Afternoon Session (2 hours): Contour Detection Basics**

**Learning Goals:**
- Understand contours and their role in shape detection
- Learn to filter contours based on area and shape properties
- Prepare foundation for bubble detection

**Activities:**
1. **Contour Detection Theory** (30 minutes)
   - Study what contours represent
   - Understand contour hierarchy and retrieval modes
   - Learn about contour approximation methods

2. **Contour Detection Implementation** (90 minutes)
   ```python
   # contour_detection.py
   import cv2
   import numpy as np

   def detect_contours(image_path):
       """Detect and analyze contours in preprocessed image"""

       # Preprocess image
       img = cv2.imread(image_path)
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
       blurred = cv2.GaussianBlur(gray, (5, 5), 0)
       thresh = cv2.adaptiveThreshold(
           blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
           cv2.THRESH_BINARY_INV, 11, 2
       )

       # Find contours
       contours, hierarchy = cv2.findContours(
           thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
       )

       # Filter contours by area (potential bubbles)
       min_area = 100  # Minimum bubble area
       max_area = 2000  # Maximum bubble area

       bubble_candidates = []
       for contour in contours:
           area = cv2.contourArea(contour)
           if min_area < area < max_area:
               # Check if contour is roughly circular
               perimeter = cv2.arcLength(contour, True)
               circularity = 4 * np.pi * area / (perimeter * perimeter)

               if circularity > 0.3:  # Rough circle check
                   bubble_candidates.append(contour)

       # Visualize results
       result_img = img.copy()
       cv2.drawContours(result_img, contours, -1, (0, 255, 0), 1)
       cv2.drawContours(result_img, bubble_candidates, -1, (0, 0, 255), 2)

       return {
           'original': img,
           'threshold': thresh,
           'result': result_img,
           'all_contours': len(contours),
           'bubble_candidates': len(bubble_candidates)
       }

   def analyze_contour_properties(contour):
       """Analyze properties of a single contour"""
       area = cv2.contourArea(contour)
       perimeter = cv2.arcLength(contour, True)

       # Bounding rectangle
       x, y, w, h = cv2.boundingRect(contour)
       aspect_ratio = float(w) / h

       # Extent (contour area / bounding rectangle area)
       rect_area = w * h
       extent = float(area) / rect_area

       # Solidity (contour area / convex hull area)
       hull = cv2.convexHull(contour)
       hull_area = cv2.contourArea(hull)
       solidity = float(area) / hull_area

       return {
           'area': area,
           'perimeter': perimeter,
           'aspect_ratio': aspect_ratio,
           'extent': extent,
           'solidity': solidity
       }
   ```

**Daily Deliverable:**
- Create `day3-preprocessing-experiments.md` documenting your preprocessing experiments

---

### **Day 4: Template Detection Fundamentals**

#### **Morning Session (3 hours): Understanding Template Matching**

**Learning Goals:**
- Understand template matching concepts
- Learn to locate answer grid in OMR sheets
- Implement basic template detection for standard layouts

**Activities:**
1. **Template Matching Theory** (45 minutes)
   - Study how template matching works
   - Understand normalized cross-correlation
   - Learn about scale and rotation invariance challenges

2. **Grid Detection Implementation** (90 minutes)
   ```python
   # template_detection.py
   import cv2
   import numpy as np

   def detect_answer_grid(image_path):
       """Detect answer grid region in OMR sheet"""

       # Load and preprocess
       img = cv2.imread(image_path)
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

       # Apply morphological operations to enhance grid structure
       kernel = np.ones((3, 3), np.uint8)
       opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

       # Use HoughLines to detect grid lines
       edges = cv2.Canny(opening, 50, 150, apertureSize=3)
       lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)

       # Separate horizontal and vertical lines
       horizontal_lines = []
       vertical_lines = []

       if lines is not None:
           for rho, theta in lines[:, 0]:
               if abs(theta) < np.pi/4 or abs(theta - np.pi) < np.pi/4:
                   horizontal_lines.append((rho, theta))
               else:
                   vertical_lines.append((rho, theta))

       return {
           'horizontal_lines': len(horizontal_lines),
           'vertical_lines': len(vertical_lines),
           'edges': edges,
           'original': img
       }

   def find_bubble_regions(image_path):
       """Find individual bubble regions based on grid structure"""

       img = cv2.imread(image_path)
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

       # Assume standard TOEFL layout: 3 columns, 20 rows
       height, width = gray.shape

       # Calculate bubble positions (this is simplified)
       # In real implementation, you'd use detected grid lines

       bubbles_per_row = 5  # A, B, C, D, E
       questions_per_column = 20
       columns = 3

       bubble_regions = []

       # Estimate bubble size and spacing
       bubble_width = width // (columns * bubbles_per_row + 2)
       bubble_height = height // (questions_per_column + 2)

       for col in range(columns):
           for row in range(questions_per_column):
               for bubble in range(bubbles_per_row):
                   x = col * (bubbles_per_row * bubble_width) + bubble * bubble_width
                   y = row * bubble_height

                   # Add some margin
                   x += bubble_width // 4
                   y += bubble_height // 4

                   w = bubble_width // 2
                   h = bubble_height // 2

                   if x + w < width and y + h < height:
                       bubble_regions.append({
                           'question': col * questions_per_column + row + 1,
                           'answer': chr(ord('A') + bubble),
                           'bbox': (x, y, w, h),
                           'region': gray[y:y+h, x:x+w]
                       })

       return bubble_regions
   ```

3. **Coordinate System Understanding** (45 minutes)
   - Map TOEFL answer sheet layout
   - Understand question numbering (1-60)
   - Calculate relative positions for bubble detection

**Knowledge Checkpoint:**
- How does template matching work in computer vision?
- What are the challenges in detecting grids in real-world images?
- How would you handle slight rotations in answer sheets?

#### **Afternoon Session (2 hours): Bubble Region Extraction**

**Learning Goals:**
- Extract individual bubble regions from answer grid
- Understand region of interest (ROI) extraction
- Prepare extracted regions for classification

**Activities:**
1. **ROI Extraction Implementation** (90 minutes)
   ```python
   # bubble_extraction.py
   import cv2
   import numpy as np
   import matplotlib.pyplot as plt

   def extract_bubble_roi(image, bbox):
       """Extract bubble region of interest"""
       x, y, w, h = bbox
       roi = image[y:y+h, x:x+w]

       # Ensure ROI is valid
       if roi.size == 0:
           return None

       # Resize to standard size for consistency
       roi_resized = cv2.resize(roi, (40, 40))

       return roi_resized

   def visualize_bubble_extraction(image_path, num_samples=12):
       """Visualize extracted bubble regions"""

       bubble_regions = find_bubble_regions(image_path)

       if len(bubble_regions) < num_samples:
           num_samples = len(bubble_regions)

       fig, axes = plt.subplots(3, 4, figsize=(12, 9))
       axes = axes.flatten()

       for i in range(num_samples):
           bubble = bubble_regions[i]
           roi = extract_bubble_roi(
               cv2.imread(image_path, cv2.IMREAD_GRAYSCALE),
               bubble['bbox']
           )

           if roi is not None:
               axes[i].imshow(roi, cmap='gray')
               axes[i].set_title(f"Q{bubble['question']}-{bubble['answer']}")
               axes[i].axis('off')

       plt.tight_layout()
       plt.savefig('datasets/analysis/bubble_extraction.png', dpi=300)
       plt.show()

   # Test bubble extraction
   if __name__ == "__main__":
       sample_path = "datasets/samples/sample_image.jpg"
       visualize_bubble_extraction(sample_path)
   ```

2. **Quality Assessment** (30 minutes)
   - Evaluate extraction accuracy
   - Identify common problems (misalignment, size variations)
   - Document areas for improvement

**Daily Deliverable:**
- Create `day4-template-detection.md` with grid detection results

---

### **Day 5: Bubble Classification Basics**

#### **Morning Session (3 hours): Fill Detection Algorithm**

**Learning Goals:**
- Understand how to determine if a bubble is filled
- Implement pixel counting approach
- Handle edge cases and noise

**Activities:**
1. **Fill Detection Theory** (45 minutes)
   - Study pixel intensity analysis
   - Understand threshold-based classification
   - Learn about confidence scoring methods

2. **Basic Classification Implementation** (90 minutes)
   ```python
   # bubble_classifier.py
   import cv2
   import numpy as np

   class BubbleClassifier:
       def __init__(self, fill_threshold=0.3, confidence_threshold=0.7):
           self.fill_threshold = fill_threshold
           self.confidence_threshold = confidence_threshold

       def classify_bubble(self, bubble_roi):
           """Classify if bubble is filled or empty"""

           if bubble_roi is None or bubble_roi.size == 0:
               return {
                   'filled': False,
                   'confidence': 0.0,
                   'fill_ratio': 0.0,
                   'status': 'invalid'
               }

           # Ensure grayscale
           if len(bubble_roi.shape) == 3:
               bubble_roi = cv2.cvtColor(bubble_roi, cv2.COLOR_BGR2GRAY)

           # Apply preprocessing
           blurred = cv2.GaussianBlur(bubble_roi, (3, 3), 0)
           _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)

           # Calculate fill ratio
           total_pixels = thresh.size
           filled_pixels = np.sum(thresh == 255)
           fill_ratio = filled_pixels / total_pixels

           # Determine if filled
           is_filled = fill_ratio > self.fill_threshold

           # Calculate confidence based on how clear the decision is
           distance_from_threshold = abs(fill_ratio - self.fill_threshold)
           confidence = min(1.0, distance_from_threshold * 2)

           # Determine status
           if confidence < self.confidence_threshold:
               status = 'uncertain'
           elif is_filled:
               status = 'filled'
           else:
               status = 'empty'

           return {
               'filled': is_filled,
               'confidence': confidence,
               'fill_ratio': fill_ratio,
               'status': status
           }

       def classify_question(self, bubble_rois):
           """Classify all bubbles for one question (A-E)"""

           results = {}
           answers = ['A', 'B', 'C', 'D', 'E']

           for i, roi in enumerate(bubble_rois):
               answer = answers[i] if i < len(answers) else f'Option{i+1}'
               results[answer] = self.classify_bubble(roi)

           # Determine final answer
           filled_answers = [ans for ans, result in results.items()
                           if result['filled'] and result['confidence'] > self.confidence_threshold]

           if len(filled_answers) == 1:
               final_answer = filled_answers[0]
               status = 'valid'
           elif len(filled_answers) > 1:
               final_answer = 'MULTIPLE'
               status = 'multiple_marks'
           else:
               final_answer = 'BLANK'
               status = 'no_mark'

           return {
               'answer': final_answer,
               'status': status,
               'bubble_results': results
           }

   def test_classifier(image_path):
       """Test bubble classifier on sample image"""

       classifier = BubbleClassifier()
       bubble_regions = find_bubble_regions(image_path)

       # Test first few questions
       img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

       test_results = []
       for q in range(1, 4):  # Test first 3 questions
           question_bubbles = [b for b in bubble_regions if b['question'] == q]

           bubble_rois = []
           for bubble in question_bubbles:
               roi = extract_bubble_roi(img, bubble['bbox'])
               bubble_rois.append(roi)

           result = classifier.classify_question(bubble_rois)
           result['question'] = q
           test_results.append(result)

       return test_results
   ```

3. **Parameter Tuning** (45 minutes)
   - Experiment with different threshold values
   - Test on various image qualities
   - Document optimal parameters for different conditions

**Knowledge Checkpoint:**
- How do you determine if a bubble is filled using pixel analysis?
- What factors affect classification accuracy?
- How would you handle partially filled bubbles?

#### **Afternoon Session (2 hours): Testing and Validation**

**Learning Goals:**
- Test bubble classification on real images
- Measure accuracy and identify failure cases
- Understand the importance of validation in computer vision

**Activities:**
1. **Manual Ground Truth Creation** (60 minutes)
   ```python
   # ground_truth_creator.py
   import cv2
   import json

   def create_ground_truth(image_path, output_path):
       """Interactive ground truth creation tool"""

       img = cv2.imread(image_path)
       bubble_regions = find_bubble_regions(image_path)

       ground_truth = {}

       print("Ground Truth Creation Tool")
       print("For each question, enter the correct answer (A-E) or 'BLANK':")

       for q in range(1, 11):  # First 10 questions for testing
           question_bubbles = [b for b in bubble_regions if b['question'] == q]

           # Show bubble regions for this question
           question_img = img.copy()
           for bubble in question_bubbles:
               x, y, w, h = bubble['bbox']
               cv2.rectangle(question_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
               cv2.putText(question_img, bubble['answer'],
                          (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

           cv2.imshow(f'Question {q}', question_img)
           cv2.waitKey(1000)  # Show for 1 second

           answer = input(f"Question {q} answer: ").upper().strip()
           ground_truth[q] = answer

           cv2.destroyAllWindows()

       # Save ground truth
       with open(output_path, 'w') as f:
           json.dump(ground_truth, f, indent=2)

       return ground_truth
   ```

2. **Accuracy Measurement** (60 minutes)
   ```python
   # accuracy_evaluator.py
   import json

   def evaluate_accuracy(predictions, ground_truth):
       """Evaluate classification accuracy"""

       correct = 0
       total = 0
       errors = []

       for question, true_answer in ground_truth.items():
           if question in predictions:
               pred_answer = predictions[question]['answer']

               if pred_answer == true_answer:
                   correct += 1
               else:
                   errors.append({
                       'question': question,
                       'predicted': pred_answer,
                       'actual': true_answer
                   })

               total += 1

       accuracy = correct / total if total > 0 else 0

       return {
           'accuracy': accuracy,
           'correct': correct,
           'total': total,
           'errors': errors
       }

   def detailed_error_analysis(errors):
       """Analyze types of errors"""

       error_types = {
           'false_positive': 0,  # Detected fill when empty
           'false_negative': 0,  # Missed filled bubble
           'multiple_marks': 0,  # Multiple bubbles detected
           'wrong_bubble': 0     # Wrong bubble in correct question
       }

       for error in errors:
           if error['predicted'] == 'MULTIPLE':
               error_types['multiple_marks'] += 1
           elif error['predicted'] == 'BLANK':
               error_types['false_negative'] += 1
           elif error['actual'] == 'BLANK':
               error_types['false_positive'] += 1
           else:
               error_types['wrong_bubble'] += 1

       return error_types
   ```

**Daily Deliverable:**
- Create `day5-classification-results.md` with accuracy measurements

---

### **Day 6: Integration and Testing**

#### **Morning Session (3 hours): Complete Pipeline Integration**

**Learning Goals:**
- Combine all components into a complete OMR processor
- Implement proper error handling and logging
- Test end-to-end functionality

**Activities:**
1. **Pipeline Integration** (90 minutes)
   ```python
   # omr_processor.py
   import cv2
   import numpy as np
   import json
   from datetime import datetime

   class OMRProcessor:
       def __init__(self, config=None):
           self.config = config or self.default_config()
           self.classifier = BubbleClassifier(
               fill_threshold=self.config['fill_threshold'],
               confidence_threshold=self.config['confidence_threshold']
           )

       def default_config(self):
           return {
               'fill_threshold': 0.3,
               'confidence_threshold': 0.7,
               'min_bubble_area': 100,
               'max_bubble_area': 2000,
               'expected_questions': 60
           }

       def process_answer_sheet(self, image_path, answer_key=None):
           """Complete OMR processing pipeline"""

           try:
               # Step 1: Load and validate image
               img = cv2.imread(image_path)
               if img is None:
                   raise ValueError(f"Could not load image: {image_path}")

               # Step 2: Detect bubble regions
               bubble_regions = find_bubble_regions(image_path)

               if not bubble_regions:
                   raise ValueError("No bubble regions detected")

               # Step 3: Process each question
               results = {}
               for q in range(1, self.config['expected_questions'] + 1):
                   question_bubbles = [b for b in bubble_regions if b['question'] == q]

                   if len(question_bubbles) != 5:  # Should have A, B, C, D, E
                       results[q] = {
                           'answer': 'ERROR',
                           'status': 'missing_bubbles',
                           'confidence': 0.0
                       }
                       continue

                   # Extract ROIs
                   gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                   bubble_rois = []
                   for bubble in question_bubbles:
                       roi = extract_bubble_roi(gray_img, bubble['bbox'])
                       bubble_rois.append(roi)

                   # Classify question
                   result = self.classifier.classify_question(bubble_rois)
                   results[q] = result

               # Step 4: Calculate score if answer key provided
               score_info = None
               if answer_key:
                   score_info = self.calculate_score(results, answer_key)

               return {
                   'status': 'success',
                   'timestamp': datetime.now().isoformat(),
                   'image_path': image_path,
                   'results': results,
                   'score': score_info,
                   'config': self.config
               }

           except Exception as e:
               return {
                   'status': 'error',
                   'error': str(e),
                   'timestamp': datetime.now().isoformat(),
                   'image_path': image_path
               }

       def calculate_score(self, results, answer_key):
           """Calculate score based on answer key"""

           correct = 0
           total = 0
           errors = []

           for question, correct_answer in answer_key.items():
               if int(question) in results:
                   student_answer = results[int(question)]['answer']

                   if student_answer == correct_answer:
                       correct += 1
                   elif student_answer not in ['ERROR', 'BLANK', 'MULTIPLE']:
                       errors.append({
                           'question': question,
                           'correct': correct_answer,
                           'student': student_answer
                       })

                   total += 1

           percentage = (correct / total * 100) if total > 0 else 0

           return {
               'correct': correct,
               'total': total,
               'percentage': percentage,
               'errors': errors
           }

   # Test the complete processor
   def test_omr_processor():
       processor = OMRProcessor()

       # Sample answer key
       answer_key = {str(i): chr(ord('A') + i % 5) for i in range(1, 11)}

       sample_path = "datasets/samples/sample_image.jpg"
       result = processor.process_answer_sheet(sample_path, answer_key)

       # Save results
       with open('datasets/analysis/processing_result.json', 'w') as f:
           json.dump(result, f, indent=2)

       return result
   ```

2. **Error Handling and Logging** (90 minutes)
   ```python
   # error_handler.py
   import logging
   import traceback
   from enum import Enum

   class ErrorType(Enum):
       IMAGE_LOAD_ERROR = "image_load_error"
       GRID_DETECTION_ERROR = "grid_detection_error"
       BUBBLE_EXTRACTION_ERROR = "bubble_extraction_error"
       CLASSIFICATION_ERROR = "classification_error"
       VALIDATION_ERROR = "validation_error"

   class OMRLogger:
       def __init__(self, log_file='logs/omr_processing.log'):
           self.setup_logging(log_file)

       def setup_logging(self, log_file):
           logging.basicConfig(
               level=logging.INFO,
               format='%(asctime)s - %(levelname)s - %(message)s',
               handlers=[
                   logging.FileHandler(log_file),
                   logging.StreamHandler()
               ]
           )
           self.logger = logging.getLogger(__name__)

       def log_processing_start(self, image_path):
           self.logger.info(f"Starting OMR processing for: {image_path}")

       def log_processing_complete(self, image_path, duration, results):
           self.logger.info(
               f"Completed OMR processing for: {image_path} "
               f"in {duration:.2f}s. Success: {results['status'] == 'success'}"
           )

       def log_error(self, error_type, message, image_path=None):
           error_msg = f"Error ({error_type.value}): {message}"
           if image_path:
               error_msg += f" - Image: {image_path}"

           self.logger.error(error_msg)
           self.logger.error(traceback.format_exc())
   ```

**Knowledge Checkpoint:**
- Can you process a complete answer sheet end-to-end?
- How does your system handle errors and edge cases?
- What's the processing time for a typical image?

#### **Afternoon Session (2 hours): Performance Testing & Documentation**

**Learning Goals:**
- Measure system performance on various test cases
- Document processing pipeline and results
- Identify areas for improvement

**Activities:**
1. **Performance Benchmarking** (90 minutes)
   ```python
   # performance_tester.py
   import time
   import os
   from statistics import mean, stdev

   def benchmark_processor(test_images_dir, iterations=3):
       """Benchmark OMR processor performance"""

       processor = OMRProcessor()
       results = []

       test_images = [f for f in os.listdir(test_images_dir)
                     if f.lower().endswith(('.jpg', '.png'))]

       for image_file in test_images:
           image_path = os.path.join(test_images_dir, image_file)
           image_times = []

           for i in range(iterations):
               start_time = time.time()
               result = processor.process_answer_sheet(image_path)
               end_time = time.time()

               processing_time = end_time - start_time
               image_times.append(processing_time)

           avg_time = mean(image_times)
           std_time = stdev(image_times) if len(image_times) > 1 else 0

           results.append({
               'image': image_file,
               'avg_time': avg_time,
               'std_time': std_time,
               'success': result['status'] == 'success'
           })

       return results

   def generate_performance_report(benchmark_results):
       """Generate performance analysis report"""

       successful_times = [r['avg_time'] for r in benchmark_results if r['success']]
       success_rate = len(successful_times) / len(benchmark_results)

       if successful_times:
           avg_processing_time = mean(successful_times)
           fastest_time = min(successful_times)
           slowest_time = max(successful_times)
       else:
           avg_processing_time = 0
           fastest_time = 0
           slowest_time = 0

       report = f"""
   # OMR Processor Performance Report

   ## Summary
   - Total images tested: {len(benchmark_results)}
   - Success rate: {success_rate:.1%}
   - Average processing time: {avg_processing_time:.2f}s
   - Fastest processing: {fastest_time:.2f}s
   - Slowest processing: {slowest_time:.2f}s

   ## Individual Results
   """

       for result in benchmark_results:
           status = "✅" if result['success'] else "❌"
           report += f"- {result['image']}: {result['avg_time']:.2f}s {status}\n"

       return report
   ```

2. **Week 1 Documentation Compilation** (30 minutes)
   - Consolidate all daily notes into comprehensive week summary
   - Document lessons learned and challenges encountered
   - Prepare foundation for Week 2 development

**Daily Deliverable:**
- Create `day6-integration-testing.md` with performance benchmarks

---

### **Day 7: Review, Documentation & Week 2 Preparation**

#### **Full Day Session (4-5 hours): Comprehensive Review**

**Learning Goals:**
- Review all Week 1 learning objectives and achievements
- Create comprehensive documentation for academic submission
- Prepare development foundation for Week 2

**Activities:**
1. **Code Review and Cleanup** (90 minutes)
   - Review all code written during the week
   - Add comprehensive comments and documentation
   - Organize code into proper modules and structure

2. **Academic Documentation Creation** (120 minutes)
   ```markdown
   # Week 1 Academic Report Template

   ## Executive Summary
   - Project overview and objectives
   - Week 1 achievements summary
   - Key technical insights gained

   ## Learning Objectives Assessment
   ### Objective 1: Project Understanding ✅
   - [Evidence of understanding]

   ### Objective 2: Environment Setup ✅
   - [Documentation of setup process]

   ### Objective 3: Dataset Analysis ✅
   - [Analysis results and insights]

   ### Objective 4: OpenCV Experiments ✅
   - [Experimental results and learnings]

   ### Objective 5: Documentation ✅
   - [Documentation deliverables completed]

   ## Technical Implementation
   ### Image Preprocessing Pipeline
   - Algorithm description
   - Code implementation
   - Test results

   ### Template Detection Approach
   - Methodology explanation
   - Implementation details
   - Performance analysis

   ### Bubble Classification System
   - Classification algorithm
   - Accuracy measurements
   - Error analysis

   ## Dataset Analysis Results
   ### Quality Categorization
   - High quality: X images
   - Medium quality: Y images
   - Low quality: Z images

   ### Processing Challenges Identified
   - Lighting variations
   - Image rotation/skew
   - Template variations

   ## Performance Metrics
   - Processing time: X seconds average
   - Classification accuracy: Y% on test set
   - Success rate: Z% on varied quality images

   ## Lessons Learned
   ### Technical Insights
   - [Key technical discoveries]

   ### Development Process
   - [Process improvement insights]

   ### Academic Methodology
   - [Documentation and research insights]

   ## Week 2 Preparation
   ### Technical Foundation Ready
   - [List of completed components]

   ### Identified Areas for Improvement
   - [Areas needing enhancement]

   ### Development Roadmap
   - [Plan for Week 2 activities]

   ## Appendices
   ### Appendix A: Code Listings
   ### Appendix B: Test Results
   ### Appendix C: Performance Benchmarks
   ```

3. **Week 2 Planning Session** (60 minutes)
   - Review Week 2 objectives from implementation guide
   - Identify potential challenges based on Week 1 learnings
   - Set up development infrastructure for more complex development

**Knowledge Checkpoint - Week 1 Final Assessment:**
- Can you process an OMR image end-to-end with reasonable accuracy?
- Do you understand the core challenges in computer vision for OMR?
- Are you prepared to begin building the web application components?
- Have you documented your learning process adequately for academic evaluation?

---

## 📊 Knowledge Checkpoints Summary

### **Day 1 Checkpoint: Foundation Understanding**
- [ ] Can explain OMR system purpose and applications
- [ ] Understands project scope and constraints
- [ ] Successfully configured Python development environment
- [ ] Verified OpenCV installation and basic functionality

### **Day 2 Checkpoint: Data Competency**
- [ ] Successfully downloaded and organized Kaggle OMR dataset
- [ ] Can categorize images by quality levels
- [ ] Understands various challenges in real-world OMR images
- [ ] Created systematic data organization structure

### **Day 3 Checkpoint: Image Processing Fundamentals**
- [ ] Understands grayscale conversion and its importance
- [ ] Can implement basic preprocessing pipeline
- [ ] Knows difference between binary and adaptive thresholding
- [ ] Successfully detects contours and filters by properties

### **Day 4 Checkpoint: Template Detection**
- [ ] Understands template matching concepts
- [ ] Can detect grid structures in answer sheets
- [ ] Successfully extracts individual bubble regions
- [ ] Understands coordinate systems for bubble mapping

### **Day 5 Checkpoint: Classification Skills**
- [ ] Implemented pixel-based fill detection algorithm
- [ ] Can measure classification accuracy
- [ ] Understands confidence scoring and uncertainty handling
- [ ] Created ground truth data for validation

### **Day 6 Checkpoint: Integration Competency**
- [ ] Successfully integrated all components into complete pipeline
- [ ] Implemented proper error handling and logging
- [ ] Measured end-to-end system performance
- [ ] Can process real answer sheets with reasonable accuracy

### **Day 7 Checkpoint: Academic Readiness**
- [ ] Created comprehensive documentation of all work
- [ ] Demonstrated academic-level analysis and reporting
- [ ] Prepared foundation for Week 2 development
- [ ] Achieved all Week 1 learning objectives

---

## 🚨 Common Pitfalls & How to Avoid Them

### **Technical Pitfalls**

#### **1. OpenCV Installation Issues**
- **Problem:** Import errors, missing dependencies
- **Solution:** Use virtual environments, install specific versions
- **Prevention:** Follow exact installation commands, test immediately

#### **2. Image Path Problems**
- **Problem:** File not found errors, path separators
- **Solution:** Use absolute paths, cross-platform path handling
- **Prevention:** Always verify file existence before processing

#### **3. Coordinate System Confusion**
- **Problem:** Incorrect bubble detection due to coordinate errors
- **Solution:** Draw debug rectangles, verify coordinates visually
- **Prevention:** Test with simple, known examples first

#### **4. Threshold Parameter Issues**
- **Problem:** Poor classification due to wrong thresholds
- **Solution:** Make parameters configurable, test on various images
- **Prevention:** Start with literature values, tune systematically

### **Academic Pitfalls**

#### **1. Insufficient Documentation**
- **Problem:** Cannot explain implementation decisions
- **Solution:** Document while coding, not after
- **Prevention:** Create daily learning logs

#### **2. Unrealistic Expectations**
- **Problem:** Expecting perfect accuracy immediately
- **Solution:** Set realistic targets (75-85% for academic project)
- **Prevention:** Research typical OMR system performance

#### **3. Scope Creep**
- **Problem:** Adding unnecessary features
- **Solution:** Focus on core requirements first
- **Prevention:** Review project scope daily

#### **4. Poor Time Management**
- **Problem:** Spending too much time on one component
- **Solution:** Use timeboxing, stick to daily schedules
- **Prevention:** Set realistic daily goals

### **Development Pitfalls**

#### **1. No Version Control**
- **Problem:** Losing work, cannot track changes
- **Solution:** Use Git from day 1, commit frequently
- **Prevention:** Initialize repository before starting

#### **2. Hardcoded Values**
- **Problem:** Code only works for specific images
- **Solution:** Use configuration files, parameters
- **Prevention:** Think about generalization from start

#### **3. No Error Handling**
- **Problem:** System crashes on edge cases
- **Solution:** Add try-catch blocks, validate inputs
- **Prevention:** Test with problematic images early

---

## 📚 Resources & References

### **Essential OpenCV Documentation**
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [Image Processing in OpenCV](https://docs.opencv.org/4.x/d2/d96/tutorial_py_table_of_contents_imgproc.html)
- [Contour Features](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html)

### **Computer Vision Fundamentals**
- [Digital Image Processing by Gonzalez & Woods](https://www.imageprocessingplace.com/)
- [OpenCV Python Tutorial](https://opencv-python-tutroals.readthedocs.io/)
- [Computer Vision: Algorithms and Applications by Szeliski](http://szeliski.org/Book/)

### **OMR-Specific Resources**
- [OMR Technology Overview](https://en.wikipedia.org/wiki/Optical_mark_recognition)
- [Academic Papers on OMR Systems](https://scholar.google.com/scholar?q=optical+mark+recognition+image+processing)
- [Kaggle OMR Dataset](https://www.kaggle.com/datasets/collinslemeke/omr-dataset)

### **Python Development Tools**
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [NumPy Documentation](https://numpy.org/doc/stable/)
- [Matplotlib Tutorials](https://matplotlib.org/stable/tutorials/index.html)

### **Academic Writing Resources**
- [IEEE Paper Format Guidelines](https://www.ieee.org/conferences/publishing/templates.html)
- [Technical Writing Guide](https://developers.google.com/tech-writing)
- [Academic Citation Formats](https://www.citationmachine.net/)

### **Development Best Practices**
- [Python Code Style Guide (PEP 8)](https://pep8.org/)
- [Git Best Practices](https://git-scm.com/book)
- [Code Documentation Standards](https://peps.python.org/pep-0257/)

---

## 📝 Practical Exercises Summary

### **Exercise 1: Environment Verification (Day 1)**
```python
# Complete this verification script
import cv2
import numpy as np
import matplotlib.pyplot as plt

def verify_environment():
    """Verify all required tools are working"""
    # TODO: Test OpenCV image loading
    # TODO: Test NumPy array operations
    # TODO: Test Matplotlib display
    pass
```

### **Exercise 2: Dataset Quality Analysis (Day 2)**
```python
# Implement automated quality assessment
def analyze_dataset_quality(dataset_path):
    """Analyze and categorize dataset by quality metrics"""
    # TODO: Implement brightness analysis
    # TODO: Implement contrast measurement
    # TODO: Implement sharpness detection
    # TODO: Create quality categories
    pass
```

### **Exercise 3: Preprocessing Pipeline (Day 3)**
```python
# Create configurable preprocessing pipeline
def create_preprocessing_pipeline():
    """Build flexible preprocessing pipeline"""
    # TODO: Implement grayscale conversion
    # TODO: Add noise reduction
    # TODO: Implement adaptive thresholding
    # TODO: Add morphological operations
    pass
```

### **Exercise 4: Grid Detection (Day 4)**
```python
# Implement robust grid detection
def detect_answer_grid(image):
    """Detect answer grid with rotation handling"""
    # TODO: Implement line detection
    # TODO: Handle rotation correction
    # TODO: Extract grid coordinates
    # TODO: Validate grid structure
    pass
```

### **Exercise 5: Bubble Classification (Day 5)**
```python
# Implement intelligent bubble classifier
def classify_bubbles(bubble_regions):
    """Classify bubbles with confidence scoring"""
    # TODO: Implement fill detection
    # TODO: Add confidence calculation
    # TODO: Handle edge cases
    # TODO: Return structured results
    pass
```

### **Exercise 6: Complete Integration (Day 6)**
```python
# Build complete OMR processing system
class OMRSystem:
    def process_answer_sheet(self, image_path, answer_key):
        """Complete end-to-end processing"""
        # TODO: Integrate all components
        # TODO: Add error handling
        # TODO: Calculate final score
        # TODO: Generate detailed report
        pass
```

---

## ✅ Week 1 Success Criteria

### **Minimum Achievement Level (Pass)**
- [ ] Development environment successfully configured
- [ ] Dataset downloaded and organized
- [ ] Basic image preprocessing pipeline working
- [ ] Can detect some bubbles in good quality images
- [ ] Basic classification algorithm implemented
- [ ] Documented daily learning progress

### **Good Achievement Level (B Grade)**
- [ ] All minimum criteria plus:
- [ ] Robust preprocessing handling various image qualities
- [ ] Template detection working on most images
- [ ] Classification accuracy >70% on test images
- [ ] Complete integration with error handling
- [ ] Comprehensive documentation with analysis

### **Excellent Achievement Level (A Grade)**
- [ ] All good criteria plus:
- [ ] Advanced preprocessing with rotation correction
- [ ] Robust template detection >85% success rate
- [ ] Classification accuracy >80% with confidence scoring
- [ ] Performance optimization and benchmarking
- [ ] Academic-quality documentation with insights
- [ ] Prepared foundation for advanced Week 2 development

---

## 🎯 Preparation for Week 2

### **Technical Foundation Ready**
- [ ] Core image processing pipeline complete and tested
- [ ] Bubble detection and classification algorithms validated
- [ ] Code organized in reusable modules
- [ ] Test framework established
- [ ] Performance benchmarks documented

### **Development Environment Enhanced**
- [ ] Web development tools installed (Node.js, npm)
- [ ] Database tools prepared (Supabase account)
- [ ] API development tools ready (Postman, Thunder Client)
- [ ] Version control workflow established

### **Academic Documentation Advanced**
- [ ] Technical methodology documented
- [ ] Initial literature review completed
- [ ] Problem analysis and solution approach defined
- [ ] Week 1 results ready for academic report
- [ ] Research questions refined for Week 2

---

**🎓 Week 1 Learning Roadmap Complete**

This comprehensive roadmap provides a structured, educational approach to mastering the foundations of OMR systems using computer vision. Each day builds progressively on previous knowledge while maintaining academic rigor and practical application focus.

**Next Steps:** Proceed to Week 2 with confidence in your image processing foundations, ready to tackle full-stack web development and system integration challenges.