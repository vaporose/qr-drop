"""
Handles WebSocket connections and broadcasting functionalities.

This module provides mechanisms to register WebSocket identities for sessions and to broadcast
messages to all connected clients within a specific session.
"""
import asyncio
import logging

from ..models import Identity, setup_identity
from ..store import SESSIONS, CONNECTIONS
from ..config import SETTINGS
from fastapi import WebSocket

logger = logging.getLogger(__name__)


def register_websocket_identity(websocket: WebSocket, session_id: str) -> Identity:
    """

    Args:
        websocket: WebSocket connection for this session
        session_id: Associated session ID

    Returns:
        An identity object associated with the WebSocket connection.
        This identity is used to track the user's session and WebSocket connection.
    """
    if session_id not in CONNECTIONS:
        CONNECTIONS[session_id] = {}

    if websocket not in CONNECTIONS[session_id]:
        identity = setup_identity(websocket)
        SESSIONS[session_id].participants.add(identity)
        CONNECTIONS[session_id][websocket] = identity
        return identity

    identity = CONNECTIONS[session_id].get(websocket)
    if identity is None:
        raise ValueError(f"WebSocket present in CONNECTIONS[{session_id}] but has no associated identity")
    return identity


async def broadcast(session_id: str, payload: dict):
    """
    Broadcasts a JSON payload to all connected clients in a given session.

    This function iterates over all clients connected to the specified session and sends
    the provided JSON payload to each client asynchronously.

    Args:
        session_id (str): The session identifier for the group of connected clients to
            which the payload will be broadcasted.
        payload (dict): The JSON payload to be sent to all clients in the specified session.
    """
    for client in CONNECTIONS[session_id]:
        await client.send_json(payload)


async def heartbeat(websocket: WebSocket, session_id: str):
    """
    Sends periodic heartbeat messages to the client to ensure the connection is alive.

    Args:
        websocket: The WebSocket connection instance.
        session_id: Session ID associated with this websocket.
    """
    while True:
        await asyncio.sleep(SETTINGS.HEARTBEAT_INTERVAL)
        try:
            await asyncio.wait_for(websocket.send_json({"type": "ping"}), timeout=SETTINGS.HEARTBEAT_TIMEOUT)
        except asyncio.TimeoutError:
            logger.warning("Heartbeat timeout for session %s, closing connection", session_id)
            await websocket.close(code=4008, reason="Heartbeat timeout")
            break
        except Exception:
            break


def create_heartbeat_task(websocket: WebSocket, session_id: str):
    """
    Creates and returns an asynchronous task that manages a heartbeat for
    maintaining the connection and session.

    The reason we're doing this rather than just directly using the asyncio.create_task
    is for testing purposes. It's a whole lot easier to mock the output of a custom
    function than it is to go mocking the asyncio event loop directly.

    Args:
        websocket: The WebSocket connection instance used for communication.
        session_id: The unique identifier corresponding to the active session.

    Returns:
        asyncio.Task: A task instance that runs the heartbeat coroutine.
    """
    return asyncio.create_task(heartbeat(websocket, session_id))
