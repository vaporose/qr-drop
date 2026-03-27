from fastapi.testclient import TestClient


def test_websocket_connection(client: TestClient):
    # Create session first
    resp = client.post("/sessions")
    session_id = resp.json()["session_id"]
    
    with client.websocket_connect(f"/ws/sessions/{session_id}") as websocket:
        # First message from the server: {"type": "user_joined", "count": 1}
        data = websocket.receive_json()
        assert data["type"] == "user_joined"
        assert data["count"] == 1

        # Sending and receiving a chat message
        websocket.send_json({"type": "chat_message", "message": "hello websocket"})
        data = websocket.receive_json()
        assert data["type"] == "chat_message"
        assert data["content"] == "hello websocket"


