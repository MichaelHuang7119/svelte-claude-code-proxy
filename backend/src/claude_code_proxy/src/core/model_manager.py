from src.core.config import config
from src.core.colored_logger import colored_logger
from typing import Optional, Tuple

class ModelManager:
    def __init__(self, config):
        self.config = config
    
    def map_claude_model_to_openai(self, claude_model: str) -> str:
        """Map Claude model names to OpenAI model names based on BIG/SMALL pattern"""
        # If it's already an OpenAI model, return as-is
        if claude_model.startswith("gpt-") or claude_model.startswith("o1-"):
            return claude_model

        # If it's other supported models (ARK/Doubao/DeepSeek), return as-is
        if (claude_model.startswith("ep-") or claude_model.startswith("doubao-") or 
            claude_model.startswith("deepseek-")):
            return claude_model
        
        # Map based on model naming patterns
        model_lower = claude_model.lower()
        if 'haiku' in model_lower:
            return self.config.small_model
        elif 'sonnet' in model_lower:
            return self.config.middle_model
        elif 'opus' in model_lower:
            return self.config.big_model
        else:
            # Default to big model for unknown models
            return self.config.big_model
    
    async def get_client_and_model(self, claude_model: str, exclude_provider: str = None) -> Optional[Tuple[any, str, str]]:
        """Get client, model name, and provider name for the given Claude model"""
        if not self.config.provider_manager:
            # Fallback to legacy behavior
            model_name = self.map_claude_model_to_openai(claude_model)
            from src.core.client import OpenAIClient
            client = OpenAIClient(
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_base_url,
                timeout=self.config.request_timeout,
                api_version=self.config.azure_api_version,
                custom_headers=self.config.get_custom_headers()
            )
            return client, model_name, "Legacy Claude Code Proxy"
        
        # Determine model type from Claude model name
        model_lower = claude_model.lower()
        if 'haiku' in model_lower:
            model_type = "small"
        elif 'sonnet' in model_lower:
            model_type = "middle"
        elif 'opus' in model_lower:
            model_type = "big"
        else:
            # Default to big model for unknown models
            model_type = "big"
        
        # Get client and model from provider manager
        result = await self.config.provider_manager.get_client_for_model(model_type, exclude_provider)
        if result:
            client, model_name, provider_name = result
            colored_logger.info(f"🎯 Using {provider_name} with model {model_name} for {claude_model}")
            return client, model_name, provider_name
        
        # If no provider available, fall back to legacy
        colored_logger.warning(f"⚠️  No provider available for {model_type} models, falling back to legacy")
        try:
            model_name = self.map_claude_model_to_openai(claude_model)
            from src.core.client import OpenAIClient
            client = OpenAIClient(
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_base_url,
                timeout=self.config.request_timeout,
                api_version=self.config.azure_api_version,
                custom_headers=self.config.get_custom_headers()
            )
            return client, model_name, "Legacy Fallback"
        except Exception as e:
            colored_logger.error(f"❌ Legacy fallback failed: {e}")
            return None
    
    async def get_next_model_for_provider(self, claude_model: str, provider_name: str) -> Optional[Tuple[any, str, str]]:
        """Get next model for a specific provider, cycling through its models"""
        if not self.config.provider_manager:
            return None
        
        # Determine model type from Claude model name
        model_lower = claude_model.lower()
        if 'haiku' in model_lower:
            model_type = "small"
        elif 'sonnet' in model_lower:
            model_type = "middle"
        elif 'opus' in model_lower:
            model_type = "big"
        else:
            # Default to big model for unknown models
            model_type = "big"
        
        # Get next model for the specific provider
        result = self.config.provider_manager.get_next_model_for_provider(provider_name, model_type)
        if result:
            state, model_name = result
            colored_logger.info(f"🔄 Trying next model {model_name} for {provider_name}")
            return state.client, model_name, provider_name
        
        return None

model_manager = ModelManager(config)