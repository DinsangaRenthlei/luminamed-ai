# LuminaMed AI - API Reference

**Base URL (Development)**: `http://localhost:8000`  
**Base URL (Production)**: `https://luminamed-api.up.railway.app`  
**API Version**: v1  
**Authentication**: None (development) | JWT Bearer Token (production)

---

## 📚 Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [Health & Status](#health--status)
   - [Report Generation](#report-generation)
   - [Report Explanation](#report-explanation)
   - [DICOM Analysis](#dicom-analysis)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

---

## 🔐 Authentication

**Current**: None (open for development)

**Production (Future)**:
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

**Get Token:**
```bash
POST /auth/token
{
  "username": "radiologist@hospital.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

## 📡 Endpoints

### Health & Status

#### GET `/`

Root endpoint with API information.

**Response:**
```json
{
  "name": "LuminaMed-AI",
  "version": "0.1.0",
  "status": "operational",
  "docs": "/docs",
  "health": "/health"
}
```

---

#### GET `/health`

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

**Status Codes:**
- `200 OK` - Service healthy
- `503 Service Unavailable` - Service degraded

---

#### GET `/metrics`

Prometheus metrics endpoint.

**Response:** Text format metrics
```
# HELP luminamed_requests_total Total requests
# TYPE luminamed_requests_total counter
luminamed_requests_total{endpoint="/v1/report",method="POST"} 1234.0

# HELP luminamed_request_latency_seconds Request latency
# TYPE luminamed_request_latency_seconds histogram
luminamed_request_latency_seconds_bucket{endpoint="/v1/report",le="5.0"} 890.0
...
```

---

### Report Generation

#### POST `/v1/report`

Generate radiology report from medical image using multi-agent AI system.

**Request:**
```http
POST /v1/report
Content-Type: multipart/form-data

Form Data:
- image: [file] (required) - Medical image (PNG, JPEG, DICOM)
- clinical_hint: [string] (optional) - Clinical indication
- modality: [string] (optional, default="xray") - Image modality
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/v1/report" \
  -F "image=@chest_xray.jpg" \
  -F "clinical_hint=Patient with persistent cough" \
  -F "modality=xray"
```

**Python Example:**
```python
import requests

with open("chest_xray.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/v1/report",
        files={"image": f},
        data={
            "clinical_hint": "Patient with persistent cough",
            "modality": "xray"
        }
    )

report = response.json()
print(report["impression"])
```

**Response (200 OK):**
```json
{
  "clinical_indication": "Patient with persistent cough",
  "technique": "XRAY examination performed",
  "findings": [
    {
      "text": "Clear lung fields without infiltrates...",
      "location": "chest",
      "severity": "normal",
      "confidence": 0.85,
      "bbox": null,
      "supported_by_image": true
    }
  ],
  "impression": "No acute cardiopulmonary findings...",
  "icd_codes": ["R91.8"],
  "cpt_codes": ["71046"],
  "metadata": {
    "study_id": "study_1764966938927",
    "modality": "xray",
    "anatomical_region": "chest",
    "model_version": "models/gemini-flash-latest",
    "generation_timestamp": "2025-12-05T18:27:04.935011",
    "processing_time_ms": 17234,
    "tokens_used": 2000,
    "verification_status": {
      "is_verified": true,
      "confidence": 0.92,
      "hallucination_score": 0.08,
      "unsupported_claims": []
    }
  }
}
```

**Error Responses:**
```json
// 413 Payload Too Large
{
  "detail": "File too large: 60000000 bytes"
}

// 415 Unsupported Media Type
{
  "detail": "Unsupported content type: image/gif"
}

// 500 Internal Server Error
{
  "detail": "Report generation failed: [error details]"
}
```

**Processing Time:**
- Typical: 15-20 seconds
- Range: 10-30 seconds
- Factors: Image size, model load, agent complexity

---

### Report Explanation

#### POST `/v1/explain`

Translate radiology report to plain language.

**Request:**
```http
POST /v1/explain
Content-Type: application/json

{
  "report_text": "IMPRESSION: No acute findings...",
  "reading_level": "grade8"
}
```

**Parameters:**

| Field | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| report_text | string | Yes | Original radiology report | Any text |
| reading_level | string | No (default: grade8) | Target comprehension level | grade6, grade8, grade12 |

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/v1/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "report_text": "IMPRESSION: No acute cardiopulmonary findings.",
    "reading_level": "grade8"
  }'
```

**Response (200 OK):**
```json
{
  "plain_language": "Good news! Your chest X-ray looks normal...",
  "reading_level": "grade8",
  "key_terms": {
    "consolidation": "An area where the lung is filled with fluid...",
    "infiltrate": "Abnormal substance in the lung...",
    "pneumothorax": "Collapsed lung..."
  },
  "summary": "The report indicates normal results with no acute findings."
}
```

**Processing Time:** 8-12 seconds

---

### DICOM Analysis

#### POST `/v1/analyze-dicom`

Analyze DICOM file with AI and return findings with spatial localization (bounding boxes).

**Request:**
```http
POST /v1/analyze-dicom
Content-Type: multipart/form-data

Form Data:
- dicom_file: [file] (required) - DICOM file
- clinical_hint: [string] (optional) - Clinical indication
```

**Response (200 OK):**
```json
{
  "study_id": "dicom_1765008026484",
  "metadata": {
    "patient_id": "12345",
    "patient_name": "ANONYMOUS",
    "study_date": "20251205",
    "modality": "CT",
    "body_part": "CHEST",
    "image_width": 512,
    "image_height": 512
  },
  "findings": [
    {
      "text": "Lung nodule in right upper lobe...",
      "confidence": 0.87,
      "severity": "moderate",
      "bbox": {
        "x": 25,
        "y": 15,
        "width": 12,
        "height": 10,
        "color": "#FFA500"
      }
    }
  ],
  "impression": "...",
  "image_base64": "iVBORw0KGgo...",
  "processing_time_ms": 18500
}
```

**Bounding Box Format:**
- Coordinates in **percentage** of image dimensions
- `x`, `y`: Top-left corner (%)
- `width`, `height`: Box dimensions (%)
- `color`: Hex color code (severity-based)

---

## 📦 Data Models

### Finding
```typescript
{
  text: string              // Finding description
  location: string | null   // Anatomical location
  severity: string | null   // normal | mild | moderate | severe
  confidence: number        // 0.0 - 1.0
  bbox: BoundingBox | null  // Spatial localization
  supported_by_image: boolean
}
```

### VerificationResult
```typescript
{
  is_verified: boolean
  confidence: number        // 0.0 - 1.0
  hallucination_score: number  // 0.0 - 1.0
  unsupported_claims: string[]
}
```

### RadiologyReport
```typescript
{
  clinical_indication: string | null
  technique: string | null
  findings: Finding[]
  impression: string
  icd_codes: string[]
  cpt_codes: string[]
  metadata: ReportMetadata
}
```

---

## ❌ Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input parameters |
| 413 | Payload Too Large | File > 50MB |
| 415 | Unsupported Media Type | Invalid file format |
| 422 | Validation Error | Pydantic validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Dependencies unavailable |

### Error Response Format
```json
{
  "detail": "Error description with actionable information"
}
```

---

## ⏱️ Rate Limiting

**Current Limits:**
- 10 requests per minute (per IP)
- 20 burst allowance
- Sliding window algorithm

**Headers:**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1638360000
```

**429 Response:**
```json
{
  "detail": "Rate limit exceeded. Retry after 45 seconds."
}
```

---

## 📝 Complete Examples

### Example 1: Generate Report (Python)
```python
import requests
import json

def generate_radiology_report(image_path, clinical_context):
    """Generate radiology report from image."""
    
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/v1/report',
            files={'image': f},
            data={
                'clinical_hint': clinical_context,
                'modality': 'xray'
            },
            timeout=60
        )
    
    if response.status_code == 200:
        report = response.json()
        print(f"Study ID: {report['metadata']['study_id']}")
        print(f"Impression: {report['impression']}")
        print(f"Confidence: {report['metadata']['verification_status']['confidence']:.1%}")
        return report
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Usage
report = generate_radiology_report(
    'chest_xray.jpg',
    'Patient with fever and shortness of breath'
)
```

### Example 2: Explain Report (JavaScript)
```javascript
async function explainReport(reportText, readingLevel = 'grade8') {
  const response = await fetch('http://localhost:8000/v1/explain', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      report_text: reportText,
      reading_level: readingLevel
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();
  
  console.log('Summary:', data.summary);
  console.log('Explanation:', data.plain_language);
  console.log('Key Terms:', data.key_terms);
  
  return data;
}

// Usage
explainReport(
  "IMPRESSION: No acute findings. Lungs are clear.",
  "grade8"
).then(explanation => {
  document.getElementById('output').innerHTML = explanation.plain_language;
});
```

### Example 3: Batch Processing
```python
import asyncio
import aiohttp

async def process_batch(image_paths):
    """Process multiple images concurrently."""
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for image_path in image_paths:
            task = process_single_image(session, image_path)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

async def process_single_image(session, image_path):
    with open(image_path, 'rb') as f:
        data = aiohttp.FormData()
        data.add_field('image', f, filename=image_path)
        data.add_field('modality', 'xray')
        
        async with session.post(
            'http://localhost:8000/v1/report',
            data=data
        ) as response:
            return await response.json()

# Usage
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
reports = asyncio.run(process_batch(image_paths))
```

---

## 🔄 Webhooks (Future)

**Configuration:**
```json
POST /v1/webhooks/configure
{
  "url": "https://your-server.com/webhook",
  "events": ["report.generated", "report.approved"],
  "secret": "your-webhook-secret"
}
```

**Webhook Payload:**
```json
{
  "event": "report.generated",
  "timestamp": "2025-12-06T03:22:36.885643Z",
  "data": {
    "study_id": "study_123",
    "status": "completed",
    "report": { ... }
  }
}
```

---

## 📊 Response Times

| Endpoint | Avg | P50 | P95 | P99 |
|----------|-----|-----|-----|-----|
| `/v1/report` | 17s | 15s | 22s | 28s |
| `/v1/explain` | 10s | 9s | 13s | 16s |
| `/v1/analyze-dicom` | 19s | 17s | 24s | 30s |
| `/health` | 5ms | 3ms | 8ms | 12ms |

---

## 🔍 Interactive API Documentation

**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc (alternative view)

**Features:**
- Try endpoints directly in browser
- Auto-generated from code
- Request/response examples
- Schema definitions

---

## 📞 Support

**Issues**: https://github.com/crillypienaah/luminamed-ai/issues  
**Email**: pienaah.c@northeastern.edu  | ccpienaah@gmail.com
**Slack**: [Community Channel]

---

**Last Updated**: December 6, 2025  
**API Version**: 1.0.0
Save (Ctrl+S)

🎯 PART 6: Create Quick Start Visual Assets
Now let's capture screenshots! We'll take screenshots of:

Radiologist Portal (all 3 tabs)
Patient Portal (before/after explanation)
AI Overlay Viewer
Swagger API docs
Analytics charts

But first - let me create one more quick file: CONTRIBUTING.md
Create: docs/CONTRIBUTING.md
markdown# Contributing to LuminaMed AI

Thank you for your interest in contributing to LuminaMed AI!

## 🚀 Quick Start

1. Fork the repository
2. Clone your fork
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Run tests: `pytest`
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Development Setup

See [README.md](../README.md#installation) for installation instructions.

## 🧪 Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=services

# Run specific test
pytest tests/unit/test_report.py::test_generate_report -v
```

## 📝 Code Style

- **Python**: Black formatter, Ruff linter
- **TypeScript**: ESLint, Prettier
- **Line length**: 100 characters
- **Docstrings**: Required for all public functions

## 🎯 Pull Request Guidelines

- Clear description of changes
- Tests for new features
- Documentation updates
- No breaking changes without discussion

## 📧 Questions?

Open an issue or email: pienaah.c@northeastern.edu | ccpienaah@gmail.com