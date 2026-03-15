from fastapi import WebSocket


SESSIONS: dict[str, dict[WebSocket, str]] = {}
