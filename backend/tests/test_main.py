from fastapi.testclient import TestClient


def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_create_session(client: TestClient):
    response = client.post("/create-session")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "chat_url" in data
    assert data["chat_url"].endswith(data["session_id"])
