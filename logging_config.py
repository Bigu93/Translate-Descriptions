import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL

def setup_logging():
    """
    Configures the root logger with a rotating file handler,
    and adjusts Werkzeug's logger to prevent propagation.
    """
    try:
        logger = logging.getLogger()
        if logger.hasHandlers():
            logger.handlers.clear()

        print("Setting up logging...")
        log_directory = "logs"
        os.makedirs(log_directory, exist_ok=True)

        log_file = os.path.join(log_directory, "app.log")
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000,
            backupCount=6,
            encoding="utf-8"
        )
        handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        logger.addHandler(handler)
        
        # Adjust Werkzeug's logger
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.propagate = False
        werkzeug_logger.setLevel(logging.WARNING)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        werkzeug_logger.addHandler(console_handler)
        
        print("Logging setup complete.")
    except Exception as e:
        print(f"Error during logging setup: {e}")

def get_logger(name="__default__"):
    """
    Returns a logger with the specified name.
    """
    return logging.getLogger(name)
