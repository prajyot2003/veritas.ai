"""
VERITAS AI — Vector Store Service (ChromaDB + Sentence Transformers)
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("veritas.vectorstore")


class VectorStoreService:
    COLLECTION_NAME = "veritas_regulations"

    def __init__(self):
        self._client = None
        self._collection = None
        self._embedder = None
        self._init()

    def _init(self):
        """Initialize ChromaDB and embedding model."""
        try:
            import chromadb
            from chromadb.config import Settings

            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chromadb")
            Path(persist_dir).mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"ChromaDB collection '{self.COLLECTION_NAME}' ready ✓")
        except Exception as e:
            logger.warning(f"ChromaDB init failed: {e} — retrieval disabled")

        try:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
            self._embedder = SentenceTransformer(model_name)
            logger.info(f"Embedding model '{model_name}' loaded ✓")
        except Exception as e:
            logger.warning(f"Embedding model failed: {e} — using keyword fallback")

    def _embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        if self._embedder is None:
            return None
        try:
            embeddings = self._embedder.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
            return None

    def ingest_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Ingest documents into ChromaDB vector store."""
        if not self._collection:
            return 0

        texts = [d["content"] for d in documents]
        ids = [d["id"] for d in documents]
        metadatas = [d.get("metadata", {}) for d in documents]

        embeddings = self._embed(texts)

        try:
            if embeddings:
                self._collection.upsert(
                    ids=ids,
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
            else:
                self._collection.upsert(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                )
            logger.info(f"Ingested {len(documents)} documents into ChromaDB")
            return len(documents)
        except Exception as e:
            logger.error(f"ChromaDB ingest failed: {e}")
            return 0

    def retrieve(self, query: str, k: int = 5, filter_meta: Optional[dict] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query."""
        if not self._collection:
            return self._keyword_fallback(query)

        try:
            query_embedding = self._embed([query])
            kwargs = {"n_results": k, "include": ["documents", "metadatas", "distances"]}
            if filter_meta:
                kwargs["where"] = filter_meta

            if query_embedding:
                results = self._collection.query(
                    query_embeddings=query_embedding,
                    **kwargs,
                )
            else:
                results = self._collection.query(
                    query_texts=[query],
                    **kwargs,
                )

            output = []
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]

            for doc, meta, dist in zip(docs, metas, dists):
                output.append({
                    "document": doc,
                    "metadata": meta,
                    "relevance_score": round(1 - dist, 3),
                })
            return output
        except Exception as e:
            logger.warning(f"ChromaDB query failed: {e}")
            return self._keyword_fallback(query)

    def _keyword_fallback(self, query: str) -> List[Dict[str, Any]]:
        """Simple keyword-based fallback when ChromaDB is unavailable."""
        try:
            from backend.data.regulations import SAMPLE_REGULATIONS
        except ImportError:
            try:
                from data.regulations import SAMPLE_REGULATIONS
            except ImportError:
                return []
        results = []
        query_lower = query.lower()
        for reg in SAMPLE_REGULATIONS:
            if any(word in reg["content"].lower() for word in query_lower.split()[:5]):
                results.append({
                    "document": reg["content"][:500],
                    "metadata": reg.get("metadata", {}),
                    "relevance_score": 0.5,
                })
        return results[:5]

    def count(self) -> int:
        if not self._collection:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0
