"""
Handles session management operations, including creation and termination of chat sessions.
"""
import logging
import secrets

from datetime import datetime, timezone

from ..store import SESSIONS, CONNECTIONS
from ..models import Session
from ..schemas import CreateSessionResponse
from ..config import SETTINGS


logger = logging.getLogger(__name__)


def create_new_session():
    """
    Creates a new chat session and stores it in the session store.

    This string generation method includes ceil(n * 4/3) characters, so duplicate sessions are highly improbable.
    The collision check is included for completeness, but in practice, if the session already exists, that likely
    indicates a likely problem with the generation method.

    This is why the log message is a warning and not a debug message.

    Returns:
        CreateSessionResponse: Response to create a new chat session.
    """
    session_id = secrets.token_urlsafe(6)
    if session_id in SESSIONS or session_id in CONNECTIONS:
        logger.warning("Chat session %s already exists", session_id)
        return create_new_session()

    chat_url = f"{SETTINGS.base_chat_url}{session_id}"
    SESSIONS[session_id] = Session(session_id=session_id, last_active=datetime.now(timezone.utc))
    logger.debug("Chat url: %s, Session ID: %s", chat_url, session_id)
    return CreateSessionResponse(session_id=session_id, chat_url=chat_url)


def get_section_by_id(session_id: str) -> Session | None:
    """
    Retrieves a chat session from the session store by its session ID.

    Args:
        session_id: The unique identifier of the chat session to retrieve

    Returns:
        Session or None
    """
    return SESSIONS.get(session_id)


def terminate_session(session_id: str):
    """
    Deletes a chat session from the session store.

    We need to check both the session stores to ensure consistency.

    If the session is not present in either store, or is present in one store but not the other,
    that indicates an issue with the cleanup process.

    Therefore, we log a warning to help identify potential bugs in the session lifecycle management.

    Args:
        session_id: The unique identifier of the chat session to delete.

    Returns:
        None
    """
    in_sessions = session_id in SESSIONS
    in_connections = session_id in CONNECTIONS

    if in_sessions != in_connections:
        logger.warning("Session %s in inconsistent state: SESSIONS=%s, CONNECTIONS=%s",
                     session_id, in_sessions, in_connections)
    elif not in_sessions and not in_connections:
        logger.warning("Session %s not found in either store", session_id)

    SESSIONS.pop(session_id, None)
    CONNECTIONS.pop(session_id, None)
    await cleanup_session_files(session_id)


async def process_message(session_id: str, content: str, sender_id: str) -> Message:
    """
    Processes a message by appending it to the session's message history and updating the last active timestamp.
    The message is also persisted to disk for the duration of the session.

    Args:
        session_id: An existing session identifier to update messages with.
        content: Content of a message to update.
        sender_id: Identifier of the message sender, which will be associated with the message for tracking purposes.

    Returns:
        Message: The message object that was created and stored in the session.
    """
    message = Message(content=content, sender_id=sender_id)
    SESSIONS[session_id].messages.append(message)
    SESSIONS[session_id].last_active = datetime.now(timezone.utc)
    await write_session_to_file(SESSIONS[session_id])
    return message
