"""
VERITAS AI — Knowledge Graph API (Neo4j + NetworkX fallback)
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from core.security import get_current_user
from core.database import get_neo4j
from models.schemas import GraphData, GraphEdge, GraphNode
from services.graph_service import GraphService

logger = logging.getLogger("veritas.graph")
router = APIRouter()
graph_service = GraphService()


@router.get("/data", response_model=GraphData)
async def get_graph_data(
    entity_type: Optional[str] = None,
    depth: int = 2,
    current_user: dict = Depends(get_current_user),
):
    """Get knowledge graph data for visualization."""
    try:
        data = await graph_service.get_graph(entity_type=entity_type, depth=depth)
        return data
    except Exception as e:
        logger.error(f"Graph fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/borrowers")
async def get_borrower_graph(current_user: dict = Depends(get_current_user)):
    """Get borrower relationship subgraph."""
    return await graph_service.get_subgraph("borrower")


@router.get("/ownership")
async def get_ownership_graph(current_user: dict = Depends(get_current_user)):
    """Get collateral ownership graph."""
    return await graph_service.get_subgraph("collateral")


@router.get("/transactions")
async def get_transaction_graph(current_user: dict = Depends(get_current_user)):
    """Get transaction linkage graph."""
    return await graph_service.get_subgraph("transaction")


@router.post("/query")
async def query_graph(
    query: dict,
    current_user: dict = Depends(get_current_user),
):
    """Execute a natural language graph query."""
    entity = query.get("entity", "")
    results = await graph_service.search_entity(entity)
    return results


@router.get("/analytics")
async def graph_analytics(current_user: dict = Depends(get_current_user)):
    """Get graph analytics: centrality, clusters, risk nodes."""
    return await graph_service.get_analytics()
