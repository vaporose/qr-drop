from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.routes.websocket import websocket_endpoint


@pytest.fixture
def mock_websocket():
    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    websocket.receive_json = AsyncMock()
    websocket.close = AsyncMock()
    websocket.headers = {"user-agent": "Mozilla/5.0"}
    return websocket


@pytest.fixture
def clean_store(monkeypatch):
    sessions = {}
    connections = {}
    monkeypatch.setattr("app.routes.websocket.SESSIONS", sessions)
    monkeypatch.setattr("app.routes.websocket.CONNECTIONS", connections)
    return sessions, connections


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


@pytest.mark.asyncio
async def test_pong_messages_are_ignored(mock_websocket, clean_store):
    sessions, connections = clean_store
    session_id = "test123"
    from datetime import datetime, timezone
    from app.models import Session
    sessions[session_id] = Session(
        session_id=session_id,
        last_active=datetime.now(timezone.utc)
    )

    mock_websocket.receive_json = AsyncMock(side_effect=[
        {"type": "pong"},
        Exception("stop loop")
    ])

    with patch("app.routes.websocket.create_heartbeat_task"):
        try:
            await websocket_endpoint(mock_websocket, session_id)
        except Exception:
            pass

    mock_websocket.send_json.assert_not_called()


@pytest.mark.asyncio
async def test_heartbeat_task_cancelled_on_disconnect(mock_websocket, clean_store):
    sessions, connections = clean_store
    session_id = "test123"
    from datetime import datetime, timezone
    from app.models import Session, Identity
    from starlette.websockets import WebSocketDisconnect

    sessions[session_id] = Session(
        session_id=session_id,
        last_active=datetime.now(timezone.utc)
    )

    mock_websocket.accept = AsyncMock()
    mock_websocket.receive_json = AsyncMock(
        side_effect=WebSocketDisconnect(code=1005, reason="")
    )

    mock_identity = Identity(unique_identifier="abc123", display_name="Test Browser")
    mock_task = MagicMock()

    with patch("app.routes.websocket.create_heartbeat_task", return_value=mock_task), \
            patch("app.routes.websocket.register_websocket_identity", return_value=mock_identity), \
            patch("app.routes.websocket.broadcast", new_callable=AsyncMock):
        await websocket_endpoint(mock_websocket, session_id)

    mock_task.cancel.assert_called_once()
