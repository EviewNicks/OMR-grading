# Sistem Penilaian Otomatis Ujian Pilihan Ganda Menggunakan Pengolahan Citra Digital

**Tugas Akhir Mata Kuliah Pengolahan Citra Digital**
*Simple OMR (Optical Mark Recognition) System untuk TOEFL-style Answer Sheets*

## 1. Latar Belakang & Permasalahan

Penilaian manual lembar jawaban pilihan ganda membutuhkan waktu yang lama dan rentan terhadap kesalahan manusia. Untuk mengatasi masalah ini, dikembangkan sistem otomatis berbasis pengolahan citra digital yang dapat membaca lembar jawaban TOEFL-style dari foto/scan.

**Scope Akademik:** Project ini dirancang sebagai tugas akhir dengan prinsip "Keep It Simple" - fokus pada implementasi teknis pengolahan citra yang solid tanpa kompleksitas production-grade system.

## 2. Tujuan Proyek

Membangun sistem sederhana berbasis pengolahan citra digital yang dapat:

- **Memproses foto lembar jawaban** TOEFL-style dengan 60 soal (A-E)
- **Mendeteksi bubble yang terisi** menggunakan teknik basic image processing (OpenCV)
- **Mencocokkan dengan kunci jawaban** dan menghitung skor otomatis
- **Menghasilkan laporan hasil** dalam format CSV untuk analisis

## 3. Ruang Lingkup & Batasan

### ✅ **Yang Akan Dikembangkan:**
- Sistem untuk lembar jawaban pilihan ganda TOEFL-style (A, B, C, D, E)
- Web interface sederhana untuk upload gambar dan input kunci jawaban
- Basic image processing pipeline menggunakan OpenCV
- Database storage untuk menyimpan hasil dan kunci jawaban
- Export hasil dalam format CSV

### ❌ **Batasan & Yang Tidak Dikembangkan:**
- Tidak menggunakan advanced computer vision atau machine learning
- Tidak ada real-time processing atau batch processing besar
- Tidak ada integrasi dengan LMS atau sistem akademik lain
- Tidak ada multi-user authentication atau authorization
- Fokus pada 1 format template (dapat dikembangkan kemudian)

## 4. Dataset & Sumber Data

### **Dataset Utama:**
[Kaggle OMR Dataset](https://www.kaggle.com/datasets/collinslemeke/omr-dataset)
- Berisi gambar lembar jawaban OMR dengan berbagai kondisi
- Format TOEFL-style dengan bubble A-E
- Variasi kualitas foto dan kondisi pencahayaan

### **Data Tambahan:**
- Sample template lembar jawaban dari contoh yang disediakan
- Test images dengan berbagai kondisi (lighting, angle, quality)
- Synthetic data untuk testing edge cases

### **Target Metrics (Realistis untuk Academic Project):**
- **Bubble Detection Accuracy:** 80-90% pada kondisi normal
- **Processing Time:** 2-5 detik per lembar (acceptable untuk demo)
- **Template Recognition:** 85%+ success rate
- **Overall System Accuracy:** 75-85% (sufficient untuk proof of concept)

## 5. Pendekatan Teknis

### **Core Approach - Simple Image Processing:**
- **Basic OpenCV Pipeline:** Grayscale → Blur → Threshold → Contour Detection
- **Template Matching:** Deteksi grid jawaban menggunakan pattern recognition
- **Bubble Detection:** Pixel counting untuk menentukan bubble yang terisi
- **Rule-based Classification:** Threshold-based decision untuk filled vs empty

### **Key Features:**
- **Upload Interface:** Web-based upload untuk lembar jawaban dan kunci
- **Image Preprocessing:** Basic correction untuk brightness dan contrast
- **Result Visualization:** Preview hasil deteksi dengan overlay
- **Manual Override:** Interface untuk koreksi manual jika diperlukan
- **Export Functionality:** CSV export untuk analisis hasil

## 6. Tech Stack & Spesifikasi Teknis

### **Technology Stack:**
```yaml
Backend: FastAPI (Python)
Frontend: Next.js (React)
Database: Supabase PostgreSQL
Storage: Supabase Storage
Queue: Redis (untuk async processing)
Image Processing: OpenCV (cv2)
Deployment: Vercel (frontend) + Railway (backend)
```

### **Spesifikasi Sistem:**
- **Format Lembar:** 60 soal, pilihan A-E (sesuai template TOEFL)
- **Input:** Upload foto/scan lembar jawaban (JPG, PNG)
- **Penilaian:** +1 benar, 0 salah/kosong (tanpa penalti)
- **Output:** Skor total, breakdown per soal, export CSV
- **Error Handling:** Multiple marks flagged untuk review manual

### **Asumsi & Constraints:**
- Template format konsisten (grid 3x20)
- Foto dengan kualitas minimal (resolusi >800px)
- Orientasi foto relatif lurus (toleransi ±10°)
- Processing per-image (tidak batch processing)

## 7. Aplikasi Web - Fitur & Interface

### **Core Features (MVP):**

#### **1. Input Management**
- **Upload Kunci Jawaban:** Form input 60 soal (A-E) atau upload CSV
- **Upload Lembar Jawaban:** Drag & drop interface untuk foto (single upload)
- **Template Preview:** Tampilan contoh template untuk reference

#### **2. Processing & Analysis**
- **Image Processing:** Real-time preview hasil deteksi bubble
- **Answer Extraction:** Grid overlay menunjukkan jawaban yang terdeteksi
- **Scoring:** Automatic calculation dengan breakdown per soal
- **Error Handling:** Flag untuk multiple marks atau undetected bubbles

#### **3. Results & Export**
- **Score Display:** Total score, percentage, dan detail per soal
- **Visual Feedback:** Color-coded right/wrong answers
- **CSV Export:** Student ID, answers per question, total score
- **Processing History:** Simple list dari previous uploads

### **UI Components:**
- Simple, clean interface menggunakan Next.js components
- Responsive design untuk desktop usage
- Progress indicators untuk image processing
- Error messages dan success notifications

## 8. Arsitektur & Pipeline

### **System Architecture:**
```
[NextJS Frontend] ←→ [FastAPI Backend] ←→ [Supabase DB]
                           ↓
                    [OpenCV Processing]
                           ↓
                      [Redis Queue]
```

### **Image Processing Pipeline:**
```python
1. Image Upload → FastAPI endpoint
2. Preprocessing → Grayscale + Gaussian Blur + Threshold
3. Template Detection → Find answer grid using contour detection
4. Bubble Extraction → Extract 60 bubble regions (3x20 grid)
5. Fill Detection → Count black pixels per bubble
6. Answer Classification → Determine filled bubble per question
7. Scoring → Compare with answer key
8. Results Storage → Save to Supabase + return JSON response
```

### **Data Flow:**
- **Input:** Image file + Answer key
- **Processing:** OpenCV analysis → Answer extraction
- **Storage:** Results in PostgreSQL, Images in Supabase Storage
- **Output:** Score + CSV export + Visual feedback

## 9. Skema Klasifikasi (Simple Rules-Based)

### **Bubble Classification:**
- **Binary Classification:** Filled vs Not Filled (simple pixel counting)
- **Threshold:** Dynamic threshold berdasarkan contrast analysis
- **Confidence:** Basic confidence score based on pixel density

### **Answer Logic:**
```python
for each question (1-60):
    if exactly_one_bubble_filled:
        answer = bubble_letter  # A, B, C, D, or E
    elif multiple_bubbles_filled:
        answer = "INVALID" + flag_for_manual_review
    else:
        answer = "BLANK"
```

## 10. Timeline Pengembangan (8 Minggu)

### **Phase 1: Foundation (Minggu 1-3)**
- **Minggu 1:** Setup environment, explore Kaggle dataset, basic OpenCV experiments
- **Minggu 2:** Develop image preprocessing pipeline, template detection prototype
- **Minggu 3:** Implement bubble detection and basic fill classification

### **Phase 2: Integration (Minggu 4-6)**
- **Minggu 4:** Build FastAPI backend with image processing endpoints
- **Minggu 5:** Develop Next.js frontend with upload and results interface
- **Minggu 6:** Integrate frontend-backend, implement database storage

### **Phase 3: Testing & Documentation (Minggu 7-8)**
- **Minggu 7:** End-to-end testing, debugging, performance optimization
- **Minggu 8:** Academic documentation, demo preparation, final presentation

### **Deliverables per Week:**
```
Week 1: Development environment + dataset analysis
Week 2: Working image processing prototype
Week 3: Bubble detection with accuracy metrics
Week 4: Backend API with image processing endpoints
Week 5: Frontend interface with basic functionality
Week 6: Full-stack integration with database
Week 7: Complete system testing and bug fixes
Week 8: Academic report + demo video + presentation
```

## 11. Academic Requirements & Success Criteria

### **Academic Deliverables:**
- **Source Code:** Well-documented Python (FastAPI) + JavaScript (Next.js)
- **Technical Report:** Methodology, implementation, results analysis (Bahasa Indonesia)
- **Demo Video:** 5-10 minutes showing complete workflow
- **Live Demo:** Working prototype demonstration to instructors
- **User Manual:** Setup and usage instructions

### **Success Metrics for Academic Assessment:**
- **Functionality:** Working end-to-end system (40%)
- **Technical Implementation:** Clean code with proper image processing (30%)
- **Documentation:** Comprehensive technical report and code comments (20%)
- **Innovation:** Problem-solving approach and creativity (10%)

### **Technical Notes & Best Practices:**
- **Code Quality:** Use proper error handling and logging
- **Documentation:** Comment all image processing functions in Indonesian
- **Testing:** Include test cases with sample images
- **Version Control:** Regular Git commits with descriptive messages
- **Academic Integrity:** Original implementation with proper citations

### **Deployment Strategy (Optional for Extra Credit):**
- **Free Hosting:** Vercel (frontend) + Railway (backend)
- **Database:** Supabase free tier
- **Domain:** Free .vercel.app subdomain
- **Total Cost:** $0 (perfect for student project)

---

**Project Contact:** [Your Name] - [NPM] - Pengolahan Citra Digital
**Last Updated:** [Current Date]
**Repository:** [GitHub URL when available]
