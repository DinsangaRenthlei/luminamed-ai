"""LuminaMed AI - FastAPI Application."""
import time
import base64
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

from apps.api.app.config import get_settings
from packages.types import (
    RadiologyReport, ReportMetadata, Finding,
    Modality, AnatomicalRegion, VerificationResult
)
from services.inference.agent_graph import get_report_graph
from pydantic import BaseModel

class ExplainRequest(BaseModel):
    """Request to explain a report."""
    report_text: str
    reading_level: str = "grade8"  # grade6, grade8, grade12


class ExplainResponse(BaseModel):
    """Plain language explanation."""
    plain_language: str
    reading_level: str
    key_terms: dict[str, str]
    summary: str

# Setup structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

settings = get_settings()

# Prometheus metrics
REQUESTS = Counter('luminamed_requests_total', 'Total requests', ['endpoint', 'method'])
LATENCY = Histogram('luminamed_request_latency_seconds', 'Request latency', ['endpoint'])
ERRORS = Counter('luminamed_errors_total', 'Total errors', ['endpoint', 'error_type'])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    log.info("Starting LuminaMed AI", version=settings.app_version)
    
    # Initialize services
    _ = get_report_graph()  # Warm up graph compilation
    
    log.info("LuminaMed AI ready")
    yield
    
    log.info("Shutting down LuminaMed AI")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent radiology report generation with verifiable AI",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    REQUESTS.labels(endpoint="/health", method="GET").inc()
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/report", response_model=RadiologyReport)
async def generate_report(
    image: UploadFile = File(..., description="Medical image (PNG/JPEG/DICOM)"),
    clinical_hint: str = Form("", description="Optional clinical context"),
    modality: str = Form("xray", description="Image modality"),
):
    """Generate radiology report using multi-agent system."""
    start_time = time.perf_counter()
    REQUESTS.labels(endpoint="/v1/report", method="POST").inc()
    
    try:
        # Validate content type
        if image.content_type not in settings.allowed_content_types_list:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported content type: {image.content_type}"
            )
        
        # Read and validate size
        image_data = await image.read()
        if len(image_data) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {len(image_data)} bytes"
            )
        
        # Encode for multimodal
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Generate unique study ID
        study_id = f"study_{int(time.time() * 1000)}"
        
        log.info("Generating report", study_id=study_id, modality=modality)
        
        # Execute agent graph
        graph = get_report_graph()
        initial_state = {
            "messages": [],
            "study_id": study_id,
            "image_base64": image_base64,
            "clinical_hint": clinical_hint or "No clinical context provided",
            "modality": modality,
            "findings": [],
            "impression": "",
            "codes": {},
            "verification": {}
        }
        
        result = graph.invoke(initial_state)
        
        # Build structured report
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        findings = [
            Finding(
                text=f['text'],
                location=f.get('location'),
                severity=f.get('severity'),
                confidence=f['confidence'],
                supported_by_image=True
            )
            for f in result['findings']
        ]
        
        verification = (
            VerificationResult(**result['verification']) 
            if result.get('verification') 
            else None
        )
        
        metadata = ReportMetadata(
            study_id=study_id,
            modality=Modality(modality),
            anatomical_region=AnatomicalRegion.CHEST,
            model_version=settings.model_name,
            processing_time_ms=processing_time_ms,
            tokens_used=2000,
            verification_status=verification
        )
        
        report = RadiologyReport(
            clinical_indication=clinical_hint if clinical_hint else None,
            technique=f"{modality.upper()} examination performed",
            findings=findings,
            impression=result['impression'],
            icd_codes=result['codes'].get('icd_codes', []),
            cpt_codes=result['codes'].get('cpt_codes', []),
            metadata=metadata
        )
        
        LATENCY.labels(endpoint="/v1/report").observe(processing_time_ms / 1000)
        
        log.info(
            "Report generated successfully",
            study_id=study_id,
            processing_time_ms=processing_time_ms,
            verification_passed=verification.is_verified if verification else None
        )
        
        return report
        
    except Exception as e:
        ERRORS.labels(endpoint="/v1/report", error_type=type(e).__name__).inc()
        log.error("Report generation failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
@app.post("/v1/explain", response_model=ExplainResponse)
async def explain_report(request: ExplainRequest):
    """Explain radiology report in plain language."""
    REQUESTS.labels(endpoint="/v1/explain", method="POST").inc()
    start_time = time.perf_counter()
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        
        llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            temperature=0.3,
            google_api_key=settings.google_api_key
        )
        
        # Reading level prompts
        level_prompts = {
            "grade6": "Explain like I'm 12 years old. Use very simple words. No medical jargon.",
            "grade8": "Explain in simple terms that a middle school student can understand. Define medical terms clearly.",
            "grade12": "Explain clearly but you can use some medical terminology with definitions."
        }
        
        prompt = f"""{level_prompts.get(request.reading_level, level_prompts['grade8'])}

Original Radiology Report:
{request.report_text}

Task:
1. Explain what the report means in plain language
2. Focus on what the patient needs to know
3. Explain any concerning findings clearly
4. Provide reassurance where appropriate
5. Explain next steps if mentioned

Be clear, compassionate, and accurate. Don't add medical advice beyond what's in the report."""

        response = llm.invoke([HumanMessage(content=prompt)])
        plain_text = response.content
        
        # Common radiology terms glossary
        key_terms = {
            "consolidation": "An area where the lung is filled with fluid or infection instead of air",
            "infiltrate": "Abnormal substance in the lung, often infection or inflammation",
            "pneumothorax": "Collapsed lung - air has leaked into the space around the lung",
            "pleural effusion": "Fluid buildup around the lung",
            "cardiomegaly": "Enlarged heart",
            "atelectasis": "Part of the lung has collapsed or isn't inflating properly",
            "costophrenic angle": "The corner where your diaphragm meets your chest wall",
            "cardiac silhouette": "The outline of your heart on the X-ray"
        }
        
        # Generate brief summary
        summary_prompt = f"In 1-2 sentences, what is the main takeaway from this report?\n\n{request.report_text}"
        summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
        
        processing_time = time.perf_counter() - start_time
        LATENCY.labels(endpoint="/v1/explain").observe(processing_time)
        
        log.info("Explanation generated", reading_level=request.reading_level, time_ms=int(processing_time*1000))
        
        return ExplainResponse(
            plain_language=plain_text,
            reading_level=request.reading_level,
            key_terms=key_terms,
            summary=summary_response.content
        )
        
    except Exception as e:
        ERRORS.labels(endpoint="/v1/explain", error_type=type(e).__name__).inc()
        log.error("Explanation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.post("/v1/analyze-dicom")
async def analyze_dicom(
    dicom_file: UploadFile = File(..., description="DICOM file"),
    clinical_hint: str = Form("", description="Clinical context"),
):
    """Analyze DICOM file and return findings with bounding boxes."""
    start_time = time.perf_counter()
    REQUESTS.labels(endpoint="/v1/analyze-dicom", method="POST").inc()
    
    try:
        from services.dicom.dicom_utils import dicom_to_png, extract_dicom_metadata
        
        # Read DICOM
        dicom_bytes = await dicom_file.read()
        
        log.info("Processing DICOM file", filename=dicom_file.filename)
        
        # Extract metadata
        metadata = extract_dicom_metadata(dicom_bytes)
        
        # Convert to PNG for AI processing
        png_bytes, _ = dicom_to_png(dicom_bytes)
        image_base64 = base64.b64encode(png_bytes).decode('utf-8')
        
        # Generate report using existing agent system
        study_id = f"dicom_{int(time.time() * 1000)}"
        
        graph = get_report_graph()
        initial_state = {
            "messages": [],
            "study_id": study_id,
            "image_base64": image_base64,
            "clinical_hint": clinical_hint or "DICOM image analysis",
            "modality": metadata.get('modality', 'xray').lower(),
            "findings": [],
            "impression": "",
            "codes": {},
            "verification": {}
        }
        
        result = graph.invoke(initial_state)
        
        # Generate mock bounding boxes for findings
        findings_with_boxes = []
        for idx, finding in enumerate(result['findings']):
            bbox = {
                "x": 10 + (idx * 15),
                "y": 10 + (idx * 10),
                "width": 20,
                "height": 15,
                "color": "#FF0000" if finding.get('severity') != 'normal' else "#00FF00"
            }
            
            findings_with_boxes.append({
                "text": finding['text'],
                "confidence": finding['confidence'],
                "severity": finding.get('severity', 'normal'),
                "bbox": bbox
            })
        
        processing_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        log.info("DICOM analysis complete", study_id=study_id, time_ms=processing_time_ms)
        
        return {
            "study_id": study_id,
            "metadata": metadata,
            "findings": findings_with_boxes,
            "impression": result['impression'],
            "image_base64": image_base64,
            "image_width": metadata['image_width'],
            "image_height": metadata['image_height'],
            "processing_time_ms": processing_time_ms
        }
        
    except Exception as e:
        ERRORS.labels(endpoint="/v1/analyze-dicom", error_type=type(e).__name__).inc()
        log.error("DICOM analysis failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"DICOM analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.api.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )