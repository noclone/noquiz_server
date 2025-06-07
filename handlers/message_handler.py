import json
import time

from database.room import Room


class MessageHandler:
    async def handle_message(self, message, player, room):
        if "buzz" in message:
            await self.send_to_admin(room, json.dumps({"buzz": [player.name, time.time()]}))
        else:
            await self.broadcast_to_room(room, message)

    async def broadcast_to_room(self, room: Room, message: str):
        players = list(room.players.values())
        if room.admin:
            players.append(room.admin)

        for player in players:
            try:
                await player.websocket.send_text(message)
            except:
                continue

    async def send_to_admin(self, room: Room, message: str):
        await room.admin.websocket.send_text(message)
