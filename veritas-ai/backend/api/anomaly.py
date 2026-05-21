"""
VERITAS AI — Anomaly Detection API
"""
import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from core.security import get_current_user
from models.schemas import AnomalyResult
from services.anomaly_service import AnomalyDetectionService
from services.ocr_service import OCRService
from api.documents import DOCUMENTS_DB, DocumentStatus

logger = logging.getLogger("veritas.anomaly")
router = APIRouter()

ocr_service = OCRService()
anomaly_service = AnomalyDetectionService()


async def _run_analysis(doc_id: str, file_path: str, filename: str):
    """Background task: run full anomaly pipeline on a document."""
    try:
        DOCUMENTS_DB[doc_id]["status"] = DocumentStatus.processing

        # 1. OCR + text extraction
        extracted = await asyncio.get_event_loop().run_in_executor(
            None, ocr_service.extract, file_path, filename
        )

        # 2. Anomaly detection
        result = await asyncio.get_event_loop().run_in_executor(
            None, anomaly_service.analyze, extracted, doc_id
        )

        # 3. Update document record
        DOCUMENTS_DB[doc_id].update(
            {
                "status": DocumentStatus.flagged if result.fraud_score > 50 else DocumentStatus.analyzed,
                "fraud_score": result.fraud_score,
                "trust_score": result.trust_score,
                "risk_level": result.risk_level,
                "extracted_text": result.extracted_text,
                "anomaly_flags": [f.flag_type for f in result.flags],
                "metadata": result.extracted_metadata,
            }
        )

        # Store full result
        ANOMALY_RESULTS[doc_id] = result

        logger.info(f"Analysis complete for {doc_id}: fraud={result.fraud_score:.1f}")
    except Exception as e:
        logger.error(f"Analysis failed for {doc_id}: {e}", exc_info=True)
        if doc_id in DOCUMENTS_DB:
            DOCUMENTS_DB[doc_id]["status"] = DocumentStatus.pending


# In-memory result store
ANOMALY_RESULTS: dict = {}


@router.post("/analyze/{doc_id}")
async def analyze_document(
    doc_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Trigger anomaly analysis for a document (runs in background)."""
    doc = DOCUMENTS_DB.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc["status"] == DocumentStatus.processing:
        return {"message": "Analysis already in progress", "doc_id": doc_id}

    background_tasks.add_task(
        _run_analysis, doc_id, doc["upload_path"], doc["filename"]
    )
    return {"message": "Analysis started", "doc_id": doc_id}


@router.get("/results/{doc_id}", response_model=AnomalyResult)
async def get_anomaly_result(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get anomaly analysis results for a document."""
    result = ANOMALY_RESULTS.get(doc_id)
    if not result:
        doc = DOCUMENTS_DB.get(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc["status"] == DocumentStatus.processing:
            raise HTTPException(status_code=202, detail="Analysis in progress")
        raise HTTPException(status_code=404, detail="No analysis results yet — trigger /analyze first")
    return result


@router.get("/results")
async def list_anomaly_results(current_user: dict = Depends(get_current_user)):
    """List all anomaly results (summary)."""
    summaries = []
    for doc_id, result in ANOMALY_RESULTS.items():
        summaries.append(
            {
                "document_id": doc_id,
                "fraud_score": result.fraud_score,
                "trust_score": result.trust_score,
                "risk_level": result.risk_level,
                "flag_count": len(result.flags),
                "analyzed_at": result.analyzed_at,
            }
        )
    return summaries
