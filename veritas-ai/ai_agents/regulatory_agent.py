"""
VERITAS AI — Regulatory Intelligence Agent
Summarizes RBI/SEBI regulations and generates MAPs
"""
import logging
import os
from typing import Dict, List, TypedDict

logger = logging.getLogger("veritas.agents.regulatory")


class RegulatoryState(TypedDict):
    query: str
    retrieved_docs: List[str]
    summary: str
    action_points: List[Dict]


def retrieve_docs_node(state: RegulatoryState) -> RegulatoryState:
    """Node 1: Retrieve relevant regulation chunks."""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from backend.services.vector_store import VectorStoreService
        vs = VectorStoreService()
        results = vs.retrieve(state["query"], k=5)
        state["retrieved_docs"] = [r["document"] for r in results]
    except Exception as e:
        logger.warning(f"Retrieval failed: {e}")
        state["retrieved_docs"] = ["No regulations retrieved"]
    return state


def summarize_node(state: RegulatoryState) -> RegulatoryState:
    """Node 2: Summarize retrieved regulations using Ollama."""
    docs = state.get("retrieved_docs", [])
    context = "\n\n".join(docs[:3])[:1500]

    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature=0.1,
        )
        prompt = f"""You are a regulatory compliance expert at an Indian bank.

Summarize the following regulatory text in 3-4 bullet points that a banking officer can act on:

{context}

Topic: {state['query']}

Provide a clear, actionable summary. Use banking language."""

        state["summary"] = llm.invoke(prompt)
    except Exception as e:
        logger.warning(f"Summarization failed: {e}")
        state["summary"] = f"Regulatory summary for '{state['query']}': {context[:400]}..."

    return state


def generate_maps_node(state: RegulatoryState) -> RegulatoryState:
    """Node 3: Generate Measurable Action Points from the summary."""
    summary = state.get("summary", "")
    query = state.get("query", "")

    # Extract key action items from summary
    action_points = []
    action_keywords = ["must", "required", "shall", "mandatory", "within", "submit", "verify", "file", "report"]
    sentences = summary.split(".")
    for s in sentences:
        s = s.strip()
        if any(kw in s.lower() for kw in action_keywords) and len(s) > 20:
            action_points.append({
                "title": s[:80] + "..." if len(s) > 80 else s,
                "description": s,
                "priority": "high" if any(k in s.lower() for k in ["mandatory", "must", "immediately"]) else "medium",
                "source": query,
            })

    state["action_points"] = action_points[:5]
    return state


def run_regulatory_agent(query: str) -> dict:
    """Run the full regulatory intelligence agent."""
    initial_state = RegulatoryState(
        query=query,
        retrieved_docs=[],
        summary="",
        action_points=[],
    )

    try:
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(RegulatoryState)
        workflow.add_node("retrieve", retrieve_docs_node)
        workflow.add_node("summarize", summarize_node)
        workflow.add_node("generate_maps", generate_maps_node)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "summarize")
        workflow.add_edge("summarize", "generate_maps")
        workflow.add_edge("generate_maps", END)
        app = workflow.compile()
        result = app.invoke(initial_state)
    except ImportError:
        state = retrieve_docs_node(initial_state)
        state = summarize_node(state)
        state = generate_maps_node(state)
        result = state

    return {
        "query": query,
        "summary": result["summary"],
        "action_points": result["action_points"],
        "docs_retrieved": len(result["retrieved_docs"]),
    }
