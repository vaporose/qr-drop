from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .views import add_router
from .config import SETTINGS


def create_app() -> FastAPI:
    app = FastAPI()
    add_router(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[SETTINGS.base_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
