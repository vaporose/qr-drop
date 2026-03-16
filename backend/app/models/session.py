"""
This module manages session creation and representation, including handling
participants and messages within a session.

The `Session` model defines the structure of a session, which includes
details such as a unique session ID, last active timestamp, participants,
and messages. The `create_session` function helps initialize a session
object.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .identity import Identity
from .message import Message


class Session(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: str
    last_active: datetime
    participants: set[Identity] = set()
    messages: list[Message] = []

