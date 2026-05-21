"""
VERITAS AI — Pydantic Schemas
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


# ── Enums ─────────────────────────────────────────────────────
class UserRole(str, Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class DocumentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    analyzed = "analyzed"
    flagged = "flagged"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ComplianceStatus(str, Enum):
    pending = "pending"
    compliant = "compliant"
    non_compliant = "non_compliant"
    under_review = "under_review"


# ── Auth ──────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    created_at: str


# ── Documents ─────────────────────────────────────────────────
class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus = DocumentStatus.pending


class DocumentResponse(DocumentBase):
    id: str
    upload_path: str
    uploaded_by: str
    created_at: datetime
    fraud_score: Optional[float] = None
    trust_score: Optional[float] = None
    risk_level: Optional[RiskLevel] = None
    extracted_text: Optional[str] = None
    anomaly_flags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# ── Anomaly ───────────────────────────────────────────────────
class AnomalyFlag(BaseModel):
    flag_type: str
    severity: RiskLevel
    description: str
    confidence: float
    evidence: Optional[str] = None


class AnomalyResult(BaseModel):
    document_id: str
    fraud_score: float = Field(ge=0.0, le=100.0)
    trust_score: float = Field(ge=0.0, le=100.0)
    risk_level: RiskLevel
    flags: List[AnomalyFlag]
    extracted_text: str
    extracted_metadata: Dict[str, Any]
    ai_explanation: str
    analyzed_at: datetime


# ── Compliance ────────────────────────────────────────────────
class MeasurableActionPoint(BaseModel):
    id: str
    title: str
    description: str
    regulation_ref: str
    status: ComplianceStatus
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    evidence_uploaded: bool = False
    priority: RiskLevel


class ComplianceValidationRequest(BaseModel):
    map_id: str
    proof_description: str


class ComplianceValidationResult(BaseModel):
    map_id: str
    is_valid: bool
    confidence: float
    reasoning: str
    suggestions: List[str]
    validated_at: datetime


# ── Graph ─────────────────────────────────────────────────────
class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # borrower, entity, collateral, transaction
    properties: Dict[str, Any] = {}
    risk_score: Optional[float] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: float = 1.0
    properties: Dict[str, Any] = {}


class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = {}


# ── Risk ──────────────────────────────────────────────────────
class UnderwritingDecision(BaseModel):
    document_id: str
    decision: str  # approve / reject / review
    confidence: float
    risk_score: float
    explanation: str
    key_factors: List[str]
    recommendations: List[str]
    generated_at: datetime


class DashboardMetrics(BaseModel):
    total_documents: int
    flagged_documents: int
    average_fraud_score: float
    average_trust_score: float
    compliance_rate: float
    active_maps: int
    critical_alerts: int
    risk_distribution: Dict[str, int]
    recent_alerts: List[Dict[str, Any]]
    trend_data: List[Dict[str, Any]]


# ── Alert ─────────────────────────────────────────────────────
class Alert(BaseModel):
    id: str
    title: str
    description: str
    severity: RiskLevel
    document_id: Optional[str] = None
    created_at: datetime
    is_read: bool = False
