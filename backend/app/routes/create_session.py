import secrets
import logging

from .router import router
from ..config import SETTINGS
from ..schemas import CreateSessionResponse
from ..store import SESSIONS
from ..models import Session
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@router.post("/create-session")
async def create_session() -> CreateSessionResponse:
    """
    Sets up a new session ID and adds it to the SESSIONS store.

    Returns:
        CreateSessionResponse: The created session ID and the computed chat URL.
    """
    session_id = secrets.token_urlsafe(6)
    chat_url = f"{SETTINGS.base_chat_url}{session_id}"
    SESSIONS[session_id] = Session(session_id=session_id, last_active=datetime.now(timezone.utc))
    logger.debug("Chat url: %s, Session ID: %s", chat_url, session_id)
    return CreateSessionResponse(session_id=session_id, chat_url=chat_url)
