import json
import time

from data_types.message import create_message, Message, Subject
from data_types.player import Player
from data_types.room import Room


async def handle_message(raw, player, room):
    data = json.loads(raw)
    message = create_message(data)

    # Display
    if room.display is not None and player.id == room.display.id:
        print(f"ERROR Display: {message}")
        return

    # Admin
    elif room.admin is not None and player.id == room.admin.id:
        await handle_admin_client_message(message, room, player)
        return

    # Player
    else:
        await handle_player_client_message(message, room, player)
        return


async def send_to_admin(room: Room, message: str):
    await room.admin.websocket.send_text(message)

async def send_to_display(room: Room, message: str):
    if room.display is not None:
        await room.display.websocket.send_text(message)

async def send_to_player(room: Room, player_id: str, message: str):
    player = room.players.get(player_id)
    if player:
        await player.websocket.send_text(message)

async def send_to_all_players(room: Room, self_player: Player, message: str):
    for player in room.players.values():
        if player.id != self_player.id:
            await player.websocket.send_text(message)

async def broadcast_to_room(room: Room, player: Player, message: str):
        await send_to_admin(room, message)
        await send_to_display(room, message)
        await send_to_all_players(room, player, message)

async def handle_player_client_message(message: Message, room: Room, player: Player):
    if message.subject == Subject.BUZZER and message.action == "ADD":
        response = Message(subject=Subject.BUZZER, action=message.action, content={"PLAYER_NAME": player.name, "TIME": time.time()})
        await send_to_admin(room, json.dumps(response.to_json()))
        return

    if message.subject == Subject.PLAYER_NAME and message.action == "UPDATE":
        player.name = message.content["PLAYER_NAME"]
        message = Message(Subject.GAME_STATE, "ROOM_UPDATE", room.get_state())
        await send_to_player(room, player.id, json.dumps(message.to_json()))
        await broadcast_to_room(room, player, json.dumps(message.to_json()))
        return

    if message.subject == Subject.PLAYER_NUMBER_ANSWER and message.action == "UPDATE":
        player.current_answer = message.content["VALUE"]
        return

    if message.subject == Subject.RIGHT_ORDER:
        if message.action == "REQUEST":
            response = Message(subject=Subject.RIGHT_ORDER, action=message.action, content=room.last_right_order)
            await send_to_player(room, player.id, json.dumps(response.to_json()))
            return
        if message.action == "PLAYER_ANSWER":
            message.content["PLAYER_NAME"] = player.name
            await send_to_display(room, json.dumps(message.to_json()))
            return

    print(f"Unknown message: {message}")


async def handle_admin_client_message(message: Message, room: Room, player: Player):
    if message.subject == Subject.GAME_STATE and message.action == "START":
        room.started = True
        await send_to_display(room, json.dumps(message.to_json()))
        await send_to_all_players(room, player, json.dumps(message.to_json()))
        return

    if message.subject == Subject.BUZZER and message.action == "RESET":
        await send_to_all_players(room, player, json.dumps(message.to_json()))
        return

    if message.subject == Subject.RIGHT_ORDER:
        if message.action == "SEND":
            room.last_right_order = message.content
            await send_to_all_players(room, player, json.dumps(message.to_json()))
            await send_to_display(room, json.dumps(message.to_json()))
            return
        if message.action == "SHOW_ANSWER":
            await send_to_display(room, json.dumps(message.to_json()))
            return
        if message.action == "REQUEST_PLAYERS_ANSWER":
            clear_players_answer = Message(subject=Subject.RIGHT_ORDER, action="CLEAR_PLAYERS_ANSWER", content={})
            await send_to_display(room, json.dumps(clear_players_answer.to_json()))
            await send_to_all_players(room, player, json.dumps(message.to_json()))
            return

    if message.subject == Subject.TIMER:
        await send_to_display(room, json.dumps(message.to_json()))
        return

    if message.subject == Subject.PLAYER_NUMBER_ANSWER and message.action == "SHOW":
        message.content["PLAYERS"] = room.get_state()["players"]
        await send_to_display(room, json.dumps(message.to_json()))
        return

    if message.subject == Subject.PLAYER_SCORE:
        if message.action == "SHOW":
            message.content["PLAYERS"] = room.get_state()["players"]
            await send_to_display(room, json.dumps(message.to_json()))
            return
        if message.action == "UPDATE":
            room.update_player_score(message.content["PLAYER_ID"], message.content["SCORE"])
            return

    if message.subject == Subject.QUESTION:
        if message.action == "SEND":
            reset_buzzer = Message(subject=Subject.BUZZER, action="RESET", content={})
            await send_to_all_players(room, player, json.dumps(reset_buzzer.to_json()))

            await send_to_display(room, json.dumps(message.to_json()))
            await send_to_all_players(room, player, json.dumps(message.to_json()))
            return
        if message.action == "SHOW_ANSWER":
            await send_to_display(room, json.dumps(message.to_json()))
            return

    if message.subject == Subject.BOARD:
        if message.action == "UPDATE":
            await send_to_display(room, json.dumps(message.to_json()))
            return

    if message.subject == Subject.THEMES:
        if message.action == "SHOW":
            await send_to_display(room, json.dumps(message.to_json()))
            return
        if message.action == "ANSWERS":
            await send_to_display(room, json.dumps(message.to_json()))
            return

    print(f"Unknown message: {message}")

