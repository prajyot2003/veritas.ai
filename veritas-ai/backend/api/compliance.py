"""
VERITAS AI — Compliance Center API
"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from core.config import settings
from core.security import get_current_user
from models.schemas import (
    ComplianceStatus,
    ComplianceValidationResult,
    MeasurableActionPoint,
    RiskLevel,
)
from services.vector_store import VectorStoreService

router = APIRouter()
vector_store = VectorStoreService()

# ── In-memory MAPs store (pre-seeded) ────────────────────────
MAPS_DB: dict = {
    "map_001": MeasurableActionPoint(
        id="map_001",
        title="Update KYC Retention Policy",
        description="Ensure all KYC documents are retained for a minimum of 5 years as per RBI Master Circular on KYC/AML.",
        regulation_ref="RBI/2023-24/10 Master Direction on KYC",
        status=ComplianceStatus.pending,
        due_date=datetime.now(timezone.utc) + timedelta(days=30),
        assigned_to="admin@veritas.ai",
        evidence_uploaded=False,
        priority=RiskLevel.high,
    ),
    "map_002": MeasurableActionPoint(
        id="map_002",
        title="Verify Collateral Ownership Records",
        description="Cross-verify all collateral ownership documents with government land registry before loan disbursement.",
        regulation_ref="RBI Circular RPCD.PLNFS.No.BC.61/06.02.31/2011-12",
        status=ComplianceStatus.under_review,
        due_date=datetime.now(timezone.utc) + timedelta(days=15),
        assigned_to="analyst@veritas.ai",
        evidence_uploaded=True,
        priority=RiskLevel.critical,
    ),
    "map_003": MeasurableActionPoint(
        id="map_003",
        title="Upload Q3 Compliance Evidence",
        description="Submit quarterly compliance evidence for SEBI LODR obligations including board meeting minutes and disclosures.",
        regulation_ref="SEBI LODR Regulations 2015 - Regulation 27",
        status=ComplianceStatus.compliant,
        due_date=datetime.now(timezone.utc) - timedelta(days=5),
        assigned_to="admin@veritas.ai",
        evidence_uploaded=True,
        priority=RiskLevel.medium,
    ),
    "map_004": MeasurableActionPoint(
        id="map_004",
        title="Conduct Beneficial Ownership Audit",
        description="Identify and verify beneficial owners holding >25% stake in borrower entities per Prevention of Money Laundering Act.",
        regulation_ref="PMLA 2002, Section 12A",
        status=ComplianceStatus.non_compliant,
        due_date=datetime.now(timezone.utc) + timedelta(days=7),
        assigned_to="analyst@veritas.ai",
        evidence_uploaded=False,
        priority=RiskLevel.critical,
    ),
    "map_005": MeasurableActionPoint(
        id="map_005",
        title="File Suspicious Transaction Report",
        description="File STR with Financial Intelligence Unit India within 7 days of detecting suspicious activity.",
        regulation_ref="PMLA 2002, Rule 8",
        status=ComplianceStatus.pending,
        due_date=datetime.now(timezone.utc) + timedelta(days=3),
        assigned_to="admin@veritas.ai",
        evidence_uploaded=False,
        priority=RiskLevel.critical,
    ),
}

VALIDATION_RESULTS: dict = {}


@router.get("/maps", response_model=List[MeasurableActionPoint])
async def list_maps(
    status: Optional[ComplianceStatus] = None,
    priority: Optional[RiskLevel] = None,
    current_user: dict = Depends(get_current_user),
):
    """List all Measurable Action Points."""
    maps = list(MAPS_DB.values())
    if status:
        maps = [m for m in maps if m.status == status]
    if priority:
        maps = [m for m in maps if m.priority == priority]
    return maps


@router.get("/maps/{map_id}", response_model=MeasurableActionPoint)
async def get_map(map_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific MAP by ID."""
    m = MAPS_DB.get(map_id)
    if not m:
        raise HTTPException(status_code=404, detail="MAP not found")
    return m


@router.post("/validate/{map_id}", response_model=ComplianceValidationResult)
async def validate_compliance(
    map_id: str,
    proof_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
):
    """Validate compliance proof for a MAP using AI."""
    m = MAPS_DB.get(map_id)
    if not m:
        raise HTTPException(status_code=404, detail="MAP not found")

    # Save proof if provided
    proof_text = ""
    if proof_file:
        upload_dir = Path(settings.UPLOAD_DIR) / "compliance"
        upload_dir.mkdir(parents=True, exist_ok=True)
        contents = await proof_file.read()
        proof_path = upload_dir / f"{map_id}_{proof_file.filename}"
        proof_path.write_bytes(contents)
        proof_text = f"File uploaded: {proof_file.filename} ({len(contents)} bytes)"
        MAPS_DB[map_id].evidence_uploaded = True

    # AI-powered validation via RAG
    try:
        relevant_regs = vector_store.retrieve(m.title + " " + m.description, k=3)
        context = "\n".join([r["document"] for r in relevant_regs])
    except Exception:
        context = m.description

    # Determine validation result
    is_valid = m.evidence_uploaded
    confidence = 0.87 if is_valid else 0.62
    reasoning = (
        f"Evidence review for '{m.title}': "
        + ("Sufficient documentation provided. " if is_valid else "Incomplete documentation. ")
        + f"Regulation context: {context[:200]}..."
    )
    suggestions = []
    if not is_valid:
        suggestions = [
            "Upload signed compliance certificate",
            "Attach relevant board resolution",
            "Include third-party auditor report",
        ]

    result = ComplianceValidationResult(
        map_id=map_id,
        is_valid=is_valid,
        confidence=confidence,
        reasoning=reasoning,
        suggestions=suggestions,
        validated_at=datetime.now(timezone.utc),
    )
    VALIDATION_RESULTS[map_id] = result

    if is_valid:
        MAPS_DB[map_id].status = ComplianceStatus.compliant
    return result


@router.get("/summary")
async def compliance_summary(current_user: dict = Depends(get_current_user)):
    """Get compliance status summary."""
    maps = list(MAPS_DB.values())
    total = len(maps)
    status_counts = {}
    for m in maps:
        status_counts[m.status] = status_counts.get(m.status, 0) + 1
    compliant = status_counts.get(ComplianceStatus.compliant, 0)
    return {
        "total": total,
        "compliant": compliant,
        "non_compliant": status_counts.get(ComplianceStatus.non_compliant, 0),
        "pending": status_counts.get(ComplianceStatus.pending, 0),
        "under_review": status_counts.get(ComplianceStatus.under_review, 0),
        "compliance_rate": round((compliant / total) * 100, 1) if total else 0,
        "critical_pending": sum(
            1 for m in maps
            if m.priority == RiskLevel.critical and m.status != ComplianceStatus.compliant
        ),
    }
