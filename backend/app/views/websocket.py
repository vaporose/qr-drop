from .router import router
from fastapi import WebSocket

SESSIONS: dict[str, list[WebSocket]] = {}


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    SESSIONS[session_id].append(websocket)
    # if len(SESSIONS[session_id]) == 2:
    #     await websocket.close(code=1008, reason="Max connections for this session ID reached")
    #     return

    await websocket.accept()
    # Broadcast user_joined to all
    for client in SESSIONS[session_id]:
        await client.send_json({"type": "user_joined", "count": len(SESSIONS[session_id])})


    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to other clients in the same session
            for client in SESSIONS[session_id]:
                await client.send_text(data)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        SESSIONS[session_id].remove(websocket)
