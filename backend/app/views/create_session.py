from .router import router
from ..config import SETTINGS
from ..schemas import CreateSessionResponse
from fastapi import FastAPI, WebSocket
import secrets



@router.post("/create-session")
async def create_session() -> CreateSessionResponse:
    session_id = secrets.token_urlsafe(6)
    chat_url = f"{SETTINGS['BASE_CHAT_URL']}{session_id}"
    print("Chat url: ", chat_url, "Session id: ", session_id)
    return CreateSessionResponse(session_id=session_id, chat_url=chat_url)
