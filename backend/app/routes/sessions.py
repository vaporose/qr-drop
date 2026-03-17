"""
Handles session lifecycle endpoints: creation and termination.

Session creation is the entry point for all chat sessions. The client calls
POST /sessions to receive a session ID, then uses that ID to establish a
WebSocket connection. The session remains active until explicitly terminated
via DELETE /sessions/{session_id} or until the inactivity timeout fires.
"""

import logging
import secrets
from datetime import datetime, timezone

from fastapi import HTTPException

from .router import router
from ..config import SETTINGS
from ..models import Session
from ..schemas import CreateSessionResponse
from ..store import SESSIONS, CONNECTIONS

logger = logging.getLogger(__name__)


@router.post("/sessions")
async def create_session() -> CreateSessionResponse:
    """
    Creates a new chat session and stores it in the session store.

    Returns:
        CreateSessionResponse: The generated session ID and its associated chat URL.
    """
    session_id = secrets.token_urlsafe(6)
    chat_url = f"{SETTINGS.base_chat_url}{session_id}"
    SESSIONS[session_id] = Session(session_id=session_id, last_active=datetime.now(timezone.utc))
    logger.debug("Chat url: %s, Session ID: %s", chat_url, session_id)
    return CreateSessionResponse(session_id=session_id, chat_url=chat_url)


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Session:
    """
    Debugging endpoint for retrieving a chat session from the session store.
    Intentionally only functions when debug is set to true.

    Args:
        session_id: The unique identifier of the chat session to retrieve.

    Returns:
        Session: The chat session object if found, otherwise raises an HTTPException.
    """
    if not SETTINGS.debug:
        raise HTTPException(status_code=404)
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404)
    return SESSIONS[session_id]


@router.delete("/sessions/{session_id}", status_code=204)
async def end_session(session_id: str):
    """
    Ends the session associated with the given chat session ID.

    For logging, we check if the session exists in both the session store and the connections store.
    We want to know if for some reason the session is existing in only one store, or in neither,
    as if this endpoint is being called in that condition, it may mean something wasn't cleaned up correctly.
    Args:
        session_id: The unique identifier of the chat session to end.
    """
    in_sessions = session_id in SESSIONS
    in_connections = session_id in CONNECTIONS

    if in_sessions != in_connections:
        logger.debug("Session %s in inconsistent state: SESSIONS=%s, CONNECTIONS=%s",
                     session_id, in_sessions, in_connections)
    elif not in_sessions and not in_connections:
        logger.debug("Session %s not found in either store", session_id)

    SESSIONS.pop(session_id, None)
    CONNECTIONS.pop(session_id, None)
