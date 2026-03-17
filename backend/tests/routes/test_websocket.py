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


def test_websocket_broadcast(client: TestClient):
    # 1. Create a session first
    resp = client.post("/sessions")
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]
    
    # 2. First client joins
    with client.websocket_connect(f"/ws/sessions/{session_id}") as ws1:
        data1 = ws1.receive_json()
        assert data1["type"] == "user_joined"
        assert data1["count"] == 1
        
        # 3. Second client joins
        with client.websocket_connect(f"/ws/sessions/{session_id}") as ws2:
            # ws1 should receive a message about a new user
            data1_new = ws1.receive_json()
            assert data1_new["type"] == "user_joined"
            assert data1_new["count"] == 2
            
            # ws2 should receive the initial message
            data2 = ws2.receive_json()
            assert data2["type"] == "user_joined"
            assert data2["count"] == 2
            
            # 4. Send a message from ws1, ws2 should receive it
            ws1.send_json({"type": "chat_message", "message": "msg from ws1"})
            
            # Both should receive the message
            data_ws2 = ws2.receive_json()
            assert data_ws2["type"] == "chat_message"
            assert data_ws2["content"] == "msg from ws1"
            
            data_ws1 = ws1.receive_json()
            assert data_ws1["type"] == "chat_message"
            assert data_ws1["content"] == "msg from ws1"
