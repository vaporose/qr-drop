from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone


class Message(BaseModel):
    content: str
    sender_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uid: str = Field(default_factory=lambda: str(uuid4()))
