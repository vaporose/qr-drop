"""
This module implements the application router and resolves circular
imports caused by the factory pattern.

The module defines a reusable `APIRouter` instance and a function that
attaches it to the FastAPI app while avoiding circular dependencies. Any
route module should import `router` from this module to register its
routes, ensuring proper initialization order when constructing the app.

The application factory should import `add_router` from this module's init
file to register the routes.
"""

from fastapi import APIRouter

router = APIRouter()


def add_router(app):
    """
    This function resolves circular imports that arise from the factory pattern.
    Route modules must import `router` from this file to register their endpoints.
    If those modules were imported at the top level of main.py, they would execute
    before the router is defined, creating a circular dependency. Deferring those
    imports to the body of this function ensures the router exists before any route
    module attempts to import it.

    Args:
        app: The FastAPI application without the nice new router

    Returns:
        The FastAPI application passed in, now with a shiny new router
    """
    from . import websocket, sessions
    app.include_router(router)
    return app
