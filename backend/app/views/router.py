from fastapi import APIRouter

router = APIRouter()

def add_router(app):
    from . import home, websocket, create_session
    app.include_router(router)  # Include the router in the FastAPI app
    return app
