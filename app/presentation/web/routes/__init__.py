"""
Route blueprints for API endpoints.
"""
from app.presentation.web.routes.product_routes import create_product_routes
from app.presentation.web.routes.translation_routes import create_translation_routes
from app.presentation.web.routes.auth_routes import create_auth_routes

__all__ = [
    "create_product_routes",
    "create_translation_routes",
    "create_auth_routes",
]
