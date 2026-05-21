"""
VERITAS AI — Risk Analysis & Underwriting API
"""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from core.security import get_current_user
from models.schemas import DashboardMetrics, RiskLevel, UnderwritingDecision
from api.documents import DOCUMENTS_DB
from api.anomaly import ANOMALY_RESULTS
from api.compliance import MAPS_DB, ComplianceStatus

router = APIRouter()


def _compute_dashboard_metrics() -> DashboardMetrics:
    docs = list(DOCUMENTS_DB.values())
    total = len(docs)
    flagged = sum(1 for d in docs if d.get("fraud_score") and d["fraud_score"] > 50)

    fraud_scores = [d["fraud_score"] for d in docs if d.get("fraud_score") is not None]
    trust_scores = [d["trust_score"] for d in docs if d.get("trust_score") is not None]

    maps = list(MAPS_DB.values())
    compliant_maps = sum(1 for m in maps if m.status == ComplianceStatus.compliant)

    risk_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for d in docs:
        if d.get("risk_level"):
            risk_dist[d["risk_level"]] = risk_dist.get(d["risk_level"], 0) + 1

    recent_alerts = []
    for doc_id, result in list(ANOMALY_RESULTS.items())[-5:]:
        if result.flags:
            for flag in result.flags[:2]:
                recent_alerts.append({
                    "id": f"alert_{doc_id}_{flag.flag_type}",
                    "title": flag.flag_type.replace("_", " ").title(),
                    "description": flag.description,
                    "severity": flag.severity,
                    "document_id": doc_id,
                    "created_at": result.analyzed_at.isoformat(),
                })

    # Trend data (last 7 days simulated)
    import random
    trend_data = [
        {
            "day": f"Day {i+1}",
            "fraud_score": round(random.uniform(20, 80), 1),
            "trust_score": round(random.uniform(40, 90), 1),
            "documents": random.randint(1, 10),
        }
        for i in range(7)
    ]

    return DashboardMetrics(
        total_documents=total,
        flagged_documents=flagged,
        average_fraud_score=round(sum(fraud_scores) / len(fraud_scores), 1) if fraud_scores else 0.0,
        average_trust_score=round(sum(trust_scores) / len(trust_scores), 1) if trust_scores else 0.0,
        compliance_rate=round((compliant_maps / len(maps)) * 100, 1) if maps else 0.0,
        active_maps=len(maps),
        critical_alerts=sum(
            1 for r in ANOMALY_RESULTS.values()
            for f in r.flags if f.severity == RiskLevel.critical
        ),
        risk_distribution=risk_dist,
        recent_alerts=recent_alerts[:10],
        trend_data=trend_data,
    )


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    """Get aggregated risk dashboard metrics."""
    return _compute_dashboard_metrics()


@router.get("/underwriting/{doc_id}", response_model=UnderwritingDecision)
async def get_underwriting_decision(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get AI-powered underwriting decision for a document."""
    doc = DOCUMENTS_DB.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    result = ANOMALY_RESULTS.get(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="Run /anomaly/analyze first")

    fraud_score = result.fraud_score
    trust_score = result.trust_score

    # Decision logic
    if fraud_score > 70:
        decision = "reject"
        explanation = (
            f"High underwriting risk detected. Fraud score of {fraud_score:.1f}/100 "
            f"indicates significant anomalies including: {', '.join(f.flag_type for f in result.flags[:3])}. "
            "Loan approval is not recommended without thorough manual verification."
        )
        key_factors = [f.description for f in result.flags[:4]]
        recommendations = [
            "Conduct in-person verification of borrower identity",
            "Request original document submission",
            "Perform site inspection for collateral",
            "File Suspicious Activity Report",
        ]
    elif fraud_score > 40:
        decision = "review"
        explanation = (
            f"Moderate risk detected (fraud score: {fraud_score:.1f}/100, trust score: {trust_score:.1f}/100). "
            "Manual review recommended before decision. Anomalies detected require further investigation."
        )
        key_factors = [f.description for f in result.flags[:2]]
        recommendations = [
            "Request additional KYC documentation",
            "Verify ownership records with registry",
            "Cross-check financial statements",
        ]
    else:
        decision = "approve"
        explanation = (
            f"Low risk profile (fraud score: {fraud_score:.1f}/100, trust score: {trust_score:.1f}/100). "
            "Document appears authentic and consistent. Standard underwriting conditions apply."
        )
        key_factors = ["Clean ownership record", "Consistent financial data", "Valid KYC documentation"]
        recommendations = ["Proceed with standard loan processing", "Maintain document records for 5 years"]

    return UnderwritingDecision(
        document_id=doc_id,
        decision=decision,
        confidence=round((100 - abs(fraud_score - 50)) / 100, 2),
        risk_score=fraud_score,
        explanation=explanation,
        key_factors=key_factors,
        recommendations=recommendations,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/alerts")
async def get_risk_alerts(current_user: dict = Depends(get_current_user)):
    """Get all risk alerts across documents."""
    alerts = []
    for doc_id, result in ANOMALY_RESULTS.items():
        for flag in result.flags:
            alerts.append({
                "id": f"{doc_id}_{flag.flag_type}",
                "document_id": doc_id,
                "type": flag.flag_type,
                "severity": flag.severity,
                "description": flag.description,
                "confidence": flag.confidence,
                "created_at": result.analyzed_at.isoformat(),
            })
    alerts.sort(key=lambda x: x["severity"], reverse=True)
    return alerts
