"""
Configuration management for Translate-Descriptions application.

This module provides centralized configuration management with environment-based
settings, validation, and singleton pattern.
"""

import os
import logging
from dataclasses import dataclass, field
from dotenv import load_dotenv
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    loaded = load_dotenv()
    if loaded:
        logger.info("Environment variables loaded from .env file")
    else:
        logger.warning("No .env file found or file is empty")
except Exception as e:
    logger.error(f"Error loading .env file: {e}")


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration."""
    host: str
    database: str
    user: str
    password: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30


@dataclass(frozen=True)
class OpenAIConfig:
    """OpenAI configuration."""
    api_key: str
    model: str
    timeout: int = 30


@dataclass(frozen=True)
class IdoSellConfig:
    """IdoSell API configuration."""
    client_username: str
    client_secret: str
    base_url: str
    api_version: str = "v6"
    ssl_verify: bool = True


@dataclass(frozen=True)
class VIESConfig:
    """VIES configuration."""
    wsdl_url: str


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    log_dir: str = "logs"
    max_bytes: int = 10000
    backup_count: int = 3


@dataclass(frozen=True)
class CacheConfig:
    """Cache configuration."""
    enabled: bool = True
    ttl: int = 3600  # 1 hour
    backend: str = "memory"  # memory, redis


@dataclass(frozen=True)
class Settings:
    """Application settings (singleton).
    
    Centralized configuration management with validation.
    All settings are frozen (immutable) after initialization.
    """
    
    # Database
    database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        database=os.getenv("DB_NAME", "translate_descriptions"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", "")
    ))
    
    # OpenAI
    openai: OpenAIConfig = field(default_factory=lambda: OpenAIConfig(
        api_key=os.getenv("O_SECRET", ""),
        model=os.getenv("MODEL", "gpt-4"),
        timeout=int(os.getenv("OPENAI_TIMEOUT", "30") or "30")
    ))
    
    # IdoSell
    ido_sell: IdoSellConfig = field(default_factory=lambda: IdoSellConfig(
        client_username=os.getenv("IDOSELL_CLIENT_USERNAME", ""),
        client_secret=os.getenv("IDOSELL_CLIENT_SECRET", ""),
        base_url=os.getenv("IDOSELL_BASE_URL", ""),
        api_version=os.getenv("API_VERSION", "v6"),
        ssl_verify=os.getenv("SSL_VERIFY", "true").lower() == "true"
    ))
    
    # VIES
    vies: VIESConfig = field(default_factory=lambda: VIESConfig(
        wsdl_url=os.getenv("VIES", "https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl")
    ))
    
    # Logging
    logging: LoggingConfig = field(default_factory=lambda: LoggingConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        log_dir=os.getenv("LOG_DIR", "logs"),
        max_bytes=int(os.getenv("LOG_MAX_BYTES", "10000") or "10000"),
        backup_count=int(os.getenv("LOG_BACKUP_COUNT", "10") or "10")
    ))
    
    # Cache
    cache: CacheConfig = field(default_factory=lambda: CacheConfig(
        enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
        ttl=int(os.getenv("CACHE_TTL", "3600") or "3600"),
        backend=os.getenv("CACHE_BACKEND", "memory")
    ))
    
    # Translation
    translation_provider: str = os.getenv("TRANSLATION_PROVIDER", "openai")
    translation_config: Dict[str, Any] = field(default_factory=dict)
    
    # CORS
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    _instance: Optional['Settings'] = None
    
    @classmethod
    def get_instance(cls) -> 'Settings':
        """Get singleton instance.
        
        Returns:
            Settings instance (creates if doesn't exist)
        """
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._validate()
        return cls._instance
    
    def _validate(self) -> None:
        """Validate all configuration settings.
        
        Raises:
            ConfigurationError: If any required setting is missing or invalid
        """
        from app.core.domain.exceptions import ConfigurationError
        errors = []
        
        if not self.database.host:
            errors.append("Database host is required")
        if not self.database.database:
            errors.append("Database name is required")
        if not self.database.user:
            errors.append("Database user is required")
        if not self.database.password:
            errors.append("Database password is required")
        if self.database.pool_size < 1:
            errors.append("Pool size must be at least 1")
        
        if not self.openai.api_key:
            errors.append("OpenAI API key is required")
        if not self.openai.model:
            errors.append("OpenAI model is required")
        
        if not self.ido_sell.client_username:
            errors.append("IdoSell client username is required")
        if not self.ido_sell.client_secret:
            errors.append("IdoSell client secret is required")
        if not self.ido_sell.base_url:
            errors.append("IdoSell base URL is required")
        
        if not self.vies.wsdl_url:
            errors.append("VIES WSDL URL is required")
        
        if errors:
            raise ConfigurationError(
                f"Configuration errors: {', '.join(errors)}"
            )


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the prompts configuration directory.
    
    Args:
        prompt_name: Name of the prompt to load (e.g., 'generate', 'rephrase', 'meta_title')
    
    Returns:
        The prompt template as a string
    
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
        KeyError: If the prompt file doesn't contain a 'prompt' key
        Exception: For other errors loading the prompt
    
    Example:
        >>> prompt = load_prompt("generate")
        >>> print(prompt[:50])
        'Na podstawie przesłanego zdjęcia lub kilku zdjęć...'
    """
    import yaml
    from pathlib import Path
    
    prompts_dir = Path(__file__).parent / "prompts"
    prompt_file = prompts_dir / f"{prompt_name}.yaml"
    
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}"
        )
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_data = yaml.safe_load(f)
        
        if 'prompt' not in prompt_data:
            raise KeyError(
                f"Prompt file '{prompt_file}' does not contain a 'prompt' key"
            )
        
        prompt_content = prompt_data['prompt']
        
        if not isinstance(prompt_content, str):
            raise ValueError(
                f"Prompt content in '{prompt_file}' is not a string"
            )
        
        logger.debug(f"Successfully loaded prompt: {prompt_name}")
        return prompt_content
        
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file '{prompt_file}': {e}")
        raise Exception(f"Error parsing prompt file '{prompt_file}': {e}") from e
    except Exception as e:
        logger.error(f"Error loading prompt '{prompt_name}': {e}")
        raise


def get_settings() -> Settings:
    """
    Get the Settings singleton instance.
    
    Returns:
        Settings instance
    """
    return Settings.get_instance()


def get_allowed_origins() -> str:
    """
    Get the allowed CORS origins.
    
    Returns:
        String of allowed origins (comma-separated or '*')
    """
    return get_settings().allowed_origins


def get_base_url() -> str:
    """
    Get the IdoSell base URL.
    
    Returns:
        Base URL for IdoSell API
    """
    return get_settings().ido_sell.base_url


def get_client_username() -> str:
    """
    Get the IdoSell client username.
    
    Returns:
        Client username for API authentication
    """
    return get_settings().ido_sell.client_username


def get_client_secret() -> str:
    """
    Get the IdoSell client secret.
    
    Returns:
        Client secret for API authentication
    """
    return get_settings().ido_sell.client_secret


def get_openai_api_key() -> str:
    """
    Get the OpenAI API key.
    
    Returns:
        OpenAI API key
    """
    return get_settings().openai.api_key


def get_openai_model() -> str:
    """
    Get the OpenAI model name.
    
    Returns:
        OpenAI model name (e.g., 'gpt-4')
    """
    return get_settings().openai.model
