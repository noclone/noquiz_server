import json
import time

from data_types.room import Room


class MessageHandler:
    async def handle_message(self, message, player, room):
        data = json.loads(message)
        if "buzz" in data.keys():
            await self.send_to_admin(room, json.dumps({"buzz": [player.name, time.time()]}))
        elif "player-answer" in data.keys():
            player.current_answer = data["player-answer"]
        elif 'player-right-order-answer' in data.keys():
            data["player_name"] = player.name
            await self.send_to_display(room, json.dumps(data))
        else:
            await self.broadcast_to_room(room, message)

    async def broadcast_to_room(self, room: Room, message: str):
        players = list(room.players.values())
        if room.admin:
            players.append(room.admin)
        if room.display:
            players.append(room.display)

        for player in players:
            try:
                await player.websocket.send_text(message)
            except:
                continue

    async def send_to_admin(self, room: Room, message: str):
        await room.admin.websocket.send_text(message)

    async def send_to_display(self, room: Room, message: str):
        await room.display.websocket.send_text(message)
