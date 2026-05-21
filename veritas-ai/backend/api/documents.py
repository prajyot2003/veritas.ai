"""
VERITAS AI — Document Upload & Management API
"""
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from core.config import settings
from core.security import get_current_user
from models.schemas import DocumentResponse, DocumentStatus

router = APIRouter()

# ── In-memory document store ─────────────────────────────────
DOCUMENTS_DB: dict = {}

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/tiff": ".tiff",
}


def get_documents_db() -> dict:
    return DOCUMENTS_DB


@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload one or more documents (PDF/image)."""
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files per upload")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for file in files:
        # Validate content type
        content_type = file.content_type or ""
        if content_type not in ALLOWED_TYPES and not file.filename.endswith(
            (".pdf", ".png", ".jpg", ".jpeg", ".tiff")
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {content_type}",
            )

        # Validate size
        contents = await file.read()
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {size_mb:.1f}MB (max {settings.MAX_UPLOAD_SIZE_MB}MB)",
            )

        # Save file
        doc_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix.lower() or ".bin"
        safe_filename = f"{doc_id}{ext}"
        file_path = upload_dir / safe_filename

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(contents)

        # Store metadata
        doc = {
            "id": doc_id,
            "filename": file.filename,
            "file_type": content_type,
            "file_size": len(contents),
            "upload_path": str(file_path),
            "uploaded_by": current_user["email"],
            "status": DocumentStatus.pending,
            "created_at": datetime.now(timezone.utc),
            "fraud_score": None,
            "trust_score": None,
            "risk_level": None,
            "extracted_text": None,
            "anomaly_flags": None,
            "metadata": {},
        }
        DOCUMENTS_DB[doc_id] = doc
        results.append(DocumentResponse(**doc))

    return results


@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(
    status_filter: Optional[DocumentStatus] = None,
    current_user: dict = Depends(get_current_user),
):
    """List all documents (optionally filtered by status)."""
    docs = list(DOCUMENTS_DB.values())
    if status_filter:
        docs = [d for d in docs if d["status"] == status_filter]
    docs.sort(key=lambda x: x["created_at"], reverse=True)
    return [DocumentResponse(**d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single document by ID."""
    doc = DOCUMENTS_DB.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse(**doc)


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Download the original document file."""
    doc = DOCUMENTS_DB.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = Path(doc["upload_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(path=str(file_path), filename=doc["filename"])


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a document (admin only)."""
    if current_user["role"] not in ("admin",):
        raise HTTPException(status_code=403, detail="Admin role required")
    doc = DOCUMENTS_DB.pop(doc_id, None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        Path(doc["upload_path"]).unlink(missing_ok=True)
    except Exception:
        pass
    return {"message": "Document deleted"}
