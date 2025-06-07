import json
from fastapi.testclient import TestClient
from main import app

def test_websocket_connection():
    client = TestClient(app)

    # Create a room
    response = client.post("/api/rooms/create")
    assert response.status_code == 200
    room_data = response.json()
    room_id = room_data["room_id"]

    # Connect to the room
    with client.websocket_connect(f"/ws/{room_id}") as websocket:
        # Send player information
        player_info = {
            "name": "TestPlayer"
        }
        websocket.send_text(json.dumps(player_info))
        
        # Receive the room state after connection
        response = websocket.receive_text()
        room_state = json.loads(response)
        
        # Verify the room state
        assert room_state["room_id"] == room_id
        assert room_state["player_count"] == 1
        assert len(room_state["players"]) == 1
        assert room_state["players"][0]["name"] == "TestPlayer"

def test_multiple_players_connection():
    client = TestClient(app)
    
    # Create a room
    response = client.post("/api/rooms/create")
    room_id = response.json()["room_id"]
    
    # Connect first player
    with client.websocket_connect(f"/ws/{room_id}") as websocket1:
        player1_info = {"name": "Player1"}
        websocket1.send_text(json.dumps(player1_info))
        
        # Get initial room state
        response1 = websocket1.receive_text()
        room_state1 = json.loads(response1)
        assert room_state1["player_count"] == 1
        
        # Connect second player
        with client.websocket_connect(f"/ws/{room_id}") as websocket2:
            player2_info = {"name": "Player2"}
            websocket2.send_text(json.dumps(player2_info))
            
            # Both players should receive updated room state
            response2_1 = websocket1.receive_text()
            response2_2 = websocket2.receive_text()
            
            room_state2_1 = json.loads(response2_1)
            room_state2_2 = json.loads(response2_2)
            
            # Verify room state
            assert room_state2_1 == room_state2_2
            assert room_state2_1["player_count"] == 2
            assert len(room_state2_1["players"]) == 2
            
            player_names = {p["name"] for p in room_state2_1["players"]}
            assert player_names == {"Player1", "Player2"}

def test_admin_connection():
    client = TestClient(app)
    
    # Create a room
    response = client.post("/api/rooms/create")
    room_id = response.json()["room_id"]
    
    # Connect admin player
    with client.websocket_connect(f"/ws/{room_id}") as websocket1:
        admin_info = {"name": "AdminPlayer", "admin": True}
        websocket1.send_text(json.dumps(admin_info))
        
        # Get initial room state
        response1 = websocket1.receive_text()
        room_state1 = json.loads(response1)
        
        # Verify admin is set correctly
        assert room_state1["admin"] is not None
        assert room_state1["admin"]["name"] == "AdminPlayer"
        
        # Connect regular player
        with client.websocket_connect(f"/ws/{room_id}") as websocket2:
            player2_info = {"name": "RegularPlayer"}
            websocket2.send_text(json.dumps(player2_info))
            
            # Both players should receive updated room state
            response2_1 = websocket1.receive_text()
            response2_2 = websocket2.receive_text()
            
            room_state2_1 = json.loads(response2_1)
            room_state2_2 = json.loads(response2_2)
            
            # Verify room states are identical
            assert room_state2_1 == room_state2_2
            
            # Verify room state
            assert room_state2_1["player_count"] == 1  # Admin is not counted in players
            assert len(room_state2_1["players"]) == 1
            assert room_state2_1["admin"]["name"] == "AdminPlayer"
            assert room_state2_1["players"][0]["name"] == "RegularPlayer"