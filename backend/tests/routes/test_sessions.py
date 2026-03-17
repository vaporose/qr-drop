from fastapi.testclient import TestClient
from app.store import SESSIONS, CONNECTIONS
from app.config import SETTINGS


def test_create_session(client: TestClient):
    """
    Test POST /sessions creates a new session and returns the correct response format.
    """
    response = client.post("/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "chat_url" in data
    assert data["session_id"] in SESSIONS
    assert SESSIONS[data["session_id"]].session_id == data["session_id"]


def test_get_session_debug_off(client: TestClient):
    """
    Test GET /sessions/{session_id} returns 404 when debug mode is disabled.
    """
    # Force debug to False
    original_debug = SETTINGS.debug
    SETTINGS.debug = False
    try:
        # Create a session first to ensure it exists
        resp = client.post("/sessions")
        session_id = resp.json()["session_id"]
        
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 404
    finally:
        SETTINGS.debug = original_debug


def test_get_session_debug_on(client: TestClient):
    """
    Test GET /sessions/{session_id} returns session data when debug mode is enabled.
    """
    # Force debug to True
    original_debug = SETTINGS.debug
    SETTINGS.debug = True
    try:
        # Create a session first
        resp = client.post("/sessions")
        session_id = resp.json()["session_id"]
        
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "last_active" in data
    finally:
        SETTINGS.debug = original_debug


def test_get_session_not_found(client: TestClient):
    """
    Test GET /sessions/{session_id} returns 404 when the session does not exist (debug ON).
    """
    # Force debug to True
    original_debug = SETTINGS.debug
    SETTINGS.debug = True
    try:
        response = client.get("/sessions/nonexistent")
        assert response.status_code == 404
    finally:
        SETTINGS.debug = original_debug


def test_end_session(client: TestClient):
    """
    Test DELETE /sessions/{session_id} removes session from SESSIONS and CONNECTIONS.
    """
    # Create a session first
    resp = client.post("/sessions")
    session_id = resp.json()["session_id"]
    
    # Manually add to CONNECTIONS to test cleanup
    CONNECTIONS[session_id] = {}
    
    assert session_id in SESSIONS
    assert session_id in CONNECTIONS
    
    response = client.delete(f"/sessions/{session_id}")
    assert response.status_code == 204
    
    assert session_id not in SESSIONS
    assert session_id not in CONNECTIONS
