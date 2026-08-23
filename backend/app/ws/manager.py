"""
NeuroScrape - WebSocket Manager
Handles live connection multiplexing by job_id to stream logs, progress,
heal_events, and results in real time to the frontend test console and product UI.
"""

import json
import logging
from typing import Any, Dict, List
from fastapi import WebSocket

logger = logging.getLogger("neuroscrape.ws")


class ConnectionManager:
    def __init__(self):
        # Map of job_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Global subscribers (e.g. NeuroWatch aggregate dashboard)
        self.global_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
        logger.info(f"WebSocket client connected to job stream: {job_id}")

    async def connect_global(self, websocket: WebSocket):
        """Connect a subscriber to the global aggregate feed (all watches)."""
        await websocket.accept()
        self.global_connections.append(websocket)
        logger.info("WebSocket client connected to global aggregate feed.")

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            if websocket in self.active_connections[job_id]:
                self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        logger.info(f"WebSocket client disconnected from job stream: {job_id}")

    def disconnect_global(self, websocket: WebSocket):
        if websocket in self.global_connections:
            self.global_connections.remove(websocket)
        logger.info("WebSocket client disconnected from global aggregate feed.")

    async def broadcast_to_job(self, job_id: str, message: Dict[str, Any]):
        """Broadcasts a structured JSON event to all listeners of a specific job_id."""
        if job_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Failed to send WS message to connection: {e}")
                    dead_connections.append(connection)
            for dead in dead_connections:
                self.disconnect(dead, job_id)

    async def broadcast_to_global(self, message: Dict[str, Any]):
        """Broadcasts to all global aggregate feed subscribers."""
        dead = []
        for conn in self.global_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect_global(d)

    async def send_log(self, job_id: str, msg: str, level: str = "info"):
        await self.broadcast_to_job(job_id, {
            "type": "log",
            "message": msg,
            "level": level
        })

    async def send_progress(self, job_id: str, percent: int, msg: str):
        await self.broadcast_to_job(job_id, {
            "type": "progress",
            "percent": percent,
            "message": msg
        })

    async def send_heal_event(self, job_id: str, heal_data: Dict[str, Any]):
        await self.broadcast_to_job(job_id, {
            "type": "heal_event",
            "message": f"Healed selector for {heal_data.get('field_name')} using {heal_data.get('method')}",
            **heal_data
        })

    async def send_done(self, job_id: str, rows: List[Dict[str, Any]], collector_id: str = None):
        await self.broadcast_to_job(job_id, {
            "type": "done",
            "message": "Scrape completed successfully",
            "collector_id": collector_id,
            "rows": rows
        })

    async def send_error(self, job_id: str, error_msg: str):
        await self.broadcast_to_job(job_id, {
            "type": "error",
            "message": error_msg
        })

    async def send_watch_update(self, watch_id: str, update_data: Dict[str, Any]):
        """Send a watch_update event to the per-watch channel and global feed."""
        await self.broadcast_to_job(f"watch_{watch_id}", update_data)
        await self.broadcast_to_global(update_data)


ws_manager = ConnectionManager()

