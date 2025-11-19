"""Configuration and security module for AstraFoundry"""

import os
from typing import Optional
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class Config:
    """Configuration manager for AstraFoundry"""
    
    def __init__(self):
        """Initialize configuration by loading environment variables"""
        load_dotenv()
        self._validate_required_keys()
    
    def _validate_required_keys(self) -> None:
        """Validate that all required API keys are present"""
        required_keys = ['GOOGLE_API_KEY']
        missing_keys = []
        
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ConfigurationError(
                f"Missing required API keys: {', '.join(missing_keys)}. "
                f"Please set them in your .env file or environment variables."
            )
    
    @property
    def google_api_key(self) -> str:
        """Get Google API key for Gemini models"""
        return os.getenv('GOOGLE_API_KEY', '')
    
    @property
    def google_search_api_key(self) -> Optional[str]:
        """Get Google Search API key (optional)"""
        return os.getenv('GOOGLE_SEARCH_API_KEY')
    
    @property
    def google_search_engine_id(self) -> Optional[str]:
        """Get Google Search Engine ID (optional)"""
        return os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    @property
    def timeout_seconds(self) -> int:
        """Get pipeline timeout in seconds (default: 300)"""
        return int(os.getenv('TIMEOUT_SECONDS', '300'))
    
    @property
    def enable_memory(self) -> bool:
        """Check if memory bank is enabled (default: True)"""
        return os.getenv('ENABLE_MEMORY', 'true').lower() == 'true'
    
    def get_safe_config(self) -> dict:
        """Get configuration dict with sensitive values masked"""
        return {
            'google_api_key': self._mask_key(self.google_api_key),
            'google_search_api_key': self._mask_key(self.google_search_api_key),
            'google_search_engine_id': self._mask_key(self.google_search_engine_id),
            'timeout_seconds': self.timeout_seconds,
            'enable_memory': self.enable_memory
        }
    
    @staticmethod
    def _mask_key(key: Optional[str]) -> str:
        """Mask API key for safe logging"""
        if not key:
            return 'Not set'
        if len(key) <= 8:
            return '***'
        return f"{key[:4]}...{key[-4:]}"


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def validate_config() -> bool:
    """Validate configuration and return True if valid"""
    try:
        get_config()
        return True
    except ConfigurationError:
        return False
