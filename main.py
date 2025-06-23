from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from uuid import uuid4

from data_types.message import create_message, Subject, Message
from data_types.player import Player
from handlers.message_handler import send_to_admin, send_to_all_players, handle_message, broadcast_to_room
from handlers.room_handler import RoomHandler

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

room_handler = RoomHandler()

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

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    try:
        init_data = await websocket.receive_text()
        message = create_message(json.loads(init_data))
        if message.subject != Subject.PLAYER_INIT:
            await websocket.close()
            return

        is_admin = message.action == "INIT_ADMIN"
        is_display = message.action == "INIT_DISPLAY"
        player_info = message.content
        player = Player(
            id=player_info.get("player_id", str(uuid4()),),
            name=player_info.get("name", "Anonymous"),
            websocket=websocket,
        )
    except Exception:
        await websocket.close()
        return

    room = room_handler.get_room(room_id)
    if not room:
        await websocket.close()
        return

    if is_admin and room.admin is not None and room.admin.id != player.id:
        response = Message(subject=Subject.PLAYER_INIT, action="INIT_FAILED", content={"REASON": "Room already has an admin."})
        await websocket.send_text(json.dumps(response.to_json()))
        await websocket.close()
        return

    response = Message(subject=Subject.PLAYER_INIT, action="INIT_SUCCESS", content={"PLAYER_ID": player.id})
    await websocket.send_text(json.dumps(response.to_json()))

    try:
        if is_admin:
            room.set_admin(player)
            message = Message(Subject.GAME_STATE, "ROOM_UPDATE", room.get_state())
            await send_to_admin(room, json.dumps(message.to_json()))
        elif is_display:
            room.set_display(player)
        else:
            player = room.add_player(player)
            room_state = room.get_state()
            room_state["player_id"] = player.id
            room_state["player_name"] = player.name
            message = Message(Subject.GAME_STATE, "ROOM_UPDATE", room_state)
            await send_to_admin(room, json.dumps(message.to_json()))
            await send_to_all_players(room, player, json.dumps(message.to_json()))

        while True:
            data = await websocket.receive_text()
            await handle_message(data, player, room, room_handler)
    except WebSocketDisconnect:
        if room.admin is not None and room.admin.id == player.id:
            return
        elif room.display is not None and room.display.id == player.id:
            room.display = None
        else:
            room_state = room.get_state()
            message = Message(Subject.GAME_STATE, "ROOM_UPDATE", room_state)
            await broadcast_to_room(room, player, json.dumps(message.to_json()))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)