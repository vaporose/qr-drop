import logging

from fastapi import WebSocket

from .router import router
from ..handlers import register_websocket_identity, broadcast, process_message
from ..store import SESSIONS, CONNECTIONS

logger = logging.getLogger(__name__)


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Handles WebSocket connections and broadcasting functionalities.

    Workflow:
        Checks first if the session id is valid. It should have already been set in the session store.
        Registers the WebSocket identity for the session.
        Broadcasts a user joined message to all clients in the session.
        Listens for incoming chat messages and broadcasts them to all clients in the session.

    Args:
        websocket: The WebSocket connection instance.
        session_id: The session identifier for the group of connected clients.
    """
    if session_id not in SESSIONS:
        await websocket.close(code=4004, reason="Session not found or expired")
        return

    await websocket.accept()
    try:
        identity = register_websocket_identity(websocket, session_id)

        await broadcast(session_id=session_id, payload={
                "type": "user_joined",
                "count": len(CONNECTIONS[session_id]),
                "identity": identity.model_dump_json()
            })

        while True:
            data = await websocket.receive_json()
            if data["type"] == "chat_message":
                message = await process_message(session_id=session_id,
                                                content=data["message"],
                                                sender_id=identity.unique_identifier)
                await broadcast(session_id=session_id, payload={
                    "type": "chat_message",
                    "identity": identity.model_dump(mode="json"),
                    **message.model_dump(mode="json")
                })

    except ValueError:
        logger.error("Connection state corrupted for session %s", session_id)
        await websocket.close(code=4011, reason="Internal connection error")
        return

    except Exception as err:
        logger.error("Unhandled WebSocket error: %s", err, exc_info=True)
        await websocket.close(code=4000, reason="Internal server error")
        return
    finally:
        CONNECTIONS[session_id].pop(websocket, None)
        return
