"""
VERITAS AI — OCR & Document Extraction Service
"""
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("veritas.ocr")


class ExtractedDocument:
    def __init__(self, text: str, metadata: Dict[str, Any], filename: str):
        self.text = text
        self.metadata = metadata
        self.filename = filename


class OCRService:
    def __init__(self):
        self._tesseract_available = self._check_tesseract()
        self._pdfplumber_available = self._check_pdfplumber()

    def _check_tesseract(self) -> bool:
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR available ✓")
            return True
        except Exception:
            logger.warning("Tesseract not available — will use text extraction fallback")
            return False

    def _check_pdfplumber(self) -> bool:
        try:
            import pdfplumber
            return True
        except ImportError:
            return False

    def extract(self, file_path: str, filename: str) -> ExtractedDocument:
        """Main extraction entry point — routes to appropriate extractor."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            text, meta = self._extract_pdf(file_path)
        elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
            text, meta = self._extract_image(file_path)
        else:
            text, meta = self._extract_text_fallback(file_path)

        # Enrich metadata
        meta.update(self._extract_entities(text))
        meta["filename"] = filename
        meta["file_size"] = os.path.getsize(file_path)
        meta["char_count"] = len(text)

        logger.info(f"Extracted {len(text)} chars from {filename}")
        return ExtractedDocument(text=text, metadata=meta, filename=filename)

    def _extract_pdf(self, file_path: str):
        """Extract text from PDF using pdfplumber."""
        text_parts = []
        meta = {"pages": 0, "file_type": "pdf"}

        if self._pdfplumber_available:
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    meta["pages"] = len(pdf.pages)
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ""
                        text_parts.append(page_text)

                        # Extract tables
                        tables = page.extract_tables()
                        for table in tables:
                            for row in table:
                                if row:
                                    text_parts.append(" | ".join(str(c) for c in row if c))

                    # PDF metadata
                    if pdf.metadata:
                        meta["pdf_author"] = pdf.metadata.get("Author", "")
                        meta["pdf_creator"] = pdf.metadata.get("Creator", "")
                        meta["pdf_created"] = pdf.metadata.get("CreationDate", "")
                        meta["pdf_modified"] = pdf.metadata.get("ModDate", "")

                text = "\n".join(text_parts)
                if text.strip():
                    return text, meta
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}")

        # Fallback: OCR on PDF pages
        if self._tesseract_available:
            return self._ocr_pdf_pages(file_path, meta)

        return self._extract_text_fallback(file_path)

    def _ocr_pdf_pages(self, file_path: str, meta: dict):
        """Convert PDF pages to images and OCR them."""
        try:
            from pdf2image import convert_from_path
            import pytesseract
            images = convert_from_path(file_path, dpi=200)
            meta["pages"] = len(images)
            texts = []
            for img in images:
                t = pytesseract.image_to_string(img, lang="eng")
                texts.append(t)
            return "\n".join(texts), meta
        except Exception as e:
            logger.warning(f"PDF OCR failed: {e}")
            return f"[PDF: {Path(file_path).name} — OCR unavailable]", meta

    def _extract_image(self, file_path: str):
        """Extract text from image using Tesseract OCR."""
        meta = {"file_type": "image", "pages": 1}

        if self._tesseract_available:
            try:
                import pytesseract
                from PIL import Image
                import cv2
                import numpy as np

                # Pre-process image for better OCR
                img = cv2.imread(file_path)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    # Adaptive thresholding
                    thresh = cv2.adaptiveThreshold(
                        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY, 11, 2
                    )
                    # Denoise
                    denoised = cv2.fastNlMeansDenoising(thresh)
                    pil_img = Image.fromarray(denoised)

                    # Detect signatures (high-contrast regions)
                    meta["has_signature_region"] = self._detect_signature_region(img)
                    meta["image_width"] = img.shape[1]
                    meta["image_height"] = img.shape[0]
                else:
                    pil_img = Image.open(file_path)

                text = pytesseract.image_to_string(pil_img, lang="eng", config="--oem 3 --psm 6")
                return text, meta
            except Exception as e:
                logger.warning(f"Image OCR failed: {e}")

        return f"[Image: {Path(file_path).name} — OCR unavailable]", meta

    def _detect_signature_region(self, img) -> bool:
        """Detect if image contains a signature-like region."""
        try:
            import cv2
            import numpy as np
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            long_thin = [c for c in contours if cv2.arcLength(c, False) > 50]
            return len(long_thin) > 5
        except Exception:
            return False

    def _extract_text_fallback(self, file_path: str):
        """Fallback: try to read as plain text."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(), {"file_type": "text"}
        except Exception:
            return "[Unable to extract text]", {"file_type": "unknown"}

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract structured entities from raw text."""
        entities: Dict[str, Any] = {}

        # Dates
        date_pattern = r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b"
        entities["dates"] = re.findall(date_pattern, text)

        # Financial amounts
        amount_pattern = r"(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?"
        entities["financial_amounts"] = re.findall(amount_pattern, text, re.IGNORECASE)

        # PAN numbers
        pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
        entities["pan_numbers"] = re.findall(pan_pattern, text)

        # Aadhaar (masked)
        aadhaar_pattern = r"\bXXXX\s*XXXX\s*\d{4}\b|\b\d{4}\s*\d{4}\s*\d{4}\b"
        entities["aadhaar_refs"] = re.findall(aadhaar_pattern, text)

        # Account numbers
        acct_pattern = r"\b\d{9,18}\b"
        entities["account_numbers"] = re.findall(acct_pattern, text)[:5]

        # Names (simple heuristic)
        name_pattern = r"(?:Name|Borrower|Owner|Applicant)\s*:\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})"
        entities["names"] = re.findall(name_pattern, text)

        # Ownership keywords
        entities["ownership_keywords"] = [
            w for w in ["owner", "registered", "transfer", "sale deed", "mortgage", "collateral"]
            if w.lower() in text.lower()
        ]

        return {"entities": entities}
