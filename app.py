"""
Main application entry point using new architecture.
"""
import threading
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from app.config.settings import get_allowed_origins
from app.infrastructure.logging.structured_logger import get_logger
from app.infrastructure.database.connection_pool import get_connection_pool
from app.infrastructure.database.token_repository import TokenRepository
from app.infrastructure.database.bearer_repository import BearerRepository
from app.presentation.web.routes import (
    create_product_routes,
    create_translation_routes,
    create_auth_routes,
)
from app.presentation.web.handlers import (
    ProductHandlers,
    TranslationHandlers,
    AuthHandlers,
)
from app.core.services import (
    ProductService,
    TranslationService,
    AuthService,
    TokenService,
)
from app.core.strategies.openai_strategy import OpenAIStrategy
from app.factories.api_client_factory import create_products_client
from app.factories.cache_factory import get_cache_provider
from app.config.settings import (
    get_base_url,
    get_client_username,
    get_client_secret,
    get_openai_api_key,
    get_openai_model,
)


logger = get_logger("app")
logger_files = get_logger("static_files")

# Create Flask app
app = Flask(__name__)

# Track initialization status for lazy loading
_services_initialized = False
_initialization_lock = threading.Lock()

# Configure CORS
allowed_origins = get_allowed_origins()
CORS(app, resources={r"/*": {"origins": allowed_origins}})

# Configure static file caching
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 86400


def initialize_services():
    """
    Initialize all services with dependency injection.
    
    Returns:
        Tuple of (products_client, product_service, translation_service, auth_service, token_service)
    """
    # Create products client
    base_url = get_base_url()
    client_username = get_client_username()
    client_secret = get_client_secret()
    products_client = create_products_client(base_url, client_username, client_secret)

    # Create cache
    cache = get_cache_provider()

    # Create translation strategy
    openai_api_key = get_openai_api_key()
    openai_model = get_openai_model()
    translation_strategy = OpenAIStrategy(api_key=openai_api_key, model=openai_model)

    # Get logger for services
    service_logger = get_logger("services")

    # Create services
    product_service = ProductService(products_client)
    translation_service = TranslationService(translation_strategy, cache, service_logger)
    
    # Initialize database-dependent services
    connection_pool = get_connection_pool()
    token_repository = TokenRepository(connection_pool)
    bearer_repository = BearerRepository(connection_pool)
    
    # Create auth and token services with dependencies
    token_service = TokenService(token_repository, service_logger)
    auth_service = AuthService(bearer_repository, service_logger)

    return products_client, product_service, translation_service, auth_service, token_service


def register_blueprints():
    """
    Register all route blueprints.
    Uses lazy initialization - only initializes services once on first request.
    """
    global _services_initialized
    
    # Return early if already initialized
    if _services_initialized:
        return
    
    # Use lock to prevent race conditions during initialization
    with _initialization_lock:
        # Double-check pattern in case another thread initialized while waiting for lock
        if _services_initialized:
            return
        
        try:
            logger.info("Initializing services...")
            products_client, product_service, translation_service, auth_service, token_service = initialize_services()

            # Create handlers
            product_handlers = ProductHandlers(products_client)
            translation_handlers = TranslationHandlers(translation_service)
            auth_handlers = AuthHandlers(auth_service, token_service)

            # Create routes
            product_routes = create_product_routes(product_handlers)
            translation_routes = create_translation_routes(translation_handlers)
            auth_routes = create_auth_routes(auth_handlers)

            # Register blueprints
            app.register_blueprint(product_routes)
            app.register_blueprint(translation_routes)
            app.register_blueprint(auth_routes)

            _services_initialized = True
            logger.info("All blueprints registered successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise


def register_error_handlers():
    """
    Register global error handlers.
    """
    from app.handlers.error_handlers import handle_generic_error
    from werkzeug.exceptions import NotFound

    @app.errorhandler(NotFound)
    def handle_not_found(e):
        """Handle 404 errors specifically."""
        logger.warning(f"404 Not Found: {request.path}")
        return jsonify(error="Not Found", path=request.path), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all uncaught exceptions."""
        logger.error(f"Uncaught exception: {e}")
        return handle_generic_error(e)


def register_request_logging():
    """
    Register request/response logging hooks.
    """
    @app.before_request
    def log_request():
        """Log incoming requests."""
        if app.url_map and request.path.startswith("/static/"):
            logger_files.info(f"Static file request: {request.path}")

    @app.after_request
    def log_response(response):
        """Log outgoing responses."""
        if request.path.startswith("/static"):
            logger_files.info(
                f"Static file request completed: {request.path}, "
                f"Status: {response.status_code}"
            )
        return response


# Register error handlers and request logging (these are safe to initialize at module level)
register_error_handlers()
register_request_logging()

# Add before_request handler for lazy initialization
@app.before_request
def ensure_initialized():
    """
    Ensure services are initialized before processing requests.
    This implements lazy initialization pattern for Passenger compatibility.
    """
    # Skip initialization for static files and health check endpoints
    if request.path.startswith("/static/") or request.path in ["/health", "/", "/favicon.ico"]:
        return
    
    # Initialize services on first non-static request
    register_blueprints()


@app.route("/")
def hello_world():
    """Health check endpoint."""
    return "Hello Butosklep!"


@app.route("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "translate-descriptions"}


@app.route("/favicon.ico")
def favicon():
    """Handle favicon requests to prevent 404 errors."""
    return "", 204


if __name__ == "__main__":
    logger.info("Starting Translate Descriptions application")
    app.run(host="0.0.0.0", port=5000)
