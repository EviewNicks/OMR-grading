# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sistem Penilaian Otomatis Ujian Pilihan Ganda** - OMR (Optical Mark Recognition) grading system for TOEFL-style answer sheets. This is an 8-week academic project for Digital Image Processing course, focusing on simple but solid implementation using basic OpenCV techniques.

## Architecture & Tech Stack

### Full-Stack Architecture
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

### Core Technologies
- **Backend**: FastAPI (Python) with OpenCV for image processing
- **Frontend**: Next.js (React) with TypeScript
- **Database**: Supabase (PostgreSQL)
- **Image Processing**: OpenCV, NumPy, Pillow
- **Deployment**: Vercel (frontend) + Railway (backend)

## Project Structure

```
project/
├── docs/                           # Comprehensive project documentation
│   ├── project.md                  # Main project specification
│   ├── technical-specifications.md # Detailed tech specs and schemas
│   ├── implementation-guide.md     # 8-week development timeline
│   ├── api-documentation.md        # Complete API reference
│   └── week1/                      # Week-specific documentation
├── Dataset/                        # Kaggle OMR dataset (train/test/valid)
├── backend/                        # FastAPI application (to be created)
├── frontend/                       # Next.js application (to be created)
└── scripts/                        # Utility scripts (to be created)
```

## Development Commands

### Environment Setup
```bash
# Create and activate Python virtual environment
python -m venv omr_env
# Windows
omr_env\Scripts\activate
# Linux/Mac
source omr_env/bin/activate

# Install core dependencies
pip install fastapi==0.104.1 uvicorn==0.24.0 opencv-python==4.8.1.78 numpy==1.24.3 pillow==10.0.1 supabase==2.0.0 pydantic==2.4.2 python-multipart==0.0.6

# For frontend setup
npm install
# or
yarn install
```

### Development Server Commands
```bash
# Backend (FastAPI)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Next.js)
cd frontend
npm run dev
# or
yarn dev

# Access API documentation
open http://localhost:8000/docs
```

### Testing Commands
```bash
# Run image processing tests
python -m pytest tests/test_image_processing.py -v

# Test with sample images
python scripts/test_omr_pipeline.py --image Dataset/test/sample_image.jpg

# Run environment validation
python scripts/validate_environment.py
```

## Core Image Processing Pipeline

The system processes 60-question TOEFL-style answer sheets (A-E choices) using this pipeline:

1. **Preprocessing**: Grayscale → Gaussian Blur → Adaptive Threshold
2. **Template Detection**: Find 3x20 grid using contour detection
3. **Bubble Extraction**: Extract individual bubble regions
4. **Classification**: Pixel counting to determine filled bubbles
5. **Answer Extraction**: Map detected answers to question numbers
6. **Scoring**: Compare with answer key and calculate results

### Key Processing Functions
- `process_omr_image()`: Main processing pipeline
- `detect_answer_grid()`: Template detection algorithm
- `classify_bubbles()`: Filled vs empty bubble classification
- `calculate_confidence()`: Confidence scoring for results

## Database Schema

### Core Tables
```sql
-- Answer keys storage
answer_keys: id, exam_name, total_questions, answers(JSONB), created_at

-- Student submissions
student_submissions: id, student_id, image_url, original_filename, upload_timestamp, processing_status

-- Processing results
processing_results: id, submission_id, answer_key_id, detected_answers(JSONB), confidence_scores(JSONB), total_score, flagged_questions(JSONB)
```

## API Endpoints Structure

### Core Endpoints
- `POST /api/upload-answer-key`: Store exam answer keys
- `POST /api/upload-image`: Upload student answer sheets
- `POST /api/process-image/{submission_id}`: Process image and extract answers
- `GET /api/results/{submission_id}`: Retrieve processing results
- `GET /api/export-csv/{submission_id}`: Export results as CSV

### Response Format
All API responses follow consistent JSON structure:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-09-21T10:30:00Z"
}
```

## Performance Targets

- **Processing Time**: 2-5 seconds per image
- **Accuracy**: 75-85% overall system accuracy (academic prototype)
- **Bubble Detection**: 80-90% under normal conditions
- **Template Recognition**: 85%+ success rate
- **File Size**: Maximum 5MB upload
- **Concurrent Users**: 1-5 (academic prototype)

## Development Workflow

### 8-Week Implementation Timeline
- **Week 1-3**: Foundation (Environment + Image Processing)
- **Week 4-6**: Integration (Full-stack + Database)
- **Week 7-8**: Testing & Documentation

### Daily Development Pattern
1. Environment validation with `scripts/validate_environment.py`
2. Test changes with sample images from `Dataset/test/`
3. Run processing pipeline tests
4. Update documentation in Indonesian for academic requirements

## Academic Requirements

### Documentation Standards
- **Language**: Indonesian for academic reports
- **Comments**: Comprehensive function documentation in Indonesian
- **Testing**: Include test cases with sample images
- **Report**: 20-30 page technical report required

### Key Success Metrics
- Working end-to-end system (40% of grade)
- Clean, documented code (30% of grade)
- Comprehensive academic report (20% of grade)
- Innovation and problem-solving (10% of grade)

## Dataset Organization

The project uses Kaggle OMR Dataset with images organized by quality and processing difficulty. Dataset structure should support incremental development from simple to complex cases.

## Error Handling

### Common Processing Errors
- `TEMPLATE_DETECTION_FAILED`: Cannot locate answer grid
- `PROCESSING_FAILED`: General image processing failure
- `FILE_TOO_LARGE`: Upload size exceeded
- `INVALID_FILE_TYPE`: Unsupported file format

### Debugging Approach
1. Validate image quality and resolution
2. Check template visibility and lighting
3. Verify proper grid detection
4. Analyze bubble classification confidence

## Development Notes

- Keep implementation simple and academic-focused
- Use basic OpenCV techniques (no ML/AI required)
- Focus on solid implementation over cutting-edge features
- Academic prototype design (not production-scale)
- Document all image processing decisions with rationale
- Include performance benchmarks and accuracy metrics

## Deployment

### Free Tier Deployment Stack
- **Frontend**: Vercel (auto-deploy from Git)
- **Backend**: Railway (Python runtime)
- **Database**: Supabase (PostgreSQL + File Storage)
- **Total Cost**: $0 (perfect for academic project)

---

**Project Type**: Academic Prototype
**Duration**: 8 weeks
**Focus**: Solid implementation with educational value
**Success Criteria**: Working system + comprehensive documentation