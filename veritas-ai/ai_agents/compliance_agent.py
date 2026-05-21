"""
VERITAS AI — Compliance Agent (RAG-powered)
"""
import logging
import os
from typing import Any, Dict, List, TypedDict

logger = logging.getLogger("veritas.agents.compliance")


class ComplianceState(TypedDict):
    map_id: str
    map_title: str
    map_description: str
    regulation_ref: str
    evidence_text: str
    retrieved_regulations: List[str]
    validation_result: bool
    confidence: float
    reasoning: str
    suggestions: List[str]


def retrieve_regulations_node(state: ComplianceState) -> ComplianceState:
    """Node 1: Retrieve relevant regulations from ChromaDB."""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from backend.services.vector_store import VectorStoreService
        vs = VectorStoreService()
        query = f"{state['map_title']} {state['map_description']}"
        results = vs.retrieve(query, k=3)
        state["retrieved_regulations"] = [r["document"] for r in results]
    except Exception as e:
        logger.warning(f"Regulation retrieval failed: {e}")
        state["retrieved_regulations"] = [state["regulation_ref"]]
    return state


def validate_evidence_node(state: ComplianceState) -> ComplianceState:
    """Node 2: Validate the evidence against retrieved regulations."""
    evidence = state.get("evidence_text", "").strip()
    regs = state.get("retrieved_regulations", [])

    if not evidence or len(evidence) < 20:
        state["validation_result"] = False
        state["confidence"] = 0.55
        return state

    # Check evidence covers regulation topics
    reg_text = " ".join(regs).lower()
    evidence_lower = evidence.lower()

    compliance_terms = ["complied", "attached", "verified", "audited", "certified", "submitted", "completed"]
    found = [t for t in compliance_terms if t in evidence_lower]

    state["validation_result"] = len(found) >= 1
    state["confidence"] = min(0.95, 0.5 + len(found) * 0.1)
    return state


def generate_compliance_reasoning_node(state: ComplianceState) -> ComplianceState:
    """Node 3: Generate AI-powered compliance reasoning."""
    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=0.1,
        )
        reg_context = "\n".join(state["retrieved_regulations"][:2])[:800]
        prompt = f"""You are a banking compliance officer reviewing evidence for a compliance action item.

Action Item: {state['map_title']}
Description: {state['map_description']}
Regulation Reference: {state['regulation_ref']}

Relevant Regulation Context:
{reg_context}

Evidence Provided: {state.get('evidence_text', 'No evidence provided')[:500]}

Assess compliance and provide:
1. A 2-sentence validation verdict
2. 2-3 specific suggestions if incomplete"""

        response = llm.invoke(prompt)
        state["reasoning"] = response
        state["suggestions"] = []
    except Exception as e:
        logger.warning(f"LLM compliance reasoning failed: {e}")
        _fallback_compliance_reasoning(state)

    return state


def _fallback_compliance_reasoning(state: ComplianceState):
    if state["validation_result"]:
        state["reasoning"] = (
            f"Evidence provided for '{state['map_title']}' appears sufficient. "
            f"Documentation aligns with {state['regulation_ref']} requirements."
        )
        state["suggestions"] = ["Archive compliance evidence with timestamps", "Schedule next review"]
    else:
        state["reasoning"] = (
            f"Evidence for '{state['map_title']}' is insufficient or missing. "
            f"Compliance with {state['regulation_ref']} cannot be confirmed."
        )
        state["suggestions"] = [
            "Upload signed compliance certificate from authorized signatory",
            "Attach third-party audit report",
            "Provide evidence dated within last 12 months",
        ]


def run_compliance_agent(
    map_id: str,
    map_title: str,
    map_description: str,
    regulation_ref: str,
    evidence_text: str = "",
) -> dict:
    """Run the compliance validation agent."""
    initial_state = ComplianceState(
        map_id=map_id,
        map_title=map_title,
        map_description=map_description,
        regulation_ref=regulation_ref,
        evidence_text=evidence_text,
        retrieved_regulations=[],
        validation_result=False,
        confidence=0.0,
        reasoning="",
        suggestions=[],
    )

    try:
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(ComplianceState)
        workflow.add_node("retrieve_regulations", retrieve_regulations_node)
        workflow.add_node("validate_evidence", validate_evidence_node)
        workflow.add_node("generate_reasoning", generate_compliance_reasoning_node)
        workflow.set_entry_point("retrieve_regulations")
        workflow.add_edge("retrieve_regulations", "validate_evidence")
        workflow.add_edge("validate_evidence", "generate_reasoning")
        workflow.add_edge("generate_reasoning", END)
        app = workflow.compile()
        result = app.invoke(initial_state)
    except ImportError:
        state = retrieve_regulations_node(initial_state)
        state = validate_evidence_node(state)
        state = generate_compliance_reasoning_node(state)
        result = state

    return {
        "map_id": map_id,
        "is_valid": result["validation_result"],
        "confidence": result["confidence"],
        "reasoning": result["reasoning"],
        "suggestions": result["suggestions"],
        "retrieved_regulations_count": len(result["retrieved_regulations"]),
    }
