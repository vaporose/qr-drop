"""
Provides functionality to define and manage chat user identity based on websocket connections.

"Identity" is used instead of "User" as it better represents the concept of a chat participant,
which may not be different users but rather different devices or browser sessions.
Each Identity has a unique identifier and a display name derived from the user agent string.

This module defines the `Identity` class to represent one entity in a chat and includes
a utility function `setup_identity` to create an `Identity` instance using websocket headers.
"""

import user_agents

from pydantic import BaseModel, ConfigDict
from fastapi import WebSocket
from uuid import uuid4


class Identity(BaseModel):
    model_config = ConfigDict(frozen=True)

    unique_identifier: str
    display_name: str

    def __hash__(self):
        return hash(self.unique_identifier)

    def __eq__(self, other):
        return isinstance(other, Identity) and self.unique_identifier == other.unique_identifier


def setup_identity(websocket: WebSocket) -> Identity:
    """
    Create an Identity object for a user based on their websocket connection.

    Args:
        websocket: Websocket the user is connected to

    Returns:
        Identity: An Identity object representing the user, with a unique identifier
         and display name derived from the user agent string.
    """
    user_agent = websocket.headers.get("user-agent", "Unknown device")
    ua = user_agents.parse(user_agent)
    name_from_agent = f"{ua.browser.family} on {ua.os.family}"
    unique_identifier = str(uuid4())
    identity = Identity(unique_identifier=unique_identifier, display_name=name_from_agent)
    return identity
