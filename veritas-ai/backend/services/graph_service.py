"""
VERITAS AI — Knowledge Graph Service (Neo4j + NetworkX fallback)
"""
import logging
from typing import Any, Dict, List, Optional

import networkx as nx

from models.schemas import GraphData, GraphEdge, GraphNode, RiskLevel

logger = logging.getLogger("veritas.graph")


# ── Demo graph data ───────────────────────────────────────────
DEMO_NODES = [
    {"id": "b001", "label": "Rajesh Kumar", "type": "borrower", "properties": {"loan_amount": 5000000, "credit_score": 620}, "risk_score": 72.0},
    {"id": "b002", "label": "Priya Sharma", "type": "borrower", "properties": {"loan_amount": 2500000, "credit_score": 710}, "risk_score": 28.0},
    {"id": "b003", "label": "Suresh Patel", "type": "borrower", "properties": {"loan_amount": 8000000, "credit_score": 580}, "risk_score": 85.0},
    {"id": "e001", "label": "RK Holdings Pvt Ltd", "type": "entity", "properties": {"reg_no": "MH-2019-123456", "director": "Rajesh Kumar"}, "risk_score": 68.0},
    {"id": "e002", "label": "Patel Constructions", "type": "entity", "properties": {"reg_no": "GJ-2015-789012", "director": "Suresh Patel"}, "risk_score": 79.0},
    {"id": "e003", "label": "SP Real Estate LLP", "type": "entity", "properties": {"reg_no": "MH-2021-345678", "director": "Suresh Patel"}, "risk_score": 81.0},
    {"id": "c001", "label": "Plot No. 47, Andheri", "type": "collateral", "properties": {"value": 7500000, "area": "1200 sqft"}, "risk_score": 65.0},
    {"id": "c002", "label": "Flat 12B, Powai", "type": "collateral", "properties": {"value": 4200000, "area": "850 sqft"}, "risk_score": 45.0},
    {"id": "c003", "label": "Commercial Space, Surat", "type": "collateral", "properties": {"value": 9000000, "area": "2400 sqft"}, "risk_score": 78.0},
    {"id": "t001", "label": "TXN-2023-001", "type": "transaction", "properties": {"amount": 500000, "date": "2023-11-15"}, "risk_score": 55.0},
    {"id": "t002", "label": "TXN-2023-002", "type": "transaction", "properties": {"amount": 1200000, "date": "2023-12-01"}, "risk_score": 82.0},
    {"id": "t003", "label": "TXN-2024-001", "type": "transaction", "properties": {"amount": 750000, "date": "2024-01-10"}, "risk_score": 35.0},
]

DEMO_EDGES = [
    {"source": "b001", "target": "e001", "relationship": "DIRECTOR_OF", "weight": 1.0, "properties": {"since": "2019"}},
    {"source": "b003", "target": "e002", "relationship": "DIRECTOR_OF", "weight": 1.0, "properties": {"since": "2015"}},
    {"source": "b003", "target": "e003", "relationship": "DIRECTOR_OF", "weight": 1.0, "properties": {"since": "2021"}},
    {"source": "b001", "target": "c001", "relationship": "OWNS_COLLATERAL", "weight": 0.9, "properties": {"deed_no": "MH-2020-456"}},
    {"source": "e001", "target": "c001", "relationship": "MORTGAGED_BY", "weight": 0.8, "properties": {"bank": "Canara Bank"}},
    {"source": "b002", "target": "c002", "relationship": "OWNS_COLLATERAL", "weight": 1.0, "properties": {}},
    {"source": "b003", "target": "c003", "relationship": "OWNS_COLLATERAL", "weight": 0.7, "properties": {"dispute": "pending"}},
    {"source": "e002", "target": "c003", "relationship": "MORTGAGED_BY", "weight": 0.9, "properties": {"bank": "Canara Bank"}},
    {"source": "e003", "target": "c003", "relationship": "MORTGAGED_BY", "weight": 0.9, "properties": {"bank": "SBI"}},  # Duplicate collateral!
    {"source": "b001", "target": "t001", "relationship": "INITIATED", "weight": 1.0, "properties": {}},
    {"source": "b003", "target": "t002", "relationship": "INITIATED", "weight": 1.0, "properties": {}},
    {"source": "b002", "target": "t003", "relationship": "INITIATED", "weight": 1.0, "properties": {}},
    {"source": "b001", "target": "b003", "relationship": "ASSOCIATED_WITH", "weight": 0.6, "properties": {"source": "common_address"}},
]


class GraphService:
    def __init__(self):
        self._neo4j_driver = None
        self._nx_graph = self._build_nx_graph()
        self._try_neo4j()

    def _build_nx_graph(self) -> nx.Graph:
        G = nx.DiGraph()
        for node in DEMO_NODES:
            G.add_node(node["id"], **node)
        for edge in DEMO_EDGES:
            G.add_edge(edge["source"], edge["target"], **edge)
        return G

    def _try_neo4j(self):
        """Try to connect to Neo4j, fall back to NetworkX."""
        try:
            from neo4j import GraphDatabase
            import os
            driver = GraphDatabase.driver(
                os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "veritas123")),
            )
            driver.verify_connectivity()
            self._neo4j_driver = driver
            self._seed_neo4j()
            logger.info("Neo4j connected and seeded ✓")
        except Exception as e:
            logger.warning(f"Neo4j unavailable ({e}) — using NetworkX in-memory graph")

    def _seed_neo4j(self):
        """Seed Neo4j with demo graph data."""
        if not self._neo4j_driver:
            return
        try:
            with self._neo4j_driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                for node in DEMO_NODES:
                    session.run(
                        f"CREATE (n:{node['type'].capitalize()} {{id: $id, label: $label, risk_score: $risk_score}})",
                        id=node["id"], label=node["label"], risk_score=node.get("risk_score", 0),
                    )
                for edge in DEMO_EDGES:
                    rel = edge["relationship"]
                    session.run(
                        f"""
                        MATCH (a {{id: $src}}), (b {{id: $tgt}})
                        CREATE (a)-[r:{rel} {{weight: $weight}}]->(b)
                        """,
                        src=edge["source"], tgt=edge["target"], weight=edge["weight"],
                    )
        except Exception as e:
            logger.warning(f"Neo4j seeding failed: {e}")

    async def get_graph(self, entity_type: Optional[str] = None, depth: int = 2) -> GraphData:
        """Get full graph data."""
        if self._neo4j_driver:
            return await self._get_neo4j_graph(entity_type)
        return self._get_nx_graph(entity_type)

    async def _get_neo4j_graph(self, entity_type: Optional[str] = None) -> GraphData:
        try:
            with self._neo4j_driver.session() as session:
                if entity_type:
                    result = session.run(
                        f"MATCH (n:{entity_type.capitalize()}) RETURN n"
                    )
                else:
                    result = session.run("MATCH (n) RETURN n LIMIT 100")
                nodes = [
                    GraphNode(
                        id=record["n"]["id"],
                        label=record["n"]["label"],
                        type=list(record["n"].labels)[0].lower(),
                        risk_score=record["n"].get("risk_score"),
                    )
                    for record in result
                ]
                rel_result = session.run(
                    "MATCH (a)-[r]->(b) RETURN a.id as src, b.id as tgt, type(r) as rel, r.weight as w LIMIT 200"
                )
                edges = [
                    GraphEdge(source=r["src"], target=r["tgt"], relationship=r["rel"], weight=r["w"] or 1.0)
                    for r in rel_result
                ]
                return GraphData(nodes=nodes, edges=edges)
        except Exception as e:
            logger.warning(f"Neo4j query failed: {e}")
            return self._get_nx_graph(entity_type)

    def _get_nx_graph(self, entity_type: Optional[str] = None) -> GraphData:
        """Build GraphData from NetworkX in-memory graph."""
        nodes_data = DEMO_NODES
        edges_data = DEMO_EDGES

        if entity_type:
            valid_ids = {n["id"] for n in nodes_data if n["type"] == entity_type}
            connected = set()
            for e in edges_data:
                if e["source"] in valid_ids or e["target"] in valid_ids:
                    connected.add(e["source"])
                    connected.add(e["target"])
            nodes_data = [n for n in nodes_data if n["id"] in connected or n["id"] in valid_ids]
            edge_ids = {n["id"] for n in nodes_data}
            edges_data = [e for e in edges_data if e["source"] in edge_ids and e["target"] in edge_ids]

        nodes = [
            GraphNode(
                id=n["id"],
                label=n["label"],
                type=n["type"],
                properties=n.get("properties", {}),
                risk_score=n.get("risk_score"),
            )
            for n in nodes_data
        ]
        edges = [
            GraphEdge(
                source=e["source"],
                target=e["target"],
                relationship=e["relationship"],
                weight=e.get("weight", 1.0),
                properties=e.get("properties", {}),
            )
            for e in edges_data
        ]
        return GraphData(
            nodes=nodes,
            edges=edges,
            metadata={"source": "networkx", "total_nodes": len(nodes), "total_edges": len(edges)},
        )

    async def get_subgraph(self, entity_type: str) -> GraphData:
        return self._get_nx_graph(entity_type)

    async def search_entity(self, name: str) -> List[Dict]:
        matches = [
            n for n in DEMO_NODES
            if name.lower() in n["label"].lower()
        ]
        return matches

    async def get_analytics(self) -> Dict[str, Any]:
        G = self._nx_graph
        try:
            centrality = nx.betweenness_centrality(G)
            top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            high_risk = [n for n in DEMO_NODES if (n.get("risk_score") or 0) > 70]
            duplicate_collateral = [
                n for n in DEMO_NODES
                if n["type"] == "collateral" and
                sum(1 for e in DEMO_EDGES if e["target"] == n["id"] and "MORTGAGED" in e["relationship"]) > 1
            ]
            return {
                "total_nodes": G.number_of_nodes(),
                "total_edges": G.number_of_edges(),
                "top_central_entities": [
                    {"id": k, "centrality": round(v, 4)} for k, v in top_central
                ],
                "high_risk_entities": len(high_risk),
                "duplicate_collateral_detected": len(duplicate_collateral),
                "circular_relationships": len(list(nx.simple_cycles(G))),
                "graph_density": round(nx.density(G), 4),
            }
        except Exception as e:
            return {"error": str(e), "total_nodes": G.number_of_nodes()}
