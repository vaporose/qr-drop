"""
Runtime store for active sessions and live WebSocket connections.

This module holds two in-memory dictionaries that together represent the full
state of all active chat sessions. Neither structure is persisted — both are
intentionally ephemeral and exist only for the lifetime of the running chat session.
When the process is no longer active, or when a session is explicitly cleaned up,
all associated states are removed. This is by design.

SESSIONS maps a session_id to its Session object, which holds session metadata,
message history, and participant identifiers. A Session is created when a client
calls the /create-session endpoint and is removed when the session is terminated
or expires due to inactivity.

CONNECTIONS maps a session_id to a dictionary of active WebSocket handles and
their associated Identity objects. A WebSocket entry is added when a participant
connects and removed when they disconnect. This structure exists separately from
SESSIONS because WebSocket handles are live connection objects — they are not
serializable, not part of the session state, and their lifetime is tied to the
connection rather than the session.

The session_id is the shared key between both structures. Any operation that
removes a session must clean up both SESSIONS and CONNECTIONS together. A session
present in one but not the other is an invalid state.
"""


from .models import Session, Identity
from fastapi import WebSocket

SESSIONS: dict[str, Session] = {}
CONNECTIONS: dict[str, dict[WebSocket, Identity]] = {}
