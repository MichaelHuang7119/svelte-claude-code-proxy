import os
import sys
import json
from pathlib import Path
from typing import Optional

from src.models.provider import ProviderManagerConfig
from src.core.provider_manager import ProviderManager
from src.core.colored_logger import colored_logger


# Configuration
class Config:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        # OPENAI_API_KEY is optional if using provider config file
        # Will be validated in load_provider_config() if needed
        
        # Add Anthropic API key for client validation
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            print("Warning: ANTHROPIC_API_KEY not set. Client API key validation will be disabled.")
        
        self.openai_base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.azure_api_version = os.environ.get("AZURE_API_VERSION")  # For Azure OpenAI
        self.host = os.environ.get("HOST", "0.0.0.0")
        self.port = int(os.environ.get("PORT", "8082"))
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.max_tokens_limit = int(os.environ.get("MAX_TOKENS_LIMIT", "4096"))
        self.min_tokens_limit = int(os.environ.get("MIN_TOKENS_LIMIT", "100"))
        
        # Connection settings
        self.request_timeout = int(os.environ.get("REQUEST_TIMEOUT", "90"))
        self.max_retries = int(os.environ.get("MAX_RETRIES", "2"))
        
        # Model settings - BIG and SMALL models
        self.big_model = os.environ.get("BIG_MODEL", "gpt-4o")
        self.middle_model = os.environ.get("MIDDLE_MODEL", self.big_model)
        self.small_model = os.environ.get("SMALL_MODEL", "gpt-4o-mini")
        
        # Provider configuration
        self.provider_manager: Optional[ProviderManager] = None
        self.use_provider_config = False
        
    def validate_api_key(self):
        """Basic API key validation"""
        if not self.openai_api_key:
            return False
        # Basic format check for OpenAI API keys
        if not self.openai_api_key.startswith('sk-'):
            return False
        return True
        
    def validate_client_api_key(self, client_api_key):
        """Validate client's Anthropic API key"""
        # If no ANTHROPIC_API_KEY is set in environment, skip validation
        if not self.anthropic_api_key:
            return True
            
        # Check if the client's API key matches the expected value
        return client_api_key == self.anthropic_api_key
    
    def get_custom_headers(self):
        """Get custom headers from environment variables"""
        custom_headers = {}
        
        # Get all environment variables
        env_vars = dict(os.environ)
        
        # Find CUSTOM_HEADER_* environment variables
        for env_key, env_value in env_vars.items():
            if env_key.startswith('CUSTOM_HEADER_'):
                # Convert CUSTOM_HEADER_KEY to Header-Key
                # Remove 'CUSTOM_HEADER_' prefix and convert to header format
                header_name = env_key[14:]  # Remove 'CUSTOM_HEADER_' prefix
                
                if header_name:  # Make sure it's not empty
                    # Convert underscores to hyphens for HTTP header format
                    header_name = header_name.replace('_', '-')
                    custom_headers[header_name] = env_value
        
        return custom_headers
    
    def load_provider_config(self, config_path: Optional[str] = None) -> bool:
        """Load provider configuration from file or use legacy format"""
        if config_path is None:
            # Try to find provider config file
            # Only use .example.json if the actual .json doesn't exist
            possible_paths = [
                "config/providers.json",
                "providers.json"
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    config_path = path
                    break
            
            # Only fall back to example file if no actual config exists
            if not config_path:
                example_paths = [
                    "config/providers.example.json",
                    "providers.example.json"
                ]
                for path in example_paths:
                    if Path(path).exists():
                        colored_logger.warning(f"⚠️  Using example config file: {path}")
                        colored_logger.warning("   Please create config/providers.json from the example file")
                        config_path = path
                        break
        
        if config_path and Path(config_path).exists():
            try:
                # Load from JSON file
                provider_config = ProviderManagerConfig.from_file(config_path)
                self.provider_manager = ProviderManager(provider_config)
                
                # Check if any providers were initialized
                if not self.provider_manager.providers:
                    colored_logger.error("❌ No providers were successfully initialized")
                    colored_logger.error("   Please check that required environment variables are set")
                    colored_logger.warning("⚠️  Falling back to legacy configuration")
                    self.provider_manager = None
                else:
                    self.use_provider_config = True
                    colored_logger.success(f"✅ Loaded provider configuration from {config_path}")
                    colored_logger.info(f"   Initialized {len(self.provider_manager.providers)} provider(s)")
                    return True
            except Exception as e:
                colored_logger.error(f"❌ Failed to load provider config from {config_path}: {e}")
                colored_logger.warning("⚠️  Falling back to legacy configuration")
                self.provider_manager = None
        
        # Fall back to legacy configuration
        # For legacy config, OPENAI_API_KEY is required
        if not self.openai_api_key:
            colored_logger.error("❌ OPENAI_API_KEY not found in environment variables")
            colored_logger.error("   Please set OPENAI_API_KEY or configure providers.json")
            return False
        
        try:
            provider_config = ProviderManagerConfig.from_env_config(self)
            self.provider_manager = ProviderManager(provider_config)
            self.use_provider_config = False
            colored_logger.info("ℹ️  Using legacy environment variable configuration")
            return True
        except Exception as e:
            colored_logger.error(f"❌ Failed to initialize provider manager: {e}")
            return False
    
    def print_provider_info(self):
        """Print provider configuration information with colors"""
        if not self.provider_manager:
            colored_logger.error("❌ No provider manager initialized")
            return
        
        colored_logger.header("🚀 Claude Code Proxy - Provider Configuration")
        
        for name, state in self.provider_manager.providers.items():
            if not state.provider.enabled:
                continue
                
            # Provider header
            colored_logger.provider(name, f"Priority: {state.provider.priority}")
            
            # Model information
            if state.provider.models.big:
                colored_logger.model_info(name, "BIG (opus)", state.provider.models.big)
            if state.provider.models.middle:
                colored_logger.model_info(name, "MIDDLE (sonnet)", state.provider.models.middle)
            if state.provider.models.small:
                colored_logger.model_info(name, "SMALL (haiku)", state.provider.models.small)
            
            # Status
            status_color = "healthy" if state.status.value == "healthy" else "error"
            colored_logger.status(status_color, f"Status: {state.status.value}")
            
            print()  # Empty line between providers
        
        # Configuration summary
        colored_logger.info(f"📊 Server: {self.host}:{self.port}")
        colored_logger.info(f"📊 Max Tokens: {self.max_tokens_limit}")
        colored_logger.info(f"📊 Timeout: {self.request_timeout}s")
        colored_logger.info(f"📊 Client API Key Validation: {'Enabled' if self.anthropic_api_key else 'Disabled'}")
        print()

try:
    config = Config()
    # Try to load provider configuration
    if not config.load_provider_config():
        print("Configuration Error: Failed to load provider configuration")
        sys.exit(1)
    
    # Print provider information
    config.print_provider_info()
except Exception as e:
    print(f"Configuration Error: {e}")
    sys.exit(1)