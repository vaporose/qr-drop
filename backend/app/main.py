from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .views import add_router


def create_app() -> FastAPI:
    app = FastAPI()
    add_router(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # adjust to match your Vue dev server or prod domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
