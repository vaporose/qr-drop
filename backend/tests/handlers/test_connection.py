import pytest
from unittest.mock import AsyncMock, MagicMock
from app.handlers.connection import register_websocket_identity, broadcast
from app.models import Identity, Session
from datetime import datetime


@pytest.fixture
def mock_websocket():
    websocket = MagicMock()
    websocket.headers = {"user-agent": "Mozilla/5.0"}
    websocket.send_json = AsyncMock()
    return websocket


@pytest.fixture
def clean_store(monkeypatch):
    sessions = {}
    connections = {}
    monkeypatch.setattr("app.handlers.connection.SESSIONS", sessions)
    monkeypatch.setattr("app.handlers.connection.CONNECTIONS", connections)
    return sessions, connections


def test_register_websocket_identity_new_session(mock_websocket, clean_store):
    sessions, connections = clean_store
    session_id = "session1"
    sessions[session_id] = Session(session_id=session_id, last_active=datetime.now())
    
    identity = register_websocket_identity(mock_websocket, session_id)
    
    assert session_id in connections
    assert mock_websocket in connections[session_id]
    assert connections[session_id][mock_websocket] == identity
    assert identity in sessions[session_id].participants


def test_register_websocket_identity_existing_websocket(mock_websocket, clean_store):
    sessions, connections = clean_store
    session_id = "session1"
    sessions[session_id] = Session(session_id=session_id, last_active=datetime.now())
    
    # First registration
    identity1 = register_websocket_identity(mock_websocket, session_id)
    
    # Second registration with the same websocket
    identity2 = register_websocket_identity(mock_websocket, session_id)
    
    assert identity1 == identity2
    assert len(sessions[session_id].participants) == 1


@pytest.mark.asyncio
async def test_broadcast(mock_websocket, clean_store):
    sessions, connections = clean_store
    session_id = "session1"
    connections[session_id] = {mock_websocket: MagicMock(spec=Identity)}

    payload = {"message": "hello"}
    await broadcast(session_id, payload)

    mock_websocket.send_json.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_heartbeat_terminates_inactive_session(mock_websocket, monkeypatch):
    """An inactive session must be cleaned up from the stores, not just have its socket closed."""
    from app.handlers import connection

    session_id = "inactive1"
    mock_websocket.close = AsyncMock()

    # Skip the real sleep and force the inactive branch deterministically.
    monkeypatch.setattr(connection.asyncio, "sleep", AsyncMock())
    monkeypatch.setattr(connection, "check_inactivity", lambda sid: connection.SessionState.INACTIVE)
    terminate_mock = AsyncMock()
    monkeypatch.setattr(connection, "terminate_session", terminate_mock)

    await connection.heartbeat(mock_websocket, session_id)

    terminate_mock.assert_awaited_once_with(session_id)
    mock_websocket.close.assert_awaited_once()
