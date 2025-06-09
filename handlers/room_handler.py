from typing import Dict, Optional
from uuid import uuid4

from data_types.room import Room


class RoomHandler:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    def create_room(self) -> Room:
        room_id = str(uuid4())
        room = Room(room_id)
        self.rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def remove_room(self, room_id: str):
        if room_id in self.rooms:
            del self.rooms[room_id]
