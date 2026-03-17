"""
Handles session lifecycle endpoints: creation and termination.

Session creation is the entry point for all chat sessions. The client calls
POST /sessions to receive a session ID, then uses that ID to establish a
WebSocket connection. The session remains active until explicitly terminated
via DELETE /sessions/{session_id} or until the inactivity timeout fires.
"""

import secrets
import logging

from .router import router
from ..config import SETTINGS
from ..schemas import CreateSessionResponse
from ..store import SESSIONS
from ..models import Session
from datetime import datetime, timezone

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
