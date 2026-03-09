from fastapi.testclient import TestClient


def test_websocket_connection(client: TestClient):
    session_id = "test-session"
    with client.websocket_connect(f"/ws/{session_id}") as websocket:
        # First message from the server: {"type": "user_joined", "count": 1}
        data = websocket.receive_json()
        assert data["type"] == "user_joined"
        assert data["count"] == 1

        # Sending and receiving a message
        test_message = "hello websocket"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        assert data == test_message


def test_websocket_broadcast(client: TestClient):
    session_id = "broadcast-session"
    
    # First client joins
    with client.websocket_connect(f"/ws/{session_id}") as ws1:
        data1 = ws1.receive_json()
        assert data1["count"] == 1
        
        # Second client joins
        with client.websocket_connect(f"/ws/{session_id}") as ws2:
            # ws1 should receive a message about a new user
            data1_new = ws1.receive_json()
            assert data1_new["count"] == 2
            
            # ws2 should receive the initial message
            data2 = ws2.receive_json()
            assert data2["count"] == 2
            
            # Send a message from ws1, ws2 should receive it
            ws1.send_text("msg from ws1")
            assert ws2.receive_text() == "msg from ws1"
            # ws1 also receives its own message due to backend implementation
            assert ws1.receive_text() == "msg from ws1"
