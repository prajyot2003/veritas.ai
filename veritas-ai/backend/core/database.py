"""
VERITAS AI — Database Connections: Redis, Neo4j, ChromaDB
"""
import logging
from typing import Optional

import redis.asyncio as aioredis
import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings
from core.security import seed_users

logger = logging.getLogger("veritas.db")

# ── Global Instances ─────────────────────────────────────────
redis_client: Optional[aioredis.Redis] = None
chroma_client: Optional[chromadb.PersistentClient] = None
neo4j_driver = None


async def init_db():
    """Initialize all database connections at startup."""
    global redis_client, chroma_client, neo4j_driver

    # Seed users
    seed_users()
    logger.info("Users seeded ✓")

    # Redis
    try:
        redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Redis connected ✓")
    except Exception as e:
        logger.warning(f"Redis unavailable ({e}) — using in-memory fallback")
        redis_client = None

    # ChromaDB
    try:
        chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB connected ✓")
    except Exception as e:
        logger.error(f"ChromaDB init failed: {e}")

    # Neo4j
    try:
        from neo4j import AsyncGraphDatabase
        neo4j_driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        await neo4j_driver.verify_connectivity()
        logger.info("Neo4j connected ✓")
    except Exception as e:
        logger.warning(f"Neo4j unavailable ({e}) — using NetworkX fallback")
        neo4j_driver = None


def get_redis() -> Optional[aioredis.Redis]:
    return redis_client


def get_chroma() -> Optional[chromadb.PersistentClient]:
    return chroma_client


def get_neo4j():
    return neo4j_driver
