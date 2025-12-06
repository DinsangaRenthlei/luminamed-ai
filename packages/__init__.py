"""Shared type definitions for LuminaMed AI."""
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class Modality(str, Enum):
    """Medical imaging modalities."""
    XRAY = "xray"
    CT = "ct"
    MRI = "mri"
    ULTRASOUND = "ultrasound"
    MAMMO = "mammography"
    UNKNOWN = "unknown"


class AnatomicalRegion(str, Enum):
    """Body regions for radiology."""
    CHEST = "chest"
    ABDOMEN = "abdomen"
    HEAD = "head"
    SPINE = "spine"
    EXTREMITY = "extremity"
    PELVIS = "pelvis"
    UNKNOWN = "unknown"


class Finding(BaseModel):
    """Individual radiology finding."""
    text: str = Field(..., description="Description of the finding")
    location: Optional[str] = Field(None, description="Anatomical location")
    severity: Optional[str] = Field(None, description="Severity assessment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    bbox: Optional[List[float]] = Field(None, description="Bounding box [x, y, w, h]")
    supported_by_image: bool = Field(True, description="Whether finding is grounded in image")


class VerificationResult(BaseModel):
    """Hallucination verification result."""
    is_verified: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    hallucination_score: float = Field(..., ge=0.0, le=1.0)
    unsupported_claims: List[str] = Field(default_factory=list)


class ReportMetadata(BaseModel):
    """Metadata for generated report."""
    study_id: str
    modality: Modality
    anatomical_region: AnatomicalRegion
    model_version: str
    generation_timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: int
    tokens_used: int
    verification_status: Optional[VerificationResult] = None


class RadiologyReport(BaseModel):
    """Complete radiology report structure."""
    clinical_indication: Optional[str] = None
    technique: Optional[str] = None
    findings: List[Finding] = Field(default_factory=list)
    impression: str
    icd_codes: List[str] = Field(default_factory=list)
    cpt_codes: List[str] = Field(default_factory=list)
    metadata: ReportMetadata


class AgentState(BaseModel):
    """State passed between agents in LangGraph."""
    study_id: str
    image_base64: Optional[str] = None
    clinical_hint: Optional[str] = None
    modality: Modality = Modality.UNKNOWN
    anatomical_region: AnatomicalRegion = AnatomicalRegion.UNKNOWN
    
    # Agent outputs
    findings: List[Finding] = Field(default_factory=list)
    impression: Optional[str] = None
    codes: Dict[str, List[str]] = Field(default_factory=dict)
    verification: Optional[VerificationResult] = None
    
    # Metadata
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True