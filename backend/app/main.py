import logging
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .views import add_router
from .config import SETTINGS


def create_app() -> FastAPI:
    logging.config.dictConfig(dict(SETTINGS.logging))

    app = FastAPI(
        title=SETTINGS.title,
        debug=SETTINGS.debug,
    )
    add_router(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[SETTINGS.base_frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
