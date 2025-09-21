# Technical Specifications - OMR Grading System

**Project:** Sistem Penilaian Otomatis Ujian Pilihan Ganda
**Course:** Pengolahan Citra Digital
**Approach:** Simple & Academic-Focused

---

## 📋 System Overview

Sistem sederhana untuk memproses lembar jawaban TOEFL-style menggunakan teknik basic image processing. Focus pada implementasi yang solid dan dapat dipahami untuk keperluan akademik.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js       │    │    FastAPI      │    │   Supabase      │
│   Frontend      │◄──►│    Backend      │◄──►│   Database      │
│                 │    │                 │    │                 │
│ - File Upload   │    │ - Image Proc.   │    │ - PostgreSQL    │
│ - Results View  │    │ - OpenCV        │    │ - File Storage  │
│ - CSV Export    │    │ - Answer Ext.   │    │ - Session Data  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │  Task Queue     │
                       │ (Optional Async)│
                       └─────────────────┘
```

## 🛠️ Technology Stack Detailed

### **Backend - FastAPI (Python)**

```python
Core Dependencies:
├── fastapi==0.104.1          # Web framework
├── uvicorn==0.24.0           # ASGI server
├── opencv-python==4.8.1.78  # Image processing
├── numpy==1.24.3             # Numerical operations
├── pillow==10.0.1            # Image handling
├── supabase==2.0.0           # Database client
├── redis==5.0.0              # Task queue
├── pydantic==2.4.2           # Data validation
└── python-multipart==0.0.6   # File upload support
```

### **Frontend - Next.js (React)**

```json
Core Dependencies:
{
  "next": "14.0.0",
  "react": "18.2.0",
  "typescript": "5.2.2",
  "@supabase/supabase-js": "2.38.0",
  "tailwindcss": "3.3.5",
  "axios": "1.6.0",
  "react-dropzone": "14.2.3",
  "recharts": "2.8.0"
}
```

### **Database - Supabase (PostgreSQL)**

```sql
-- Core tables structure
Tables:
├── answer_keys         # Stored answer keys
├── student_submissions # Uploaded answer sheets
├── processing_results  # Extracted answers and scores
└── session_logs        # Processing history
```

## 📊 Database Schema

### **1. answer_keys**

```sql
CREATE TABLE answer_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_name VARCHAR(255) NOT NULL,
    total_questions INTEGER DEFAULT 60,
    answers JSONB NOT NULL, -- {"1": "A", "2": "B", ...}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **2. student_submissions**

```sql
CREATE TABLE student_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id VARCHAR(100),
    image_url TEXT NOT NULL,
    original_filename VARCHAR(255),
    file_size INTEGER,
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    processing_status VARCHAR(50) DEFAULT 'pending'
);
```

### **3. processing_results**

```sql
CREATE TABLE processing_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID REFERENCES student_submissions(id),
    answer_key_id UUID REFERENCES answer_keys(id),
    detected_answers JSONB, -- {"1": "A", "2": "B", ...}
    confidence_scores JSONB, -- {"1": 0.95, "2": 0.87, ...}
    total_score INTEGER,
    max_score INTEGER DEFAULT 60,
    percentage DECIMAL(5,2),
    flagged_questions JSONB, -- [1, 5, 23] (question numbers)
    processing_time_ms INTEGER,
    processed_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Image Processing Pipeline

### **Core OpenCV Operations**

```python
def process_omr_image(image_path: str) -> dict:
    """
    Main image processing pipeline

    Steps:
    1. Load and preprocess image
    2. Detect answer grid template
    3. Extract individual bubble regions
    4. Classify each bubble (filled/empty)
    5. Determine answers per question
    6. Return structured results
    """

    # 1. Preprocessing
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # 2. Template detection
    grid_contours = detect_answer_grid(thresh)

    # 3. Bubble extraction
    bubble_regions = extract_bubble_regions(grid_contours, img.shape)

    # 4. Classification
    answers = {}
    for question_num, bubbles in bubble_regions.items():
        filled_bubble = classify_bubbles(bubbles, thresh)
        answers[question_num] = filled_bubble

    return {
        "answers": answers,
        "confidence": calculate_confidence(bubble_regions, thresh),
        "flagged": detect_ambiguous_answers(bubble_regions, thresh)
    }
```

### **Template Detection Strategy**

```python
def detect_answer_grid(thresh_image):
    """
    Detect 3x20 grid of answer bubbles

    Approach:
    1. Find large rectangular contours
    2. Apply perspective correction if needed
    3. Locate grid pattern using projection profiles
    4. Return normalized grid coordinates
    """

    # Find contours and filter by area/aspect ratio
    contours, _ = cv2.findContours(thresh_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Look for rectangular shapes that could be the answer area
    potential_grids = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50000:  # Minimum area threshold
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:  # Rectangular shape
                potential_grids.append(approx)

    # Select best candidate based on size and position
    best_grid = select_best_grid_candidate(potential_grids)

    return best_grid
```

### **Bubble Classification Algorithm**

```python
def classify_bubbles(bubble_regions, thresh_image):
    """
    Determine which bubble is filled for each question

    Method: Pixel counting with dynamic thresholding
    """

    bubble_scores = {}

    for choice, bubble_roi in bubble_regions.items():  # A, B, C, D, E
        # Extract bubble region
        x, y, w, h = bubble_roi
        bubble_area = thresh_image[y:y+h, x:x+w]

        # Count black pixels (filled areas)
        black_pixels = cv2.countNonZero(cv2.bitwise_not(bubble_area))
        total_pixels = w * h
        fill_ratio = black_pixels / total_pixels

        bubble_scores[choice] = fill_ratio

    # Determine answer based on highest fill ratio
    if max(bubble_scores.values()) > 0.3:  # Threshold for "filled"
        answer = max(bubble_scores, key=bubble_scores.get)
        confidence = bubble_scores[answer]

        # Check for multiple filled bubbles
        high_scores = [k for k, v in bubble_scores.items() if v > 0.3]
        if len(high_scores) > 1:
            return {"answer": "INVALID", "confidence": 0.0, "flag": "multiple_marks"}

        return {"answer": answer, "confidence": confidence, "flag": None}
    else:
        return {"answer": "BLANK", "confidence": 0.0, "flag": None}
```

## 🔗 API Endpoints

### **FastAPI Backend Endpoints**

```python
# Core endpoints for the OMR system

@app.post("/api/upload-answer-key")
async def upload_answer_key(exam_name: str, answers: dict):
    """Upload and store answer key for an exam"""
    pass

@app.post("/api/upload-image")
async def upload_student_image(file: UploadFile):
    """Upload student answer sheet image"""
    pass

@app.post("/api/process-image")
async def process_image(submission_id: str, answer_key_id: str):
    """Process uploaded image and extract answers"""
    pass

@app.get("/api/results/{submission_id}")
async def get_results(submission_id: str):
    """Get processing results for a submission"""
    pass

@app.get("/api/export-csv/{submission_id}")
async def export_csv(submission_id: str):
    """Export results in CSV format"""
    pass
```

## ⚡ Performance Requirements

### **Processing Speed**

- **Target:** 2-5 seconds per image
- **Image Size:** Max 5MB upload
- **Resolution:** Minimum 800x600 pixels
- **Concurrent Users:** 1-5 (academic prototype)

### **Accuracy Targets**

- **Bubble Detection:** 80-90% under normal conditions
- **Template Recognition:** 85%+ success rate
- **Overall System Accuracy:** 75-85% (sufficient for academic demo)

### **Resource Usage**

- **Memory:** <512MB peak usage
- **CPU:** Standard laptop/desktop performance
- **Storage:** <1GB total (including images)

## 🚀 Deployment Configuration

### **Development Environment**

```bash
# Local development setup
Python 3.9+
Node.js 18+
PostgreSQL 14+ (or Supabase)
Redis 6+ (optional)
```

### **Production Deployment (Free Tier)**

```yaml
Frontend: Vercel
  - Auto-deploy from Git
  - CDN distribution
  - Custom domain support

Backend: Railway
  - Python runtime
  - Auto-scaling
  - Environment variables

Database: Supabase
  - PostgreSQL hosted
  - Real-time subscriptions
  - File storage included

Cache: Redis Cloud
  - Free tier: 30MB
  - Sufficient for session data
```

## 🔒 Security Considerations

### **Data Protection**

- Image files stored with UUID naming
- No sensitive personal data required
- Automatic cleanup after processing
- Environment variables for credentials

### **Input Validation**

- File type restrictions (JPG, PNG only)
- File size limits (5MB max)
- Image dimension validation
- SQL injection prevention (parameterized queries)

## 📈 Monitoring & Logging

### **Basic Logging Strategy**

```python
import logging

# Configure logging for academic project
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('omr_system.log'),
        logging.StreamHandler()
    ]
)

# Key metrics to log:
# - Processing time per image
# - Accuracy rates
# - Error frequencies
# - System resource usage
```

## 🧪 Testing Strategy

### **Test Categories**

1. **Unit Tests:** Individual image processing functions
2. **Integration Tests:** API endpoint functionality
3. **Visual Tests:** Sample image processing accuracy
4. **Performance Tests:** Processing speed validation

### **Test Data Requirements**

- 20+ sample images with known answers
- Various quality levels (good, fair, poor)
- Edge cases (multiple marks, blank answers)
- Performance benchmarks

---

**Document Version:** 1.0
**Last Updated:** September 2024
**Status:** Academic Prototype
