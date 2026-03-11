import user_agents
import logging

from .router import router
from fastapi import WebSocket

SESSIONS: dict[str, dict[WebSocket, str]] = {}

logger = logging.getLogger(__name__)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {}

    user_agent = websocket.headers.get("user-agent", "Unknown device")
    ua = user_agents.parse(user_agent)
    identity = f"{ua.browser.family} on {ua.os.family}"

    await websocket.accept()
    SESSIONS[session_id][websocket] = identity

    for client in SESSIONS[session_id]:
        await client.send_json({
            "type": "user_joined",
            "count": len(SESSIONS[session_id]),
            "identity": identity
        })

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "chat_message":
                for client in SESSIONS[session_id]:
                    await client.send_json({
                        "type": "chat_message",
                        "client_id": identity,
                        "message": data["message"]
                    })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        SESSIONS[session_id].pop(websocket, None)
