from __future__ import annotations

from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(username, set()).add(websocket)

    def disconnect(self, username: str, websocket: WebSocket) -> None:
        if username in self.active:
            self.active[username].discard(websocket)

    async def broadcast(self, username: str, message: dict) -> None:
        for websocket in list(self.active.get(username, set())):
            await websocket.send_json(message)


MANAGER = ConnectionManager()
