from dataclasses import dataclass

from fastapi import WebSocket


@dataclass
class Player:
    id: str
    name: str
    score: int
    websocket: WebSocket