"""
Filesystem handlers for session persistence.

Sessions are stored as directories under the configured storage root, with each
session directory containing a session.json file and any file attachments uploaded
during the session. This structure is intentionally temporary — directories are
created when a session is first written and removed entirely on session termination
or inactivity timeout.

The storage root is configured via SETTINGS.session_storage_folder. A leading
slash indicates an absolute path; otherwise the path is relative to the project
root. The directory is created automatically if it does not exist.

All read and write operations are async to avoid blocking the event loop. Directory
creation and deletion are synchronous operations offloaded to a thread pool via
asyncio.to_thread.
"""

import asyncio
import logging
import shutil
from pathlib import Path

import aiofiles

from ..config import SETTINGS
from ..models import Session

logger = logging.getLogger(__name__)


def get_session_dir(session_id: str, create: bool = True) -> Path:
    """
    Gets the directory path for a given chat session ID, creating it if it doesn't exist.

    We are using a directory instead of a single file so that we can store file attachments in the directory.

    Args:
        session_id (str): The unique identifier of the chat session to get the directory for.
        create (bool): Whether to create the directory if it doesn't exist, defaults to True.

    Returns:
        Path instance of the session directory
    """
    base_path = Path(SETTINGS.session_storage_folder)
    session_dir = base_path / session_id
    if not session_dir.exists() and create:
        session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def get_session_file(session_id: str) -> Path:
    """
    Gets the file path for a given chat session ID, creating it if it doesn't exist.

    Args:
        session_id (str): Session identifier for the chat session

    Returns:
        Path instance of the session file
    """
    return get_session_dir(session_id) / "session.json"


async def write_session_to_file(session: Session) -> None:
    """
    Writes the session object to a file.

    Args:
        session (Session): Instance of a Session object to be written to a file in JSON format.
         The session will be serialized using the model_dump_json method,
         which converts the session data into a JSON string representation.
    """
    session_path = get_session_file(session.session_id)
    async with aiofiles.open(session_path, "w") as file:
        await file.write(session.model_dump_json())


async def load_session_from_file(session_id: str) -> Session | None:
    """

    Args:
        session_id (str): Session identifier for the chat session

    Returns:
        Session or None: If the session file exists, it will be read and deserialized into a
        Session object using the model_validate_json method.
        If the session file does not exist, a warning will be logged and None will be returned. Outer calls will handle
        whether this returning None warrants raising an error.
    """
    session_path = get_session_file(session_id)
    if not session_path.exists():
        logger.warning("Session %s not found.", session_id)
        return None
    async with aiofiles.open(session_path, "r") as file:
        return Session.model_validate_json(await file.read())


# noinspection PyTypeChecker
async def cleanup_session_files(session_id: str) -> None:
    """
    Removes the session directory and its contents from the file system.

    Args:
        session_id (str): Session identifier for the chat session

    Returns:
        None
    """
    session_dir = get_session_dir(session_id, create=False)
    if not session_dir.exists():
        logger.warning("Session dir %s does not exist.", session_dir)
        return

    await asyncio.to_thread(shutil.rmtree, session_dir)
    logger.info("Session dir %s deleted.", session_dir)
