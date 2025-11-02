import asyncio
import time
import random
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from src.models.provider import ProviderConfig, ProviderManagerConfig
from src.core.client import OpenAIClient


class ProviderStatus(Enum):
    """Provider status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ProviderState:
    """State tracking for a provider"""
    provider: ProviderConfig
    status: ProviderStatus = ProviderStatus.HEALTHY
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    client: Optional[OpenAIClient] = None
    # Model rotation tracking
    model_indices: Dict[str, int] = None  # Track current model index for each type

    def __post_init__(self):
        if self.model_indices is None:
            self.model_indices = {}

    def get_next_model(self, model_type: str) -> Optional[str]:
        """Get next model for the given type, cycling through available models"""
        models = getattr(self.provider.models, model_type, [])
        if not models:
            return None

        # Get current index for this model type
        current_index = self.model_indices.get(model_type, 0)

        # Get the model at current index
        model = models[current_index]

        # Update index for next time (cycle through models)
        self.model_indices[model_type] = (current_index + 1) % len(models)

        return model


class ProviderManager:
    """Manages multiple providers with fallback and health checking"""

    def __init__(self, config: ProviderManagerConfig):
        self.config = config
        self.providers: Dict[str, ProviderState] = {}
        self.logger = logging.getLogger(__name__)

        # Initialize providers
        self._initialize_providers()

        # Health check task will be started when first accessed
        self._health_check_task = None
        self._health_checks_started = False

    def _initialize_providers(self):
        """Initialize all providers from configuration"""
        for provider_config in self.config.providers:
            if not provider_config.enabled:
                continue

            # Resolve environment variables
            resolved_provider = provider_config.resolve_env_vars()

            # Create OpenAI client
            client = OpenAIClient(
                api_key=resolved_provider.api_key,
                base_url=resolved_provider.base_url,
                timeout=resolved_provider.timeout,
                api_version=resolved_provider.api_version,
                custom_headers=resolved_provider.custom_headers
            )

            # Create provider state
            state = ProviderState(
                provider=resolved_provider,
                client=client
            )
            self.providers[resolved_provider.name] = state
            self.logger.info(f"✅ Initialized provider: {resolved_provider.name}")

    def _start_health_checks(self):
        """Start background health check task"""
        if self.config.health_check_interval > 0 and not self._health_checks_started:
            try:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
                self._health_checks_started = True
            except RuntimeError:
                # No event loop running, skip health checks
                self.logger.warning("No event loop running, skipping health checks")

    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                self.logger.info("Health check loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                # Continue running even if there's an error

    async def _perform_health_checks(self):
        """Perform health checks on all providers"""
        for name, state in self.providers.items():
            if state.status == ProviderStatus.CIRCUIT_OPEN:
                # Check if circuit should be closed
                if (state.last_failure_time and
                    time.time() - state.last_failure_time > self.config.circuit_breaker.recovery_timeout):
                    state.status = ProviderStatus.HEALTHY
                    state.failure_count = 0
                    self.logger.info(f"🔄 Circuit breaker closed for {name}")

    def _ensure_health_checks_started(self):
        """Ensure health checks are started if not already running"""
        if not self._health_checks_started:
            self._start_health_checks()

    def get_available_providers(self) -> List[ProviderState]:
        """Get list of available providers sorted by priority"""
        self._ensure_health_checks_started()

        available = []
        for state in self.providers.values():
            if state.status == ProviderStatus.HEALTHY:
                available.append(state)

        # Sort by priority
        available.sort(key=lambda x: x.provider.priority)
        return available

    def get_provider_for_model(self, model_type: str) -> Optional[Tuple[ProviderState, str]]:
        """Get provider and model for the given model type (big/middle/small)"""
        available_providers = self.get_available_providers()

        if not available_providers:
            return None

        # Try each provider in priority order
        for state in available_providers:
            model = state.get_next_model(model_type)
            if model:
                return state, model

        return None

    def get_fallback_provider_for_model(self, model_type: str, exclude_provider: str = None) -> Optional[Tuple[ProviderState, str]]:
        """Get fallback provider for model type, excluding the specified provider"""
        available_providers = self.get_available_providers()

        # Filter out excluded provider
        if exclude_provider:
            available_providers = [p for p in available_providers if p.provider.name != exclude_provider]

        if not available_providers:
            return None

        # Apply fallback strategy
        if self.config.fallback_strategy == "priority":
            # Already sorted by priority
            pass
        elif self.config.fallback_strategy == "round_robin":
            # Simple round-robin (could be enhanced with state tracking)
            random.shuffle(available_providers)
        elif self.config.fallback_strategy == "random":
            random.shuffle(available_providers)

        # Try each provider
        for state in available_providers:
            model = state.get_next_model(model_type)
            if model:
                return state, model

        return None

    def get_next_model_for_provider(self, provider_name: str, model_type: str) -> Optional[Tuple[ProviderState, str]]:
        """Get next model for a specific provider, cycling through its models"""
        if provider_name not in self.providers:
            return None

        state = self.providers[provider_name]
        if state.status != ProviderStatus.HEALTHY:
            return None

        model = state.get_next_model(model_type)
        if model:
            return state, model

        return None

    async def get_client_for_model(self, model_type: str, exclude_provider: str = None) -> Optional[Tuple[OpenAIClient, str, str]]:
        """Get client, model name, and provider name for the given model type"""
        if exclude_provider:
            result = self.get_fallback_provider_for_model(model_type, exclude_provider)
        else:
            result = self.get_provider_for_model(model_type)

        if not result:
            return None

        state, model_name = result
        return state.client, model_name, state.provider.name

    def mark_provider_failure(self, provider_name: str, error: Exception = None):
        """Mark a provider as failed"""
        if provider_name not in self.providers:
            return

        state = self.providers[provider_name]
        state.failure_count += 1
        state.last_failure_time = time.time()

        self.logger.warning(f"❌ Provider {provider_name} failed (attempt {state.failure_count})")

        # Check if circuit breaker should open
        if state.failure_count >= self.config.circuit_breaker.failure_threshold:
            state.status = ProviderStatus.CIRCUIT_OPEN
            self.logger.error(f"🔴 Circuit breaker opened for {provider_name}")
        else:
            state.status = ProviderStatus.UNHEALTHY

    def mark_provider_success(self, provider_name: str):
        """Mark a provider as successful"""
        if provider_name not in self.providers:
            return

        state = self.providers[provider_name]
        state.failure_count = 0
        state.last_success_time = time.time()
        state.status = ProviderStatus.HEALTHY

        self.logger.info(f"✅ Provider {provider_name} recovered")

    def get_provider_status_summary(self) -> Dict[str, Any]:
        """Get summary of all provider statuses"""
        summary = {}
        for name, state in self.providers.items():
            summary[name] = {
                "status": state.status.value,
                "priority": state.provider.priority,
                "failure_count": state.failure_count,
                "last_failure": state.last_failure_time,
                "last_success": state.last_success_time,
                "models": {
                    "big": state.provider.models.big,
                    "middle": state.provider.models.middle,
                    "small": state.provider.models.small
                }
            }
        return summary

    async def close(self):
        """Close the provider manager and cleanup resources"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass