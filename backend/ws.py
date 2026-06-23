"""
WebSocket connection manager - extracted for organization.
"""
import json
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.user_sockets: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.user_sockets.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: str, ws: WebSocket):
        if user_id in self.user_sockets:
            self.user_sockets[user_id] = [s for s in self.user_sockets[user_id] if s is not ws]
            if not self.user_sockets[user_id]:
                self.user_sockets.pop(user_id, None)

    async def send_to_user(self, user_id: str, payload: dict):
        for ws in list(self.user_sockets.get(user_id, [])):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                pass

# broadcast_to_conversation lives in core/realtime.py

