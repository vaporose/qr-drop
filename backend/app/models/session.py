from pydantic import BaseModel
from datetime import datetime

from .message import Message


class Session(BaseModel):
    session_id: str
    last_active: datetime
    participants: set[str]
    messages: list[Message]
