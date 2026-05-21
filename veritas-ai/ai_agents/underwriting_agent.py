"""
VERITAS AI — Underwriting Intelligence Agent
"""
import logging
import os
from typing import Any, Dict, List, TypedDict

logger = logging.getLogger("veritas.agents.underwriting")


class UnderwritingState(TypedDict):
    document_id: str
    fraud_score: float
    trust_score: float
    anomaly_flags: List[Dict]
    graph_signals: Dict[str, Any]
    borrower_name: str
    loan_amount: float
    collateral_value: float
    risk_assessment: str
    decision: str
    confidence: float
    key_factors: List[str]
    recommendations: List[str]
    narrative: str


def assess_fraud_signals_node(state: UnderwritingState) -> UnderwritingState:
    """Node 1: Assess fraud signals from anomaly results."""
    fraud_score = state.get("fraud_score", 0)
    flags = state.get("anomaly_flags", [])

    critical_flags = [f for f in flags if f.get("severity") in ("critical", "high")]
    state["risk_assessment"] = "high" if (fraud_score > 60 or len(critical_flags) > 2) else \
                                "medium" if (fraud_score > 30 or len(critical_flags) > 0) else "low"
    return state


def assess_graph_signals_node(state: UnderwritingState) -> UnderwritingState:
    """Node 2: Incorporate knowledge graph signals."""
    graph = state.get("graph_signals", {})

    if graph.get("duplicate_collateral"):
        state["risk_assessment"] = "high"

    if graph.get("circular_relationships"):
        state["key_factors"] = state.get("key_factors", []) + ["Circular ownership relationship detected"]

    if graph.get("associated_high_risk"):
        state["key_factors"] = state.get("key_factors", []) + ["Connected to high-risk entities"]

    return state


def make_decision_node(state: UnderwritingState) -> UnderwritingState:
    """Node 3: Make underwriting decision."""
    fraud_score = state.get("fraud_score", 0)
    risk = state.get("risk_assessment", "medium")

    ltv = 0.0
    if state.get("collateral_value", 0) > 0:
        ltv = (state.get("loan_amount", 0) / state["collateral_value"]) * 100

    key_factors = state.get("key_factors", [])

    if fraud_score > 70 or risk == "high":
        state["decision"] = "reject"
        state["confidence"] = 0.88
        key_factors.extend(["Fraud score exceeds threshold", f"Risk level: {risk.upper()}"])
        state["recommendations"] = [
            "Escalate to fraud investigation team",
            "Do not disburse funds",
            "File Suspicious Activity Report with FIU-IND",
            "Conduct in-person verification",
        ]
    elif fraud_score > 40 or risk == "medium":
        state["decision"] = "review"
        state["confidence"] = 0.74
        key_factors.extend(["Moderate anomaly signals", "Requires manual review"])
        state["recommendations"] = [
            "Request additional KYC documentation",
            "Verify ownership through state land registry",
            "Cross-verify financial statements with IT returns",
        ]
    else:
        state["decision"] = "approve"
        state["confidence"] = 0.91
        key_factors.extend(["Clean fraud indicators", f"Acceptable LTV: {ltv:.1f}%"])
        state["recommendations"] = [
            "Proceed with standard loan processing",
            "Retain KYC records for 5 years",
            "Conduct annual review",
        ]

    if ltv > 80:
        key_factors.append(f"High LTV ratio: {ltv:.1f}% (threshold: 80%)")
        state["decision"] = "review" if state["decision"] == "approve" else state["decision"]

    state["key_factors"] = key_factors[:6]
    return state


def generate_narrative_node(state: UnderwritingState) -> UnderwritingState:
    """Node 4: Generate explainable underwriting narrative."""
    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=0.15,
        )
        prompt = f"""You are a senior bank underwriter. Generate a clear, professional underwriting decision narrative.

Borrower: {state.get('borrower_name', 'Unknown')}
Loan Amount: ₹{state.get('loan_amount', 0):,.0f}
Fraud Score: {state.get('fraud_score', 0):.1f}/100
Decision: {state.get('decision', 'review').upper()}
Key Factors: {', '.join(state.get('key_factors', [])[:4])}
Risk Level: {state.get('risk_assessment', 'medium').upper()}

Write a 3-4 sentence professional underwriting narrative explaining this decision. Be specific, use the data provided, and maintain a formal banking tone."""

        narrative = llm.invoke(prompt)
        state["narrative"] = narrative
    except Exception as e:
        logger.warning(f"LLM narrative failed: {e}")
        decision = state.get("decision", "review")
        fraud_score = state.get("fraud_score", 0)
        trust_score = state.get("trust_score", 0)
        if decision == "reject":
            state["narrative"] = (
                f"Underwriting decision: REJECT. High fraud risk detected (score: {fraud_score:.0f}/100, "
                f"trust: {trust_score:.0f}/100). Document anomalies and ownership inconsistencies present "
                "an unacceptable risk profile. Immediate escalation to the fraud investigation team is required."
            )
        elif decision == "review":
            state["narrative"] = (
                f"Underwriting decision: MANUAL REVIEW REQUIRED. Moderate risk indicators detected "
                f"(fraud score: {fraud_score:.0f}/100). Additional documentation and verification are "
                "needed before a final credit decision can be made."
            )
        else:
            state["narrative"] = (
                f"Underwriting decision: APPROVE (conditional). Risk profile is acceptable "
                f"(fraud score: {fraud_score:.0f}/100, trust: {trust_score:.0f}/100). "
                "Proceed with standard loan processing subject to final documentation review."
            )
    return state


def run_underwriting_agent(
    document_id: str,
    fraud_score: float,
    trust_score: float,
    anomaly_flags: list = None,
    graph_signals: dict = None,
    borrower_name: str = "Unknown",
    loan_amount: float = 0,
    collateral_value: float = 0,
) -> dict:
    """Run the underwriting intelligence agent."""
    initial_state = UnderwritingState(
        document_id=document_id,
        fraud_score=fraud_score,
        trust_score=trust_score,
        anomaly_flags=anomaly_flags or [],
        graph_signals=graph_signals or {},
        borrower_name=borrower_name,
        loan_amount=loan_amount,
        collateral_value=collateral_value,
        risk_assessment="",
        decision="",
        confidence=0.0,
        key_factors=[],
        recommendations=[],
        narrative="",
    )

    try:
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(UnderwritingState)
        workflow.add_node("assess_fraud", assess_fraud_signals_node)
        workflow.add_node("assess_graph", assess_graph_signals_node)
        workflow.add_node("make_decision", make_decision_node)
        workflow.add_node("generate_narrative", generate_narrative_node)
        workflow.set_entry_point("assess_fraud")
        workflow.add_edge("assess_fraud", "assess_graph")
        workflow.add_edge("assess_graph", "make_decision")
        workflow.add_edge("make_decision", "generate_narrative")
        workflow.add_edge("generate_narrative", END)
        app = workflow.compile()
        result = app.invoke(initial_state)
    except ImportError:
        state = assess_fraud_signals_node(initial_state)
        state = assess_graph_signals_node(state)
        state = make_decision_node(state)
        state = generate_narrative_node(state)
        result = state

    return {
        "document_id": document_id,
        "decision": result["decision"],
        "confidence": result["confidence"],
        "risk_score": fraud_score,
        "explanation": result["narrative"],
        "key_factors": result["key_factors"],
        "recommendations": result["recommendations"],
    }
