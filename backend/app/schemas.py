from pydantic import BaseModel


class CreateSessionResponse(BaseModel):
    session_id: str
    chat_url: str
