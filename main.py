from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from uuid import uuid4

from data_types.player import Player
from handlers.message_handler import MessageHandler
from handlers.room_handler import RoomHandler

app = FastAPI()

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

room_handler = RoomHandler()
message_handler = MessageHandler()

@app.post("/api/rooms/create")
async def create_room():
    room = room_handler.create_room()
    return room.get_state()

@app.get("/api/rooms")
async def get_rooms():
    return room_handler.get_rooms()

@app.get("/api/rooms/{room_id}")
async def get_room(room_id: str):
    room = room_handler.get_room(room_id)
    if room:
        return room.get_state()
    raise HTTPException(status_code=404, detail="Room not found")

@app.get("/api/rooms/{room_id}/board")
async def get_board(room_id: str):
    room = room_handler.get_room(room_id)
    return room.questions_handler.get_board()

@app.get("/api/rooms/{room_id}/questions_categories")
async def get_questions_categories(room_id: str):
    room = room_handler.get_room(room_id)
    return room.questions_handler.get_questions_categories()

@app.get("/api/rooms/{room_id}/questions_categories/{category}")
async def get_category_questions(room_id: str, category: str):
    room = room_handler.get_room(room_id)
    return [question.to_json() for question in room.questions_handler.get_category_questions(category)]

@app.get("/api/rooms/{room_id}/right-order")
async def get_right_order(room_id: str):
    room = room_handler.get_room(room_id)
    return room.questions_handler.get_right_order()

@app.get("/api/rooms/{room_id}/themes")
async def get_themes(room_id: str):
    room = room_handler.get_room(room_id)
    return room.questions_handler.get_themes()

@app.get("/api/rooms/{room_id}/themes/{theme}")
async def get_theme_questions(room_id: str, theme: str):
    room = room_handler.get_room(room_id)
    return [question.to_json() for question in room.questions_handler.get_theme_questions(theme)]

@app.post("/api/rooms/{room_id}/player/score")
async def update_player_score(room_id: str, request: Request):
    body = await request.json()
    player_id = body.get("player_id")
    score = body.get("score")

    if player_id is None or score is None:
        raise HTTPException(status_code=400, detail="player_id and score are required")

    room = room_handler.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.update_player_score(player_id, score)

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    try:
        init_data = await websocket.receive_text()
        player_info = json.loads(init_data)
        player = Player(
            id=player_info.get("id", str(uuid4()),),
            name=player_info.get("name", "Anonymous"),
            websocket=websocket,
        )
    except Exception:
        await websocket.close()
        return

    await websocket.send_text(json.dumps({"initiated-player-id": player.id}))

    room = room_handler.get_room(room_id)
    if not room:
        await websocket.close()
        return

    if player_info.get("admin", False):
        room.set_admin(player)
    elif player_info.get("display", False):
        room.set_display(player)
    else:
        room.add_player(player)

    try:
        room_state = room.get_state()
        await message_handler.broadcast_to_room(room, json.dumps(room_state))

        while True:
            data = await websocket.receive_text()
            await message_handler.handle_message(data, player, room)
    except WebSocketDisconnect:
        if room.admin is not None and room.admin.id == player.id:
            room.admin = None
        elif room.display is not None and room.display.id == player.id:
            room.display = None
        else:
            room.remove_player(player.id)

        if room.admin is None:
            await message_handler.broadcast_to_room(room, json.dumps({"room-deleted": True}))
            room_handler.remove_room(room_id)
        else:
            room_state = room.get_state()
            await message_handler.broadcast_to_room(room, json.dumps(room_state))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)