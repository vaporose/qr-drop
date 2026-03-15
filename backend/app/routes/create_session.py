import secrets
import logging

from .router import router
from ..config import SETTINGS
from ..schemas import CreateSessionResponse

logger = logging.getLogger(__name__)


@router.post("/create-session")
async def create_session() -> CreateSessionResponse:
    session_id = secrets.token_urlsafe(6)
    chat_url = f"{SETTINGS.base_chat_url}{session_id}"
    logger.debug("Chat url: %s, Session ID: %s", chat_url, session_id)
    return CreateSessionResponse(session_id=session_id, chat_url=chat_url)
