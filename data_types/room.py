from typing import Dict

from data_types.player import Player
from handlers.questions_handler import QuestionsHandler


class Room:
    def __init__(self, room_id: str):
        self.id = room_id
        self.players: Dict[str, Player] = {}
        self.admin: Player | None = None
        self.display: Player | None = None
        self.questions_handler = QuestionsHandler()

    def add_player(self, player: Player):
        self.players[player.id] = player

    def remove_player(self, player_id: str):
        if player_id in self.players:
            del self.players[player_id]

    def update_player_score(self, player_id: str, score: int):
        if player_id in self.players:
            self.players[player_id].score = score

    def set_admin(self, admin: Player):
        self.admin = admin

    def set_display(self, display: Player):
        self.display = display

    def get_state(self):
        return {
            "room_id": self.id,
            "player_count": len(self.players),
            "players": [p.to_dict() for p in self.players.values()],
            "admin": {"id": self.admin.id, "name": self.admin.name} if self.admin else None
        }