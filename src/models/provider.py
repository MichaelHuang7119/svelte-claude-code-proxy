from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
import os
import json


class ProviderModelConfig(BaseModel):
    """Configuration for models within a provider"""
    big: List[str] = Field(default_factory=list, description="List of big models (opus)")
    middle: List[str] = Field(default_factory=list, description="List of middle models (sonnet)")
    small: List[str] = Field(default_factory=list, description="List of small models (haiku)")


class ProviderConfig(BaseModel):
    """Configuration for a single provider"""
    name: str = Field(..., description="Provider name")
    enabled: bool = Field(default=True, description="Whether provider is enabled")
    priority: int = Field(..., description="Priority order (lower = higher priority)")
    api_key: str = Field(..., description="API key (can use ${ENV_VAR} format)")
    base_url: str = Field(..., description="Base URL for the API")
    api_version: Optional[str] = Field(default=None, description="API version (for Azure)")
    timeout: int = Field(default=90, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    custom_headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    models: ProviderModelConfig = Field(default_factory=ProviderModelConfig, description="Model configuration")
    
    def resolve_env_vars(self) -> 'ProviderConfig':
        """Resolve environment variables in configuration"""
        import os
        
        try:
            resolved = self.model_copy()
            
            # Resolve API key
            if resolved.api_key.startswith('${') and resolved.api_key.endswith('}'):
                env_var = resolved.api_key[2:-1]
                env_value = os.environ.get(env_var)
                if env_value is None:
                    raise ValueError(f"Environment variable {env_var} not found for API key")
                resolved.api_key = env_value
            
            # Resolve base URL
            if resolved.base_url.startswith('${') and resolved.base_url.endswith('}'):
                env_var = resolved.base_url[2:-1]
                env_value = os.environ.get(env_var)
                if env_value is None:
                    raise ValueError(f"Environment variable {env_var} not found for base URL")
                resolved.base_url = env_value
            
            # Resolve custom headers
            resolved_headers = {}
            for key, value in resolved.custom_headers.items():
                if value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    env_value = os.environ.get(env_var)
                    if env_value is None:
                        raise ValueError(f"Environment variable {env_var} not found for custom header {key}")
                    resolved_headers[key] = env_value
                else:
                    resolved_headers[key] = value
            resolved.custom_headers = resolved_headers
            
            return resolved
        except Exception as e:
            raise ValueError(f"Error resolving environment variables for provider {self.name}: {e}")


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration"""
    failure_threshold: int = Field(default=5, description="Number of failures before opening circuit")
    recovery_timeout: int = Field(default=60, description="Seconds to wait before attempting recovery")


class ProviderManagerConfig(BaseModel):
    """Main configuration for provider management"""
    providers: List[ProviderConfig] = Field(..., description="List of providers")
    fallback_strategy: Literal["priority", "round_robin", "random"] = Field(
        default="priority", 
        description="Fallback strategy when primary provider fails"
    )
    health_check_interval: int = Field(default=300, description="Health check interval in seconds")
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'ProviderManagerConfig':
        """Load configuration from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Provider configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in provider configuration file {file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading provider configuration from {file_path}: {e}")
    
    @classmethod
    def from_env_config(cls, config) -> 'ProviderManagerConfig':
        """Create configuration from legacy environment variables"""
        # Create a legacy provider configuration
        legacy_provider = ProviderConfig(
            name="Legacy Claude Code Proxy",
            enabled=True,
            priority=1,
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            api_version=config.azure_api_version,
            timeout=config.request_timeout,
            max_retries=config.max_retries,
            custom_headers=config.get_custom_headers(),
            models=ProviderModelConfig(
                big=[config.big_model],
                middle=[config.middle_model],
                small=[config.small_model]
            )
        )
        
        return cls(
            providers=[legacy_provider],
            fallback_strategy="priority",
            health_check_interval=300,
            circuit_breaker=CircuitBreakerConfig()
        )

