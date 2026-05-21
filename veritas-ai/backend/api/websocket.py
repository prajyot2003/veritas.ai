"""
VERITAS AI — WebSocket for Real-Time Alerts
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("veritas.ws")
router = APIRouter()

# ── Connection Manager ────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)
        logger.info(f"WebSocket client connected ({len(self.active_connections)} total)")

    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)

    async def broadcast(self, message: dict):
        disconnected = []
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.active_connections.remove(ws)


manager = ConnectionManager()


@router.websocket("/alerts")
async def websocket_alerts(ws: WebSocket):
    """WebSocket endpoint for real-time alerts."""
    await manager.connect(ws)
    try:
        # Send initial ping
        await ws.send_json({"type": "connected", "message": "VERITAS AI real-time feed active"})

        # Heartbeat loop
        while True:
            await asyncio.sleep(30)
            await ws.send_json({"type": "ping", "timestamp": datetime.now(timezone.utc).isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(ws)
        logger.info("WebSocket client disconnected")


async def broadcast_alert(alert: dict):
    """Broadcast an alert to all connected clients."""
    await manager.broadcast({"type": "alert", "data": alert, "timestamp": datetime.now(timezone.utc).isoformat()})
