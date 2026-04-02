"""
Handles WebSocket connections and broadcasting functionalities.

This module provides mechanisms to register WebSocket identities for sessions and to broadcast
messages to all connected clients within a specific session.
"""
import asyncio
import logging

from datetime import datetime, timedelta, timezone

from ..models import Identity, setup_identity
from ..store import SESSIONS, CONNECTIONS
from ..config import SETTINGS
from fastapi import WebSocket
from enum import Enum

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """
    Represents the states of a session for a system.

    This enumeration defines the possible states that a session can reside in:
    active, inactive, or closed. This helps the heartbeat function handle how
    to interact with sessions.

    Attributes:
        ACTIVE (SessionState): There have been messages sent within the timeout period.
        INACTIVE (SessionState): No messages have been sent without the timeout period.
        CLOSED (SessionState): The session wasn't found in the session store, assumed closed.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"


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


def check_inactivity(session_id: str) -> SessionState:
    """
    Checks if a session has been inactive for longer than the configured timeout.

    This function compares the current time with the last active timestamp of the session.
    If the difference exceeds the inactivity timeout defined in SETTINGS, it returns True,
    indicating that the session should be considered inactive.

    If the session is no longer in SESSIONS, it returns False, as the session has been closed.

    Args:
        session_id (str): The unique identifier of the chat session to check for inactivity.
    Returns:
        bool: True if the session is inactive, False otherwise.
    """
    current_time = datetime.now(timezone.utc)
    last_active_time = SESSIONS[session_id].last_active if session_id in SESSIONS else None
    if last_active_time is None:
        return SessionState.CLOSED
    is_inactive = (current_time - last_active_time) > timedelta(seconds=SETTINGS.INACTIVITY_TIMEOUT)
    if is_inactive:
        return SessionState.INACTIVE
    else:
        return SessionState.ACTIVE


async def close_websocket(websocket: WebSocket, code: int, reason: str, session_id: str):
    """
    Wraps an attempt to close websockets in its own try/except clause so we can gracefully handle exceptions.

    Args:
        websocket: The websocket being closed
        code: Code to send on close
        reason: Reason for closing the websocket
        session_id: Session ID associated with the websocket, for debugging
    """
    try:
        await websocket.close(code=code, reason=reason)
    except Exception:
        logger.warning("Closing socket on disconnect error for session %s", session_id, exc_info=True)


async def heartbeat(websocket: WebSocket, session_id: str):
    """
    Sends periodic heartbeat messages to the client to ensure the connection is alive.

    Args:
        websocket: The WebSocket connection instance.
        session_id: Session ID associated with this websocket.
    """
    while True:
        await asyncio.sleep(SETTINGS.HEARTBEAT_INTERVAL)
        session_state = check_inactivity(session_id)
        if session_state == SessionState.CLOSED:
            logger.warning("Session %s has been already closed, closing connection", session_id)
            await close_websocket(websocket, code=4004, reason="Session not found or expired", session_id=session_id)
            break
        elif session_state == SessionState.ACTIVE:
            try:
                await asyncio.wait_for(websocket.send_json({"type": "ping"}), timeout=SETTINGS.HEARTBEAT_TIMEOUT)
            except asyncio.TimeoutError:
                logger.warning("Heartbeat timeout for session %s, closing connection", session_id)
                await close_websocket(websocket, code=4008, reason="Heartbeat timeout", session_id=session_id)
                break
            except Exception:
                break
        elif session_state == SessionState.INACTIVE:
            logger.debug("Session %s is inactive, closing connection", session_id)
            await close_websocket(websocket, code=4008, reason="Session timeout", session_id=session_id)
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
