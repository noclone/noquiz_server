from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from uuid import uuid4

from database.player import Player
from database.room import Room
from managers.room_manager import RoomManager

app = FastAPI()

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

room_manager = RoomManager()

@app.post("/api/rooms/create")
async def create_room():
    room = room_manager.create_room()
    return room.get_state()

@app.get("/api/rooms/{room_id}")
async def get_room(room_id: str):
    room = room_manager.get_room(room_id)
    if room:
        return room.get_state()
    raise HTTPException(status_code=404, detail="Room not found")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    try:
        init_data = await websocket.receive_text()
        player_info = json.loads(init_data)
        player = Player(
            id=str(uuid4()),
            name=player_info.get("name", "Anonymous"),
            websocket=websocket
        )
    except Exception:
        await websocket.close()
        return

    room = room_manager.get_room(room_id)
    if not room:
        await websocket.close()
        return

    if player_info.get("admin", False):
        room.set_admin(player)
    else:
        room.add_player(player)

    try:
        room_state = room.get_state()
        await broadcast_to_room(room, json.dumps(room_state))

        while True:
            data = await websocket.receive_text()
            await broadcast_to_room(room, data)
    except WebSocketDisconnect:
        if room.admin is not None and room.admin.id == player.id:
            room.admin = None
        else:
            room.remove_player(player.id)

        if room.admin is None:
            await broadcast_to_room(room, json.dumps({"room-deleted": True}))
            room_manager.remove_room(room_id)
        else:
            room_state = room.get_state()
            await broadcast_to_room(room, json.dumps(room_state))

async def broadcast_to_room(room: Room, message: str):
    players = list(room.players.values())
    if room.admin:
        players.append(room.admin)

    for player in players:
        try:
            await player.websocket.send_text(message)
        except:
            continue


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)