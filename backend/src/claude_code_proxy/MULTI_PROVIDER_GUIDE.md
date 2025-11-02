# Multi-Provider Configuration Guide

This guide covers advanced usage of the multi-provider functionality in Claude Code Proxy.

## 🎯 Overview

The multi-provider system allows you to:
- Configure multiple LLM providers with different priorities
- Set up automatic fallback when providers fail
- Use different models for different request types (big/middle/small)
- Monitor provider health and status
- Implement circuit breaker patterns for reliability

## 📋 Configuration Structure

### Basic Provider Configuration

```json
{
  "providers": [
    {
      "name": "provider-name",
      "enabled": true,
      "priority": 1,
      "api_key": "${ENV_VAR_NAME}",
      "base_url": "https://api.example.com/v1",
      "api_version": null,
      "timeout": 90,
      "max_retries": 3,
      "custom_headers": {},
      "models": {
        "big": ["model1", "model2"],
        "middle": ["model3", "model4"],
        "small": ["model5", "model6"]
      }
    }
  ],
  "fallback_strategy": "priority",
  "health_check_interval": 300,
  "circuit_breaker": {
    "failure_threshold": 5,
    "recovery_timeout": 60
  }
}
```

## 🔧 Provider Configuration Options

### Required Fields

- **name**: Unique identifier for the provider
- **api_key**: API key (supports environment variable substitution)
- **base_url**: API endpoint URL
- **models**: Model configuration for different sizes

### Optional Fields

- **enabled**: Whether the provider is active (default: true)
- **priority**: Priority order, lower numbers = higher priority (default: 1)
- **api_version**: API version for Azure OpenAI (default: null)
- **timeout**: Request timeout in seconds (default: 90)
- **max_retries**: Maximum retry attempts (default: 3)
- **custom_headers**: Additional HTTP headers (default: {})

### Model Configuration

Each provider can have multiple models for different request types:

- **big**: Models for Claude opus requests
- **middle**: Models for Claude sonnet requests  
- **small**: Models for Claude haiku requests

## 🚀 Advanced Configuration Examples

### High Availability Setup

```json
{
  "providers": [
    {
      "name": "openai-primary",
      "enabled": true,
      "priority": 1,
      "api_key": "${OPENAI_API_KEY}",
      "base_url": "https://api.openai.com/v1",
      "models": {
        "big": ["gpt-4o", "gpt-4-turbo"],
        "middle": ["gpt-4o", "gpt-4-turbo"],
        "small": ["gpt-4o-mini", "gpt-3.5-turbo"]
      }
    },
    {
      "name": "azure-backup",
      "enabled": true,
      "priority": 2,
      "api_key": "${AZURE_API_KEY}",
      "base_url": "${AZURE_BASE_URL}",
      "api_version": "2024-02-15-preview",
      "models": {
        "big": ["gpt-4o", "gpt-4"],
        "middle": ["gpt-4o", "gpt-4"],
        "small": ["gpt-4o-mini", "gpt-35-turbo"]
      }
    },
    {
      "name": "local-ollama",
      "enabled": true,
      "priority": 3,
      "api_key": "dummy-key",
      "base_url": "http://localhost:11434/v1",
      "models": {
        "big": ["llama3.1:70b"],
        "middle": ["llama3.1:70b"],
        "small": ["llama3.1:8b"]
      }
    }
  ],
  "fallback_strategy": "priority",
  "circuit_breaker": {
    "failure_threshold": 3,
    "recovery_timeout": 120
  }
}
```

### Cost Optimization Setup

```json
{
  "providers": [
    {
      "name": "cheap-provider",
      "enabled": true,
      "priority": 1,
      "api_key": "${CHEAP_API_KEY}",
      "base_url": "https://cheap-api.com/v1",
      "models": {
        "big": ["cheap-big-model"],
        "middle": ["cheap-middle-model"],
        "small": ["cheap-small-model"]
      }
    },
    {
      "name": "premium-provider",
      "enabled": true,
      "priority": 2,
      "api_key": "${PREMIUM_API_KEY}",
      "base_url": "https://premium-api.com/v1",
      "models": {
        "big": ["premium-big-model"],
        "middle": ["premium-middle-model"],
        "small": ["premium-small-model"]
      }
    }
  ],
  "fallback_strategy": "priority"
}
```

### Geographic Distribution

```json
{
  "providers": [
    {
      "name": "us-east",
      "enabled": true,
      "priority": 1,
      "api_key": "${US_EAST_API_KEY}",
      "base_url": "https://us-east.api.com/v1",
      "models": {
        "big": ["gpt-4o"],
        "middle": ["gpt-4o"],
        "small": ["gpt-4o-mini"]
      }
    },
    {
      "name": "eu-west",
      "enabled": true,
      "priority": 2,
      "api_key": "${EU_WEST_API_KEY}",
      "base_url": "https://eu-west.api.com/v1",
      "models": {
        "big": ["gpt-4o"],
        "middle": ["gpt-4o"],
        "small": ["gpt-4o-mini"]
      }
    },
    {
      "name": "asia-pacific",
      "enabled": true,
      "priority": 3,
      "api_key": "${ASIA_API_KEY}",
      "base_url": "https://asia.api.com/v1",
      "models": {
        "big": ["gpt-4o"],
        "middle": ["gpt-4o"],
        "small": ["gpt-4o-mini"]
      }
    }
  ],
  "fallback_strategy": "priority"
}
```

## 🔄 Fallback Strategies

### Priority (Default)
Providers are used in priority order. If a provider fails, the next highest priority provider is used.

```json
{
  "fallback_strategy": "priority"
}
```

### Round Robin
Providers are rotated in a round-robin fashion.

```json
{
  "fallback_strategy": "round_robin"
}
```

### Random
Providers are selected randomly from available providers.

```json
{
  "fallback_strategy": "random"
}
```

## 🛡️ Circuit Breaker Configuration

The circuit breaker pattern prevents cascading failures by temporarily disabling failed providers.

```json
{
  "circuit_breaker": {
    "failure_threshold": 5,    // Number of failures before opening circuit
    "recovery_timeout": 60     // Seconds to wait before retrying
  }
}
```

### Circuit Breaker States

1. **Closed**: Provider is healthy and accepting requests
2. **Open**: Provider has failed too many times and is temporarily disabled
3. **Half-Open**: Provider is being tested to see if it has recovered

## 📊 Health Monitoring

### Health Check Configuration

```json
{
  "health_check_interval": 300  // Check every 5 minutes
}
```

### Provider Status Monitoring

Check provider status via the health endpoint:

```bash
curl http://localhost:8082/health
```

Response includes provider status:

```json
{
  "status": "healthy",
  "providers": {
    "openai": {
      "status": "healthy",
      "priority": 1,
      "failure_count": 0,
      "last_success": 1703123456.789,
      "last_failure": null
    },
    "azure": {
      "status": "circuit_open",
      "priority": 2,
      "failure_count": 5,
      "last_success": 1703123000.123,
      "last_failure": 1703123400.456
    }
  }
}
```

## 🎨 Colored Logging

The proxy provides beautiful colored terminal output:

- **Provider Names**: Each provider has a unique color
- **Status Indicators**: ✅ healthy, ❌ error, ⚠️ warning, ℹ️ info
- **Model Information**: Clear categorization of models
- **Fallback Notifications**: Real-time switching notifications

### Example Output

```
🚀 Claude Code Proxy - Provider Configuration
[openai] Priority: 1
  [openai] BIG (OPUS): gpt-4o, gpt-4-turbo
  [openai] MIDDLE (SONNET): gpt-4o, gpt-4-turbo
  [openai] SMALL (HAIKU): gpt-4o-mini, gpt-3.5-turbo
✅ Status: healthy

[azure] Priority: 2
  [azure] BIG (OPUS): gpt-4o, gpt-4
  [azure] MIDDLE (SONNET): gpt-4o, gpt-4
  [azure] SMALL (HAIKU): gpt-4o-mini, gpt-35-turbo
✅ Status: healthy
```

## 🔧 Environment Variable Substitution

All configuration values support environment variable substitution:

```json
{
  "api_key": "${OPENAI_API_KEY}",
  "base_url": "${OPENAI_BASE_URL}",
  "custom_headers": {
    "Authorization": "Bearer ${CUSTOM_TOKEN}",
    "X-API-Key": "${API_KEY}"
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Provider Not Available**
   - Check if provider is enabled
   - Verify API key is set correctly
   - Check base URL is accessible

2. **Circuit Breaker Open**
   - Wait for recovery timeout
   - Check provider health
   - Verify API key and permissions

3. **No Models Available**
   - Ensure models are configured for the request type
   - Check if models are available in the provider
   - Verify model names are correct

### Debug Mode

Enable debug logging to see detailed provider information:

```bash
export LOG_LEVEL=DEBUG
python start_proxy.py
```

## 📈 Performance Tips

1. **Provider Priority**: Order providers by reliability and speed
2. **Model Selection**: Use faster models for small requests
3. **Timeout Configuration**: Set appropriate timeouts for each provider
4. **Circuit Breaker**: Tune failure thresholds based on your use case
5. **Health Checks**: Adjust health check intervals based on provider stability

## 🔄 Migration from Legacy Configuration

To migrate from legacy environment variable configuration:

1. Create `config/providers.json` based on your current environment variables
2. Test the new configuration
3. Remove old environment variables once confirmed working

Example migration:

**Legacy:**
```bash
export OPENAI_API_KEY="sk-your-key"
export BIG_MODEL="gpt-4o"
export SMALL_MODEL="gpt-4o-mini"
```

**New:**
```json
{
  "providers": [
    {
      "name": "openai",
      "enabled": true,
      "priority": 1,
      "api_key": "${OPENAI_API_KEY}",
      "base_url": "https://api.openai.com/v1",
      "models": {
        "big": ["gpt-4o"],
        "middle": ["gpt-4o"],
        "small": ["gpt-4o-mini"]
      }
    }
  ]
}
```

This guide should help you get the most out of the multi-provider functionality! 🎉


