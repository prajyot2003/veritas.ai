"""
VERITAS AI — LangGraph Fraud Detection Agent
"""
import logging
import os
from typing import Any, Dict, TypedDict

logger = logging.getLogger("veritas.agents.fraud")


class FraudState(TypedDict):
    document_text: str
    document_id: str
    ocr_metadata: Dict[str, Any]
    anomaly_flags: list
    fraud_score: float
    ai_reasoning: str
    final_verdict: str


def _get_llm():
    """Get Ollama LLM."""
    try:
        from langchain_ollama import OllamaLLM
        return OllamaLLM(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=0.1,
        )
    except Exception as e:
        logger.warning(f"Ollama unavailable: {e} — using deterministic fallback")
        return None


def analyze_ocr_node(state: FraudState) -> FraudState:
    """Node 1: Analyze OCR output for suspicious patterns."""
    text = state["document_text"]
    flags = list(state.get("anomaly_flags", []))

    fraud_indicators = [
        ("whiteout", "Edit correction marker detected"),
        ("overwritten", "Text overwrite indicator"),
        ("forged", "Forgery keyword in document"),
        ("benami", "Benami transaction indicator"),
        ("shell company", "Shell company reference"),
        ("fictitious", "Fictitious entity mentioned"),
    ]

    for keyword, description in fraud_indicators:
        if keyword.lower() in text.lower():
            flags.append({"type": "keyword_fraud", "detail": description, "severity": "high"})

    state["anomaly_flags"] = flags
    return state


def run_ml_scoring_node(state: FraudState) -> FraudState:
    """Node 2: Run ML-based fraud scoring."""
    flags = state.get("anomaly_flags", [])
    text = state.get("document_text", "")

    # Score based on flag severity
    score = 0.0
    for flag in flags:
        if flag.get("severity") == "critical":
            score += 25
        elif flag.get("severity") == "high":
            score += 15
        elif flag.get("severity") == "medium":
            score += 8
        else:
            score += 3

    # Text-length heuristic
    if len(text) < 50:
        score += 10

    state["fraud_score"] = min(score, 100.0)
    return state


def generate_reasoning_node(state: FraudState) -> FraudState:
    """Node 3: Generate AI explanation using Ollama."""
    llm = _get_llm()
    flags = state.get("anomaly_flags", [])
    fraud_score = state.get("fraud_score", 0)

    if llm and flags:
        flag_summary = "\n".join(f"- {f.get('detail', f.get('type', 'Unknown'))}" for f in flags[:5])
        prompt = f"""You are a banking fraud analyst. Analyze this document assessment and provide a concise explanation.

Fraud Score: {fraud_score:.1f}/100
Detected Issues:
{flag_summary}

Provide a 2-3 sentence professional explanation of the risk findings and recommended action. Be specific and factual."""

        try:
            reasoning = llm.invoke(prompt)
            state["ai_reasoning"] = reasoning
        except Exception as e:
            logger.warning(f"LLM reasoning failed: {e}")
            state["ai_reasoning"] = _fallback_reasoning(fraud_score, flags)
    else:
        state["ai_reasoning"] = _fallback_reasoning(fraud_score, flags)

    return state


def determine_verdict_node(state: FraudState) -> FraudState:
    """Node 4: Determine final fraud verdict."""
    score = state.get("fraud_score", 0)
    if score > 70:
        verdict = "HIGH_RISK_FRAUD_SUSPECTED"
    elif score > 40:
        verdict = "MODERATE_RISK_REVIEW_REQUIRED"
    else:
        verdict = "LOW_RISK_PROCEED"

    state["final_verdict"] = verdict
    return state


def _fallback_reasoning(fraud_score: float, flags: list) -> str:
    if fraud_score > 70:
        return (
            f"Critical fraud risk detected (score: {fraud_score:.0f}/100). "
            f"Document shows {len(flags)} anomaly indicators including potential forgery. "
            "Immediate escalation to compliance team recommended."
        )
    elif fraud_score > 40:
        return (
            f"Moderate fraud risk detected (score: {fraud_score:.0f}/100). "
            f"Document exhibits {len(flags)} suspicious patterns requiring manual review. "
            "Do not disburse funds until verification is complete."
        )
    return (
        f"Low fraud risk (score: {fraud_score:.0f}/100). "
        "Document appears consistent with no major red flags. "
        "Proceed with standard verification procedures."
    )


def run_fraud_agent(document_text: str, document_id: str, ocr_metadata: dict = None, anomaly_flags: list = None) -> dict:
    """Run the complete fraud detection agent pipeline."""
    try:
        from langgraph.graph import StateGraph, END

        initial_state = FraudState(
            document_text=document_text,
            document_id=document_id,
            ocr_metadata=ocr_metadata or {},
            anomaly_flags=anomaly_flags or [],
            fraud_score=0.0,
            ai_reasoning="",
            final_verdict="",
        )

        # Build LangGraph
        workflow = StateGraph(FraudState)
        workflow.add_node("analyze_ocr", analyze_ocr_node)
        workflow.add_node("run_ml_scoring", run_ml_scoring_node)
        workflow.add_node("generate_reasoning", generate_reasoning_node)
        workflow.add_node("determine_verdict", determine_verdict_node)

        workflow.set_entry_point("analyze_ocr")
        workflow.add_edge("analyze_ocr", "run_ml_scoring")
        workflow.add_edge("run_ml_scoring", "generate_reasoning")
        workflow.add_edge("generate_reasoning", "determine_verdict")
        workflow.add_edge("determine_verdict", END)

        app = workflow.compile()
        result = app.invoke(initial_state)

        return {
            "document_id": document_id,
            "fraud_score": result["fraud_score"],
            "verdict": result["final_verdict"],
            "reasoning": result["ai_reasoning"],
            "flags": result["anomaly_flags"],
        }

    except ImportError:
        logger.warning("LangGraph not available — running nodes directly")
        state = FraudState(
            document_text=document_text,
            document_id=document_id,
            ocr_metadata=ocr_metadata or {},
            anomaly_flags=anomaly_flags or [],
            fraud_score=0.0,
            ai_reasoning="",
            final_verdict="",
        )
        state = analyze_ocr_node(state)
        state = run_ml_scoring_node(state)
        state = generate_reasoning_node(state)
        state = determine_verdict_node(state)
        return {
            "document_id": document_id,
            "fraud_score": state["fraud_score"],
            "verdict": state["final_verdict"],
            "reasoning": state["ai_reasoning"],
            "flags": state["anomaly_flags"],
        }
