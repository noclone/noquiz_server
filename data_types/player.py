from dataclasses import dataclass

from fastapi import WebSocket


@dataclass
class Player:
    id: str
    name: str
    websocket: WebSocket
    score: int = 0
    current_answer: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "current_answer": self.current_answer
        }