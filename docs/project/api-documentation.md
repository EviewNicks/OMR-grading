# API Documentation - OMR Grading System

**Version:** 1.0.0
**Base URL:** `http://localhost:8000` (Development) | `https://your-app.railway.app` (Production)
**Framework:** FastAPI with automatic OpenAPI documentation

---

## 📖 Overview

RESTful API untuk sistem penilaian otomatis ujian pilihan ganda. API ini menyediakan endpoints untuk mengelola kunci jawaban, mengupload gambar lembar jawaban, memproses gambar menggunakan OpenCV, dan mengekspor hasil.

### **Key Features:**

- ✅ File upload dengan validasi
- ✅ Image processing menggunakan OpenCV
- ✅ Database integration dengan Supabase
- ✅ JSON responses yang konsisten
- ✅ Error handling yang komprehensif
- ✅ CSV export functionality

### **Automatic Documentation:**

FastAPI menyediakan dokumentasi interaktif yang dapat diakses di:

- **Swagger UI:** `{BASE_URL}/docs`
- **ReDoc:** `{BASE_URL}/redoc`

---

## 🔐 Authentication & Security

### **Current Implementation:**

- **Development:** No authentication required (academic prototype)
- **Production:** Basic API key authentication (optional)

### **CORS Configuration:**

```python
# Allowed origins for CORS
allow_origins = [
    "http://localhost:3000",    # Next.js development
    "https://your-frontend.vercel.app"  # Production frontend
]
```

### **Request Headers:**

```http
Content-Type: application/json
Accept: application/json
```

---

## 📊 Response Format

### **Success Response:**

```json
{
    "success": true,
    "data": { ... },
    "message": "Operation completed successfully",
    "timestamp": "2024-09-21T10:30:00Z"
}
```

### **Error Response:**

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": { ... }
    },
    "timestamp": "2024-09-21T10:30:00Z"
}
```

### **HTTP Status Codes:**

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## 🛠️ API Endpoints

### **1. Health Check**

#### `GET /health`

Check if the API server is running and healthy.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-09-21T10:30:00Z",
  "dependencies": {
    "database": "connected",
    "opencv": "loaded",
    "storage": "available"
  }
}
```

**Example:**

```bash
curl -X GET "http://localhost:8000/health"
```

---

### **2. Answer Key Management**

#### `POST /api/upload-answer-key`

Upload dan simpan kunci jawaban untuk ujian.

**Request Body:**

```json
{
  "exam_name": "Final Exam - Pengolahan Citra",
  "total_questions": 60,
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C",
    "...": "...",
    "60": "E"
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "key_id": "550e8400-e29b-41d4-a716-446655440000",
    "exam_name": "Final Exam - Pengolahan Citra",
    "total_questions": 60,
    "created_at": "2024-09-21T10:30:00Z"
  }
}
```

**Validation Rules:**

- `exam_name`: Required, 3-255 characters
- `total_questions`: Integer, 1-100 range
- `answers`: Dict with string keys ("1", "2", ...) and values ("A"-"E")

**Example:**

```bash
curl -X POST "http://localhost:8000/api/upload-answer-key" \
     -H "Content-Type: application/json" \
     -d '{
       "exam_name": "Test Exam",
       "total_questions": 60,
       "answers": {"1": "A", "2": "B", ...}
     }'
```

#### `GET /api/answer-keys/{key_id}`

Retrieve kunci jawaban berdasarkan ID.

**Path Parameters:**

- `key_id` (string): UUID dari answer key

**Response:**

```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "exam_name": "Final Exam - Pengolahan Citra",
        "total_questions": 60,
        "answers": { ... },
        "created_at": "2024-09-21T10:30:00Z"
    }
}
```

#### `GET /api/answer-keys`

List semua answer keys yang tersimpan.

**Query Parameters:**

- `limit` (int): Maximum number of results (default: 10, max: 100)
- `offset` (int): Number of results to skip (default: 0)

**Response:**

```json
{
  "success": true,
  "data": {
    "answer_keys": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "exam_name": "Final Exam",
        "total_questions": 60,
        "created_at": "2024-09-21T10:30:00Z"
      }
    ],
    "total": 1,
    "limit": 10,
    "offset": 0
  }
}
```

---

### **3. Image Upload & Management**

#### `POST /api/upload-image`

Upload gambar lembar jawaban siswa.

**Request:**

- **Method:** POST
- **Content-Type:** multipart/form-data
- **Body:** File upload dengan key "file"

**File Requirements:**

- **Format:** JPG, PNG only
- **Size:** Maximum 5MB
- **Resolution:** Minimum 800x600 pixels recommended

**Response:**

```json
{
  "success": true,
  "data": {
    "submission_id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "student_answer_sheet.jpg",
    "file_size": 2048576,
    "file_type": "image/jpeg",
    "upload_timestamp": "2024-09-21T10:30:00Z",
    "storage_url": "https://supabase.co/storage/...",
    "processing_status": "uploaded"
  }
}
```

**Error Responses:**

```json
// File too large
{
    "success": false,
    "error": {
        "code": "FILE_TOO_LARGE",
        "message": "File size exceeds 5MB limit",
        "max_size": 5242880
    }
}

// Invalid file type
{
    "success": false,
    "error": {
        "code": "INVALID_FILE_TYPE",
        "message": "Only JPG and PNG files are allowed",
        "allowed_types": ["image/jpeg", "image/png"]
    }
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/upload-image" \
     -F "file=@student_answer.jpg"
```

#### `GET /api/submissions/{submission_id}`

Get details dari uploaded image submission.

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "student_id": "20210001",
    "filename": "student_answer_sheet.jpg",
    "file_size": 2048576,
    "upload_timestamp": "2024-09-21T10:30:00Z",
    "processing_status": "uploaded",
    "storage_url": "https://..."
  }
}
```

---

### **4. Image Processing**

#### `POST /api/process-image/{submission_id}`

Process uploaded image dan extract answers menggunakan OpenCV.

**Path Parameters:**

- `submission_id` (string): UUID dari uploaded image

**Request Body:**

```json
{
  "answer_key_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": "20210001", // Optional
  "processing_options": {
    // Optional
    "threshold_method": "adaptive",
    "confidence_threshold": 0.6,
    "flag_uncertain": true
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "submission_id": "123e4567-e89b-12d3-a456-426614174000",
    "processing_result": {
      "detected_answers": {
        "1": "A",
        "2": "B",
        "3": "BLANK",
        "4": "C",
        "...": "...",
        "60": "E"
      },
      "confidence_scores": {
        "1": 0.95,
        "2": 0.87,
        "3": 0.0,
        "4": 0.92,
        "...": "...",
        "60": 0.88
      },
      "flagged_questions": [3, 15, 42],
      "processing_metadata": {
        "total_questions_detected": 58,
        "questions_with_multiple_marks": [15],
        "questions_unclear": [42],
        "average_confidence": 0.82,
        "processing_time_ms": 3240,
        "template_detected": true,
        "image_quality_score": 0.85
      }
    },
    "scoring_result": {
      "total_score": 45,
      "max_score": 60,
      "percentage": 75.0,
      "correct_answers": 45,
      "wrong_answers": 13,
      "blank_answers": 2,
      "breakdown_per_question": {
        "1": { "detected": "A", "correct": "A", "is_correct": true },
        "2": { "detected": "B", "correct": "C", "is_correct": false },
        "...": "..."
      }
    },
    "processed_at": "2024-09-21T10:35:30Z"
  }
}
```

**Processing States:**

- `uploaded` - Image uploaded, waiting for processing
- `processing` - Currently being processed
- `completed` - Processing finished successfully
- `failed` - Processing failed due to error

**Error Responses:**

```json
// Image not found
{
    "success": false,
    "error": {
        "code": "SUBMISSION_NOT_FOUND",
        "message": "Image submission not found",
        "submission_id": "123e4567-e89b-12d3-a456-426614174000"
    }
}

// Processing failed
{
    "success": false,
    "error": {
        "code": "PROCESSING_FAILED",
        "message": "Could not detect answer grid in image",
        "details": {
            "error_type": "template_detection_failed",
            "suggestions": [
                "Ensure image has good lighting",
                "Check if template is clearly visible",
                "Try uploading higher resolution image"
            ]
        }
    }
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/process-image/123e4567-e89b-12d3-a456-426614174000" \
     -H "Content-Type: application/json" \
     -d '{
       "answer_key_id": "550e8400-e29b-41d4-a716-446655440000",
       "student_id": "20210001"
     }'
```

#### `GET /api/processing-status/{submission_id}`

Check status dari ongoing processing job.

**Response:**

```json
{
  "success": true,
  "data": {
    "submission_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "processing",
    "progress": {
      "current_step": "bubble_detection",
      "steps_completed": 3,
      "total_steps": 5,
      "percentage": 60,
      "estimated_time_remaining_ms": 1500
    },
    "started_at": "2024-09-21T10:32:00Z"
  }
}
```

---

### **5. Results Management**

#### `GET /api/results/{submission_id}`

Retrieve complete processing results.

**Response:**

```json
{
    "success": true,
    "data": {
        "submission_info": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "student_id": "20210001",
            "filename": "answer_sheet.jpg",
            "upload_timestamp": "2024-09-21T10:30:00Z"
        },
        "exam_info": {
            "exam_name": "Final Exam - Pengolahan Citra",
            "total_questions": 60
        },
        "processing_result": { ... }, // Same as process-image response
        "scoring_result": { ... }     // Same as process-image response
    }
}
```

#### `GET /api/results`

List all processing results with filtering.

**Query Parameters:**

- `student_id` (string): Filter by student ID
- `exam_name` (string): Filter by exam name
- `date_from` (string): ISO date, filter results from this date
- `date_to` (string): ISO date, filter results until this date
- `min_score` (int): Minimum score filter
- `max_score` (int): Maximum score filter
- `limit` (int): Maximum results (default: 10, max: 100)
- `offset` (int): Results to skip (default: 0)

**Response:**

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "submission_id": "123e4567-e89b-12d3-a456-426614174000",
        "student_id": "20210001",
        "exam_name": "Final Exam",
        "score": 45,
        "percentage": 75.0,
        "processed_at": "2024-09-21T10:35:30Z",
        "flagged_questions_count": 3
      }
    ],
    "total": 1,
    "filters_applied": {
      "student_id": null,
      "exam_name": null,
      "date_range": null,
      "score_range": null
    },
    "limit": 10,
    "offset": 0
  }
}
```

---

### **6. Export & Reports**

#### `GET /api/export-csv/{submission_id}`

Export individual result sebagai CSV file.

**Response:**

- **Content-Type:** `text/csv`
- **Headers:** `Content-Disposition: attachment; filename=omr_result_{submission_id}.csv`

**CSV Format:**

```csv
Submission ID,Student ID,Exam Name,Upload Time,Total Score,Percentage,Processing Time (ms),Q1,Q2,Q3,...,Q60,Flagged Questions,Status
123e4567-e89b-12d3-a456-426614174000,20210001,Final Exam,2024-09-21T10:30:00Z,45,75.0,3240,A,B,C,...,E,"3,15,42",Completed
```

#### `GET /api/export-csv-batch`

Export multiple results sebagai CSV file.

**Query Parameters:**

- `submission_ids` (string): Comma-separated list of submission IDs
- `student_ids` (string): Comma-separated list of student IDs
- `exam_name` (string): Filter by exam name
- `date_from` (string): ISO date
- `date_to` (string): ISO date

**Response:**
Same as individual CSV export but with multiple rows.

**Example:**

```bash
curl -X GET "http://localhost:8000/api/export-csv/123e4567-e89b-12d3-a456-426614174000" \
     -o result.csv
```

#### `GET /api/statistics`

Get system-wide statistics dan analytics.

**Response:**

```json
{
  "success": true,
  "data": {
    "overview": {
      "total_submissions": 150,
      "total_exams": 5,
      "average_score": 78.5,
      "processing_success_rate": 94.2
    },
    "performance_metrics": {
      "average_processing_time_ms": 3240,
      "median_processing_time_ms": 2890,
      "fastest_processing_ms": 1200,
      "slowest_processing_ms": 8500
    },
    "accuracy_metrics": {
      "average_confidence_score": 0.85,
      "questions_flagged_percentage": 8.2,
      "template_detection_success_rate": 96.8
    },
    "recent_activity": {
      "submissions_last_24h": 12,
      "submissions_last_7d": 89,
      "active_exams": 2
    }
  }
}
```

---

### **7. System Management**

#### `DELETE /api/submissions/{submission_id}`

Delete submission dan associated data.

**Response:**

```json
{
  "success": true,
  "message": "Submission and all associated data deleted successfully",
  "deleted_items": {
    "submission": true,
    "image_file": true,
    "processing_results": true
  }
}
```

#### `POST /api/cleanup-old-data`

Cleanup old submissions based on retention policy.

**Request Body:**

```json
{
  "older_than_days": 30,
  "dry_run": false
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "submissions_deleted": 45,
    "files_deleted": 45,
    "storage_freed_mb": 1250.5,
    "deleted_before": "2024-08-21T00:00:00Z"
  }
}
```

---

## 🔍 Error Handling

### **Common Error Codes:**

| Code                        | Description                      | HTTP Status |
| --------------------------- | -------------------------------- | ----------- |
| `VALIDATION_ERROR`          | Request validation failed        | 422         |
| `FILE_TOO_LARGE`            | Uploaded file exceeds size limit | 413         |
| `INVALID_FILE_TYPE`         | File type not supported          | 400         |
| `SUBMISSION_NOT_FOUND`      | Submission ID not found          | 404         |
| `ANSWER_KEY_NOT_FOUND`      | Answer key ID not found          | 404         |
| `PROCESSING_FAILED`         | Image processing failed          | 500         |
| `TEMPLATE_DETECTION_FAILED` | Could not detect answer grid     | 422         |
| `DATABASE_ERROR`            | Database operation failed        | 500         |
| `STORAGE_ERROR`             | File storage operation failed    | 500         |

### **Error Response Examples:**

```json
// Validation Error
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Input validation failed",
        "details": {
            "field": "answers",
            "error": "Must contain exactly 60 questions",
            "received": 58
        }
    }
}

// Processing Error
{
    "success": false,
    "error": {
        "code": "TEMPLATE_DETECTION_FAILED",
        "message": "Could not locate answer grid in the image",
        "details": {
            "possible_causes": [
                "Poor image quality",
                "Template not fully visible",
                "Extreme rotation or skew"
            ],
            "suggestions": [
                "Ensure good lighting conditions",
                "Keep template flat and fully visible",
                "Use higher resolution image"
            ]
        }
    }
}
```

---

## 📈 Rate Limiting

### **Current Limits (Academic Prototype):**

- **Upload:** 10 requests per minute per IP
- **Processing:** 5 requests per minute per IP
- **Export:** 20 requests per minute per IP
- **General API:** 100 requests per minute per IP

### **Rate Limit Headers:**

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1695123456
```

---

## 🧪 Testing & Development

### **Development Server:**

```bash
# Start development server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access interactive documentation
open http://localhost:8000/docs
```

### **API Testing Examples:**

```python
# Python example using requests
import requests

# Upload answer key
answer_key = {
    "exam_name": "Test Exam",
    "total_questions": 60,
    "answers": {str(i): ["A", "B", "C", "D", "E"][i % 5] for i in range(1, 61)}
}

response = requests.post(
    "http://localhost:8000/api/upload-answer-key",
    json=answer_key
)
key_id = response.json()["data"]["key_id"]

# Upload image
with open("test_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/upload-image",
        files={"file": f}
    )
submission_id = response.json()["data"]["submission_id"]

# Process image
response = requests.post(
    f"http://localhost:8000/api/process-image/{submission_id}",
    json={"answer_key_id": key_id}
)
result = response.json()["data"]
```

### **JavaScript/TypeScript Example:**

```typescript
// TypeScript example using axios
import axios from "axios";

const API_BASE = "http://localhost:8000";

// Upload and process image
const uploadAndProcess = async (imageFile: File, answerKeyId: string) => {
  // Upload image
  const formData = new FormData();
  formData.append("file", imageFile);

  const uploadResponse = await axios.post(
    `${API_BASE}/api/upload-image`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );

  const submissionId = uploadResponse.data.data.submission_id;

  // Process image
  const processResponse = await axios.post(
    `${API_BASE}/api/process-image/${submissionId}`,
    { answer_key_id: answerKeyId }
  );

  return processResponse.data.data;
};
```

---

## 📱 Integration Examples

### **Frontend Integration (Next.js):**

```typescript
// API client wrapper
class OMRApiClient {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async uploadAnswerKey(answerKey: AnswerKey): Promise<string> {
    const response = await fetch(`${this.baseURL}/api/upload-answer-key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answerKey),
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data.data.key_id;
  }

  async uploadAndProcessImage(
    file: File,
    answerKeyId: string
  ): Promise<ProcessingResult> {
    // Upload image
    const formData = new FormData();
    formData.append("file", file);

    const uploadResponse = await fetch(`${this.baseURL}/api/upload-image`, {
      method: "POST",
      body: formData,
    });

    const uploadData = await uploadResponse.json();
    const submissionId = uploadData.data.submission_id;

    // Process image
    const processResponse = await fetch(
      `${this.baseURL}/api/process-image/${submissionId}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer_key_id: answerKeyId }),
      }
    );

    const processData = await processResponse.json();
    return processData.data;
  }
}
```

---

## 📋 API Changelog

### **Version 1.0.0 (Current)**

- ✅ Initial API implementation
- ✅ Basic CRUD operations for answer keys
- ✅ Image upload and processing
- ✅ CSV export functionality
- ✅ Error handling and validation
- ✅ Comprehensive documentation

### **Future Versions (Planned):**

#### **Version 1.1.0**

- [ ] Batch processing support
- [ ] WebSocket real-time updates
- [ ] Advanced filtering and search
- [ ] PDF export functionality

#### **Version 1.2.0**

- [ ] User authentication and authorization
- [ ] Role-based access control
- [ ] API rate limiting enhancements
- [ ] Advanced analytics endpoints

---

**Document Status:** Complete
**Last Updated:** September 2024
**API Version:** 1.0.0
**Maintainer:** Academic Project Team
