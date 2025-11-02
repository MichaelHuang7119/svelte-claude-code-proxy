# Changelog

## [2.0.0] - 2024-12-19

### 🎉 Major Features Added

#### Multi-Provider Support
- **Multiple Provider Configuration**: Support for configuring multiple LLM providers with JSON configuration
- **Automatic Fallback**: Intelligent fallback when providers or models fail
- **Priority-Based Selection**: Configure provider priority for optimal performance
- **Circuit Breaker Pattern**: Prevent cascading failures with automatic provider disabling
- **Health Monitoring**: Background health checks with automatic recovery

#### Enhanced Logging
- **Colored Terminal Output**: Beautiful colored logging for better visibility
- **Provider-Specific Colors**: Each provider has a unique color for easy identification
- **Status Indicators**: Clear status indicators (✅ healthy, ❌ error, ⚠️ warning, ℹ️ info)
- **Real-Time Notifications**: Live notifications when switching providers

#### Model Management
- **Multiple Models per Provider**: Configure multiple models for each provider
- **Model-Level Fallback**: Automatic fallback to next model if current model fails
- **Smart Model Selection**: Automatic selection based on request type (big/middle/small)

### 🔧 Configuration Enhancements

#### New Configuration Format
- **JSON-Based Configuration**: `config/providers.json` for multi-provider setup
- **Environment Variable Substitution**: Support for `${ENV_VAR}` syntax
- **Flexible Provider Options**: Custom headers, timeouts, retry settings per provider
- **Fallback Strategies**: Priority, round-robin, and random selection strategies

#### Backward Compatibility
- **Legacy Support**: Full backward compatibility with existing `.env` configuration
- **Automatic Detection**: Automatic detection of configuration format
- **Seamless Migration**: Easy migration from legacy to new format

### 📁 New Files

- `src/models/provider.py` - Provider configuration models
- `src/core/provider_manager.py` - Provider management with fallback logic
- `src/core/colored_logger.py` - Colored logging utilities
- `config/providers.example.json` - Example provider configuration
- `MULTI_PROVIDER_GUIDE.md` - Comprehensive multi-provider guide

### 🔄 Modified Files

- `src/core/config.py` - Updated to support both old and new formats
- `src/core/model_manager.py` - Enhanced with provider-aware model selection
- `src/api/endpoints.py` - Updated to use new provider system with fallback
- `src/main.py` - Simplified configuration display
- `README.md` - Updated with multi-provider documentation
- `QUICKSTART.md` - Updated with multi-provider quick start guide

### 🚀 New Features

#### Provider Management
- **Provider Status Tracking**: Track provider health and failure counts
- **Automatic Recovery**: Automatic recovery from failed states
- **Load Balancing**: Support for different load balancing strategies
- **Custom Headers**: Per-provider custom header configuration

#### Error Handling
- **Intelligent Fallback**: Automatic fallback to backup providers
- **Error Classification**: Better error classification and reporting
- **Circuit Breaker**: Prevent cascading failures
- **Health Checks**: Background monitoring of provider health

#### Monitoring and Observability
- **Provider Status API**: REST API for checking provider status
- **Colored Logging**: Beautiful terminal output with colors
- **Real-Time Switching**: Live notifications of provider switches
- **Configuration Validation**: Startup validation of provider configuration

### 📊 Performance Improvements

- **Connection Pooling**: Efficient connection management per provider
- **Timeout Configuration**: Per-provider timeout settings
- **Retry Logic**: Configurable retry attempts per provider
- **Health Monitoring**: Background health checks without blocking requests

### 🔧 Configuration Examples

#### Multi-Provider Setup
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
        "big": ["gpt-4o", "gpt-4-turbo"],
        "middle": ["gpt-4o", "gpt-4-turbo"],
        "small": ["gpt-4o-mini", "gpt-3.5-turbo"]
      }
    }
  ],
  "fallback_strategy": "priority",
  "circuit_breaker": {
    "failure_threshold": 5,
    "recovery_timeout": 60
  }
}
```

#### Legacy Configuration (Still Supported)
```bash
export OPENAI_API_KEY="sk-your-key"
export BIG_MODEL="gpt-4o"
export SMALL_MODEL="gpt-4o-mini"
```

### 🎯 Usage Examples

#### Basic Multi-Provider Usage
```bash
# Copy example configuration
cp config/providers.example.json config/providers.json

# Set API keys
export OPENAI_API_KEY="sk-your-key"
export AZURE_API_KEY="your-azure-key"

# Start proxy
python start_proxy.py
```

#### Legacy Usage (Unchanged)
```bash
# Set environment variables
export OPENAI_API_KEY="sk-your-key"
export BIG_MODEL="gpt-4o"

# Start proxy
python start_proxy.py
```

### 🔍 Monitoring

#### Health Check Endpoint
```bash
curl http://localhost:8082/health
```

#### Provider Status
```json
{
  "status": "healthy",
  "providers": {
    "openai": {
      "status": "healthy",
      "priority": 1,
      "failure_count": 0
    }
  }
}
```

### 🚨 Breaking Changes

- **None**: This update is fully backward compatible
- **Legacy Configuration**: Still fully supported
- **API Endpoints**: All existing endpoints work unchanged
- **Environment Variables**: All existing environment variables work unchanged

### 📚 Documentation Updates

- **README.md**: Updated with multi-provider features
- **QUICKSTART.md**: Updated with multi-provider quick start
- **MULTI_PROVIDER_GUIDE.md**: New comprehensive guide
- **CHANGELOG.md**: This changelog

### 🧪 Testing

- **Backward Compatibility**: Tested with legacy configuration
- **Multi-Provider**: Tested with multiple provider configurations
- **Fallback Logic**: Tested automatic fallback behavior
- **Error Handling**: Tested error scenarios and recovery

### 🎉 Migration Guide

#### From Legacy to Multi-Provider

1. **Backup Current Configuration**: Save your current `.env` file
2. **Create Provider Config**: Copy `config/providers.example.json` to `config/providers.json`
3. **Configure Providers**: Edit the JSON file with your API keys and models
4. **Test Configuration**: Start the proxy and verify it works
5. **Remove Legacy Config**: Once confirmed working, you can remove the `.env` file

#### Example Migration

**Before (Legacy):**
```bash
export OPENAI_API_KEY="sk-your-key"
export BIG_MODEL="gpt-4o"
export SMALL_MODEL="gpt-4o-mini"
```

**After (Multi-Provider):**
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

### 🔮 Future Enhancements

- **Load Balancing**: More sophisticated load balancing algorithms
- **Metrics**: Prometheus metrics for monitoring
- **Dashboard**: Web dashboard for provider management
- **Auto-Scaling**: Automatic provider scaling based on load
- **Cost Optimization**: Automatic cost-based provider selection

---

## [1.0.0] - 2024-12-18

### Initial Release
- Basic Claude to OpenAI proxy functionality
- Single provider configuration
- Environment variable configuration
- Streaming support
- Function calling support
- Image support
- Custom headers support


