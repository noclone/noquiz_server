from typing import Dict

from database.player import Player


class Room:
    def __init__(self, room_id: str):
        self.id = room_id
        self.players: Dict[str, Player] = {}
        self.admin: Player | None = None

    def add_player(self, player: Player):
        self.players[player.id] = player

    def remove_player(self, player_id: str):
        if player_id in self.players:
            del self.players[player_id]

    def set_admin(self, admin: Player):
        self.admin = admin

    def get_state(self):
        return {
            "room_id": self.id,
            "player_count": len(self.players),
            "players": [{"id": p.id, "name": p.name} for p in self.players.values()],
            "admin": {"id": self.admin.id, "name": self.admin.name} if self.admin else None
        }