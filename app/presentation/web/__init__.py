"""
Web presentation layer for API endpoints.
"""
from app.presentation.web import middleware, handlers, routes, dto, validators

__all__ = [
    "middleware",
    "handlers",
    "routes",
    "dto",
    "validators",
]
