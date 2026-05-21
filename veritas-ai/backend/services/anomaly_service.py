"""
VERITAS AI — Anomaly Detection Service
Uses IsolationForest + XGBoost + heuristic checks
"""
import hashlib
import logging
import os
import re
from datetime import datetime, timezone
from typing import List

import numpy as np

from models.schemas import AnomalyFlag, AnomalyResult, RiskLevel
from services.ocr_service import ExtractedDocument

logger = logging.getLogger("veritas.anomaly")


class AnomalyDetectionService:
    def __init__(self):
        self._iso_forest = None
        self._xgb_model = None
        self._init_models()

    def _init_models(self):
        """Initialize ML models (lazy load)."""
        try:
            from sklearn.ensemble import IsolationForest
            self._iso_forest = IsolationForest(
                n_estimators=100, contamination=0.15, random_state=42
            )
            # Fit on synthetic baseline data
            baseline = np.random.randn(200, 8) * 0.5
            self._iso_forest.fit(baseline)
            logger.info("IsolationForest initialized ✓")
        except Exception as e:
            logger.warning(f"IsolationForest init failed: {e}")

        try:
            import xgboost as xgb
            # Create a simple XGBoost classifier with synthetic training
            X = np.random.randn(500, 8)
            y = (X[:, 0] + X[:, 2] > 1.5).astype(int)
            self._xgb_model = xgb.XGBClassifier(
                n_estimators=50, max_depth=4, random_state=42, eval_metric="logloss"
            )
            self._xgb_model.fit(X, y, verbose=False)
            logger.info("XGBoost classifier initialized ✓")
        except Exception as e:
            logger.warning(f"XGBoost init failed: {e}")

    def analyze(self, doc: ExtractedDocument, doc_id: str) -> AnomalyResult:
        """Full anomaly analysis pipeline."""
        flags: List[AnomalyFlag] = []
        text = doc.text
        meta = doc.metadata
        entities = meta.get("entities", {})

        # ── 1. Text-based Heuristics ────────────────────────────
        flags.extend(self._check_text_anomalies(text, entities))

        # ── 2. Metadata Tampering ───────────────────────────────
        flags.extend(self._check_metadata_tampering(meta))

        # ── 3. Financial Anomalies ──────────────────────────────
        flags.extend(self._check_financial_anomalies(entities))

        # ── 4. Ownership Inconsistencies ────────────────────────
        flags.extend(self._check_ownership(text, entities))

        # ── 5. ML Anomaly Score ─────────────────────────────────
        feature_vec = self._extract_features(text, entities, meta)
        ml_score = self._run_ml_detection(feature_vec)

        if ml_score > 0.6:
            flags.append(AnomalyFlag(
                flag_type="ml_anomaly_detected",
                severity=RiskLevel.high if ml_score > 0.8 else RiskLevel.medium,
                description=f"Machine learning models detected statistical anomalies (score: {ml_score:.2f})",
                confidence=ml_score,
                evidence="IsolationForest + XGBoost ensemble",
            ))

        # ── 6. Compute Scores ───────────────────────────────────
        fraud_score = self._compute_fraud_score(flags, ml_score)
        trust_score = max(0, 100 - fraud_score)

        if fraud_score > 70:
            risk_level = RiskLevel.critical
        elif fraud_score > 50:
            risk_level = RiskLevel.high
        elif fraud_score > 30:
            risk_level = RiskLevel.medium
        else:
            risk_level = RiskLevel.low

        # ── 7. AI Explanation ───────────────────────────────────
        ai_explanation = self._generate_explanation(flags, fraud_score, trust_score)

        return AnomalyResult(
            document_id=doc_id,
            fraud_score=round(fraud_score, 1),
            trust_score=round(trust_score, 1),
            risk_level=risk_level,
            flags=flags,
            extracted_text=text[:3000],
            extracted_metadata=meta,
            ai_explanation=ai_explanation,
            analyzed_at=datetime.now(timezone.utc),
        )

    def _check_text_anomalies(self, text: str, entities: dict) -> List[AnomalyFlag]:
        flags = []
        text_lower = text.lower()

        # Suspicious edit markers
        edit_markers = ["whiteout", "correction fluid", "overwritten", "cancelled", "void"]
        for marker in edit_markers:
            if marker in text_lower:
                flags.append(AnomalyFlag(
                    flag_type="suspicious_edit_marker",
                    severity=RiskLevel.high,
                    description=f"Document contains edit indicator: '{marker}'",
                    confidence=0.85,
                    evidence=marker,
                ))

        # Duplicate date references (inconsistency)
        dates = entities.get("dates", [])
        if len(set(dates)) > 1 and len(dates) > 3:
            flags.append(AnomalyFlag(
                flag_type="date_inconsistency",
                severity=RiskLevel.medium,
                description=f"Multiple inconsistent date references detected: {set(dates)}",
                confidence=0.72,
                evidence=str(dates[:5]),
            ))

        # Suspicious keywords
        fraud_keywords = [
            "forged", "counterfeit", "fabricated", "manipulated",
            "dummy", "fictitious", "benami", "shell company"
        ]
        found = [kw for kw in fraud_keywords if kw in text_lower]
        if found:
            flags.append(AnomalyFlag(
                flag_type="fraud_keyword_detected",
                severity=RiskLevel.critical,
                description=f"High-risk keywords found: {found}",
                confidence=0.95,
                evidence=", ".join(found),
            ))

        # Very short document (incomplete?)
        if len(text.strip()) < 100 and len(text.strip()) > 10:
            flags.append(AnomalyFlag(
                flag_type="incomplete_document",
                severity=RiskLevel.medium,
                description="Document appears incomplete — insufficient text extracted",
                confidence=0.68,
            ))

        return flags

    def _check_metadata_tampering(self, meta: dict) -> List[AnomalyFlag]:
        flags = []

        # Modified after creation
        created = meta.get("pdf_created", "")
        modified = meta.get("pdf_modified", "")
        if created and modified and created != modified:
            flags.append(AnomalyFlag(
                flag_type="metadata_modification_detected",
                severity=RiskLevel.high,
                description=f"PDF metadata shows document was modified after creation. Created: {created}, Modified: {modified}",
                confidence=0.88,
                evidence=f"Created: {created} | Modified: {modified}",
            ))

        # Unknown/suspicious creator tool
        creator = meta.get("pdf_creator", "").lower()
        suspicious_creators = ["photoshop", "gimp", "paint", "editor", "unknown"]
        for sc in suspicious_creators:
            if sc in creator:
                flags.append(AnomalyFlag(
                    flag_type="suspicious_document_creator",
                    severity=RiskLevel.high,
                    description=f"Document was created with image editing software: '{creator}'",
                    confidence=0.82,
                    evidence=creator,
                ))
                break

        return flags

    def _check_financial_anomalies(self, entities: dict) -> List[AnomalyFlag]:
        flags = []
        amounts = entities.get("financial_amounts", [])

        if len(amounts) > 0:
            # Check for unrealistically high amounts
            for amount_str in amounts:
                digits = re.sub(r"[^\d]", "", amount_str)
                if digits and int(digits) > 100_000_000_000:  # > 100 Billion
                    flags.append(AnomalyFlag(
                        flag_type="abnormal_financial_amount",
                        severity=RiskLevel.critical,
                        description=f"Abnormally high financial figure detected: {amount_str}",
                        confidence=0.91,
                        evidence=amount_str,
                    ))

        return flags

    def _check_ownership(self, text: str, entities: dict) -> List[AnomalyFlag]:
        flags = []
        names = entities.get("names", [])

        # Multiple owners (potential ownership conflict)
        if len(set(names)) > 3:
            flags.append(AnomalyFlag(
                flag_type="ownership_complexity",
                severity=RiskLevel.medium,
                description=f"Document references {len(set(names))} distinct entities — potential ownership complexity",
                confidence=0.74,
                evidence=str(names[:4]),
            ))

        # Rapid ownership transfer keywords
        transfer_keywords = ["transfer", "sale deed", "gift deed", "relinquishment", "assignment"]
        found = [kw for kw in transfer_keywords if kw.lower() in text.lower()]
        if len(found) >= 3:
            flags.append(AnomalyFlag(
                flag_type="rapid_ownership_transfer",
                severity=RiskLevel.high,
                description=f"Multiple ownership transfer terms detected — possible title laundering: {found}",
                confidence=0.79,
                evidence=", ".join(found),
            ))

        return flags

    def _extract_features(self, text: str, entities: dict, meta: dict) -> np.ndarray:
        """Convert document to feature vector for ML models."""
        return np.array([
            len(text) / 5000,                                    # normalized length
            len(entities.get("dates", [])) / 10,                 # date count
            len(entities.get("financial_amounts", [])) / 10,     # amount count
            len(entities.get("names", [])) / 5,                  # name count
            1.0 if meta.get("pdf_modified") else 0.0,            # was modified
            1.0 if meta.get("has_signature_region") else 0.0,    # has signature
            min(meta.get("pages", 1), 10) / 10,                  # page count
            len(entities.get("pan_numbers", [])) / 3,            # PAN refs
        ]).reshape(1, -1)

    def _run_ml_detection(self, features: np.ndarray) -> float:
        """Run IsolationForest + XGBoost ensemble."""
        score = 0.0
        count = 0

        if self._iso_forest:
            try:
                iso_score = self._iso_forest.decision_function(features)[0]
                # Convert: more negative = more anomalous
                iso_normalized = max(0, min(1, (-iso_score + 0.5)))
                score += iso_normalized
                count += 1
            except Exception:
                pass

        if self._xgb_model:
            try:
                xgb_prob = self._xgb_model.predict_proba(features)[0][1]
                score += xgb_prob
                count += 1
            except Exception:
                pass

        return round(score / count, 3) if count > 0 else 0.0

    def _compute_fraud_score(self, flags: List[AnomalyFlag], ml_score: float) -> float:
        """Compute final fraud score 0-100."""
        severity_weights = {
            RiskLevel.low: 5,
            RiskLevel.medium: 15,
            RiskLevel.high: 30,
            RiskLevel.critical: 50,
        }

        flag_score = sum(
            severity_weights.get(f.severity, 10) * f.confidence for f in flags
        )
        flag_score = min(flag_score, 80)

        ml_component = ml_score * 20
        total = flag_score + ml_component
        return min(total, 100)

    def _generate_explanation(self, flags: List[AnomalyFlag], fraud_score: float, trust_score: float) -> str:
        if not flags:
            return (
                f"No significant anomalies detected. Document appears authentic with a trust score of "
                f"{trust_score:.0f}/100. Standard processing recommended."
            )

        severity_counts = {}
        for f in flags:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        critical = severity_counts.get(RiskLevel.critical, 0)
        high = severity_counts.get(RiskLevel.high, 0)
        top_flags = [f.flag_type.replace("_", " ") for f in flags[:3]]

        if fraud_score > 70:
            level_text = "HIGH RISK"
        elif fraud_score > 40:
            level_text = "MODERATE RISK"
        else:
            level_text = "LOW RISK"

        return (
            f"{level_text} — Fraud Score: {fraud_score:.0f}/100 | Trust Score: {trust_score:.0f}/100. "
            f"Detected {len(flags)} anomalies ({critical} critical, {high} high severity). "
            f"Key issues: {', '.join(top_flags)}. "
            f"{'Immediate investigation required.' if fraud_score > 70 else 'Manual review recommended.' if fraud_score > 40 else 'Proceed with standard verification.'}"
        )
