"""
Translate Descriptions Application Package
"""
__version__ = "2.0.0"
__author__ = "Butosklep"

from app.config import settings
from app.core import domain, services, strategies
from app.infrastructure import database, cache, logging, external_api
from app.presentation import web
from app.parsers import json_parser, product_parser
from app.handlers import error_handlers
from app.factories import cache_factory, api_client_factory
from app.shared import constants, decorators, utils

__all__ = [
    "settings",
    "domain",
    "services",
    "strategies",
    "database",
    "cache",
    "logging",
    "external_api",
    "web",
    "json_parser",
    "product_parser",
    "error_handlers",
    "cache_factory",
    "api_client_factory",
    "constants",
    "decorators",
    "utils",
]
