# Claude Code Proxy

A proxy server that enables **Claude Code** to work with OpenAI-compatible API providers. Convert Claude API requests to OpenAI API calls, allowing you to use various LLM providers through the Claude Code CLI.

![Claude Code Proxy](demo.png)

## Features

- **Full Claude API Compatibility**: Complete `/v1/messages` endpoint support
- **Multi-Provider Support**: Support for multiple LLM providers with automatic fallback
- **Smart Model Mapping**: Configure multiple models per provider with automatic failover
- **Provider Management**: Priority-based provider selection with circuit breaker pattern
- **Colored Logging**: Beautiful colored terminal output for better visibility
- **Function Calling**: Complete tool use support with proper conversion
- **Streaming Responses**: Real-time SSE streaming support
- **Image Support**: Base64 encoded image input
- **Custom Headers**: Automatic injection of custom HTTP headers for API requests
- **Error Handling**: Comprehensive error handling with automatic provider switching
- **Backward Compatibility**: Full support for legacy environment variable configuration

## Quick Start

### 1. Install Dependencies

```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Configure

#### Option A: Multi-Provider Configuration (Recommended)

```bash
# Copy the example provider configuration
cp config/providers.example.json config/providers.json

# Edit config/providers.json and configure your providers
# Set your API keys as environment variables
export OPENAI_API_KEY="sk-your-openai-key"
export AZURE_API_KEY="your-azure-key"
export AZURE_BASE_URL="https://your-resource.openai.azure.com"
```

#### Option B: Legacy Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API configuration
# Note: Environment variables are automatically loaded from .env file
```

### 3. Start Server

```bash
# Direct run
python start_proxy.py

# Or with UV
uv run claude-code-proxy

# Or with docker compose
docker compose up -d
```

### 4. Use with Claude Code

```bash
# If ANTHROPIC_API_KEY is not set in the proxy:
ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_API_KEY="any-value" claude

# If ANTHROPIC_API_KEY is set in the proxy:
ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_API_KEY="exact-matching-key" claude
```

## Configuration

The application supports two configuration methods:

1. **Multi-Provider Configuration** (Recommended): JSON-based configuration with multiple providers
2. **Legacy Environment Variables**: Traditional environment variable configuration

### Multi-Provider Configuration

The application automatically detects and loads provider configuration from:
- `config/providers.json`
- `providers.json` 
- `config/providers.example.json` (fallback)

#### Provider Configuration Format

```json
{
  "providers": [
    {
      "name": "openai",
      "enabled": true,
      "priority": 1,
      "api_key": "${OPENAI_API_KEY}",
      "base_url": "https://api.openai.com/v1",
      "api_version": null,
      "timeout": 90,
      "max_retries": 3,
      "custom_headers": {},
      "models": {
        "big": ["gpt-4o", "gpt-4-turbo"],
        "middle": ["gpt-4o", "gpt-4-turbo"],
        "small": ["gpt-4o-mini", "gpt-3.5-turbo"]
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

#### Provider Configuration Options

- **name**: Unique provider identifier
- **enabled**: Whether the provider is active
- **priority**: Lower numbers = higher priority (1 is highest)
- **api_key**: API key (supports `${ENV_VAR}` substitution)
- **base_url**: API endpoint URL
- **api_version**: API version (for Azure OpenAI)
- **timeout**: Request timeout in seconds
- **max_retries**: Maximum retry attempts
- **custom_headers**: Additional HTTP headers
- **models**: Model lists for different sizes (big/middle/small)

#### Fallback Strategy

- **priority**: Use providers in priority order (default)
- **round_robin**: Rotate between available providers
- **random**: Randomly select from available providers

#### Circuit Breaker

- **failure_threshold**: Number of failures before disabling provider
- **recovery_timeout**: Seconds to wait before retrying disabled provider

### Legacy Environment Variables

The application automatically loads environment variables from a `.env` file in the project root using `python-dotenv`. You can also set environment variables directly in your shell.

### Environment Variables

**Required:**

- `OPENAI_API_KEY` - Your API key for the target provider

**Security:**

- `ANTHROPIC_API_KEY` - Expected Anthropic API key for client validation
  - If set, clients must provide this exact API key to access the proxy
  - If not set, any API key will be accepted

**Model Configuration:**

- `BIG_MODEL` - Model for Claude opus requests (default: `gpt-4o`)
- `MIDDLE_MODEL` - Model for Claude opus requests (default: `gpt-4o`)
- `SMALL_MODEL` - Model for Claude haiku requests (default: `gpt-4o-mini`)

**API Configuration:**

- `OPENAI_BASE_URL` - API base URL (default: `https://api.openai.com/v1`)

**Server Settings:**

- `HOST` - Server host (default: `0.0.0.0`)
- `PORT` - Server port (default: `8082`)
- `LOG_LEVEL` - Logging level (default: `WARNING`)

**Performance:**

- `MAX_TOKENS_LIMIT` - Token limit (default: `4096`)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: `90`)

**Custom Headers:**

- `CUSTOM_HEADER_*` - Custom headers for API requests (e.g., `CUSTOM_HEADER_ACCEPT`, `CUSTOM_HEADER_AUTHORIZATION`)
  - Uncomment in `.env` file to enable custom headers

### Custom Headers Configuration

Add custom headers to your API requests by setting environment variables with the `CUSTOM_HEADER_` prefix:

```bash
# Uncomment to enable custom headers
# CUSTOM_HEADER_ACCEPT="application/jsonstream"
# CUSTOM_HEADER_CONTENT_TYPE="application/json"
# CUSTOM_HEADER_USER_AGENT="your-app/1.0.0"
# CUSTOM_HEADER_AUTHORIZATION="Bearer your-token"
# CUSTOM_HEADER_X_API_KEY="your-api-key"
# CUSTOM_HEADER_X_CLIENT_ID="your-client-id"
# CUSTOM_HEADER_X_CLIENT_VERSION="1.0.0"
# CUSTOM_HEADER_X_REQUEST_ID="unique-request-id"
# CUSTOM_HEADER_X_TRACE_ID="trace-123"
# CUSTOM_HEADER_X_SESSION_ID="session-456"
```

### Header Conversion Rules

Environment variables with the `CUSTOM_HEADER_` prefix are automatically converted to HTTP headers:

- Environment variable: `CUSTOM_HEADER_ACCEPT`
- HTTP Header: `ACCEPT`

- Environment variable: `CUSTOM_HEADER_X_API_KEY`
- HTTP Header: `X-API-KEY`

- Environment variable: `CUSTOM_HEADER_AUTHORIZATION`
- HTTP Header: `AUTHORIZATION`

### Supported Header Types

- **Content Type**: `ACCEPT`, `CONTENT-TYPE`
- **Authentication**: `AUTHORIZATION`, `X-API-KEY`
- **Client Identification**: `USER-AGENT`, `X-CLIENT-ID`, `X-CLIENT-VERSION`
- **Tracking**: `X-REQUEST-ID`, `X-TRACE-ID`, `X-SESSION-ID`

### Usage Example

```bash
# Basic configuration
OPENAI_API_KEY="sk-your-openai-api-key-here"
OPENAI_BASE_URL="https://api.openai.com/v1"

# Enable custom headers (uncomment as needed)
CUSTOM_HEADER_ACCEPT="application/jsonstream"
CUSTOM_HEADER_CONTENT_TYPE="application/json"
CUSTOM_HEADER_USER_AGENT="my-app/1.0.0"
CUSTOM_HEADER_AUTHORIZATION="Bearer my-token"
```

The proxy will automatically include these headers in all API requests to the target LLM provider.

### Model Mapping

#### Multi-Provider Configuration

The proxy maps Claude model requests to your configured models based on provider priority and availability:

| Claude Request                 | Model Type    | Provider Selection     | Fallback Behavior      |
| ------------------------------ | ------------- | ---------------------- | ---------------------- |
| Models with "haiku"            | `small`       | First available provider| Try next provider if failed |
| Models with "sonnet"           | `middle`      | First available provider| Try next provider if failed |
| Models with "opus"             | `big`         | First available provider| Try next provider if failed |

#### Legacy Configuration

| Claude Request                 | Mapped To     | Environment Variable   |
| ------------------------------ | ------------- | ---------------------- |
| Models with "haiku"            | `SMALL_MODEL` | Default: `gpt-4o-mini` |
| Models with "sonnet"           | `MIDDLE_MODEL`| Default: `BIG_MODEL`   |
| Models with "opus"             | `BIG_MODEL`   | Default: `gpt-4o`      |

### Multi-Provider Examples

#### Complete Multi-Provider Setup

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
        "big": ["llama3.1:70b", "llama3.1:8b"],
        "middle": ["llama3.1:70b", "llama3.1:8b"],
        "small": ["llama3.1:8b", "llama3.1:7b"]
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

#### Provider-Specific Examples

**OpenAI Provider:**
```json
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
```

**Azure OpenAI Provider:**
```json
{
  "name": "azure",
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
}
```

**Local Ollama Provider:**
```json
{
  "name": "ollama",
  "enabled": true,
  "priority": 3,
  "api_key": "dummy-key",
  "base_url": "http://localhost:11434/v1",
  "models": {
    "big": ["llama3.1:70b", "llama3.1:8b"],
    "middle": ["llama3.1:70b", "llama3.1:8b"],
    "small": ["llama3.1:8b", "llama3.1:7b"]
  }
}
```

**Custom Provider:**
```json
{
  "name": "custom-api",
  "enabled": true,
  "priority": 4,
  "api_key": "${CUSTOM_API_KEY}",
  "base_url": "${CUSTOM_BASE_URL}",
  "custom_headers": {
    "Authorization": "Bearer ${CUSTOM_TOKEN}",
    "X-Custom-Header": "custom-value"
  },
  "models": {
    "big": ["custom-model-1"],
    "middle": ["custom-model-2"],
    "small": ["custom-model-3"]
  }
}
```

### Legacy Provider Examples

#### OpenAI

```bash
OPENAI_API_KEY="sk-your-openai-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
BIG_MODEL="gpt-4o"
MIDDLE_MODEL="gpt-4o"
SMALL_MODEL="gpt-4o-mini"
```

#### Azure OpenAI

```bash
OPENAI_API_KEY="your-azure-key"
OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
BIG_MODEL="gpt-4"
MIDDLE_MODEL="gpt-4"
SMALL_MODEL="gpt-35-turbo"
```

#### Local Models (Ollama)

```bash
OPENAI_API_KEY="dummy-key"  # Required but can be dummy
OPENAI_BASE_URL="http://localhost:11434/v1"
BIG_MODEL="llama3.1:70b"
MIDDLE_MODEL="llama3.1:70b"
SMALL_MODEL="llama3.1:8b"
```

#### Other Providers

Any OpenAI-compatible API can be used by setting the appropriate `OPENAI_BASE_URL`.

## Usage Examples

### Basic Chat

```python
import httpx

response = httpx.post(
    "http://localhost:8082/v1/messages",
    json={
        "model": "claude-3-5-sonnet-20241022",  # Maps to MIDDLE_MODEL
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)
```

## Multi-Provider Features

### Automatic Fallback

The proxy automatically handles provider failures with intelligent fallback:

1. **Provider-Level Fallback**: If a provider fails, automatically switches to the next priority provider
2. **Model-Level Fallback**: If a specific model fails, tries the next model in the same provider
3. **Circuit Breaker**: Temporarily disables failed providers to prevent cascading failures
4. **Health Monitoring**: Background health checks with automatic recovery

### Colored Logging

The proxy provides beautiful colored terminal output for better visibility:

- **Provider Names**: Each provider has a unique color for easy identification
- **Status Indicators**: ✅ healthy, ❌ error, ⚠️ warning, ℹ️ info
- **Model Information**: Clear categorization of BIG/MIDDLE/SMALL models
- **Fallback Notifications**: Real-time notifications when switching providers

### Provider Status Monitoring

Monitor provider health and status:

```bash
# Check provider status via API
curl http://localhost:8082/health

# Response includes provider status information
{
  "status": "healthy",
  "providers": {
    "openai": {
      "status": "healthy",
      "priority": 1,
      "failure_count": 0
    },
    "azure": {
      "status": "circuit_open",
      "priority": 2,
      "failure_count": 5
    }
  }
}
```

### Configuration Validation

The proxy validates your configuration on startup:

- **Provider Validation**: Checks API keys and endpoints
- **Model Validation**: Verifies model availability
- **Configuration Display**: Shows all configured providers with colored output
- **Error Reporting**: Clear error messages for configuration issues

## Integration with Claude Code

This proxy is designed to work seamlessly with Claude Code CLI:

```bash
# Start the proxy
python start_proxy.py

# Use Claude Code with the proxy
ANTHROPIC_BASE_URL=http://localhost:8082 claude

# Or set permanently
export ANTHROPIC_BASE_URL=http://localhost:8082
claude
```

## Testing

Test proxy functionality:

```bash
# Run comprehensive tests
python src/test_claude_to_openai.py
```

## Development

### Using UV

```bash
# Install dependencies
uv sync

# Run server
uv run claude-code-proxy

# Format code
uv run black src/
uv run isort src/

# Type checking
uv run mypy src/
```

### Project Structure

```
claude-code-proxy/
├── src/
│   ├── main.py                     # Main server
│   ├── test_claude_to_openai.py    # Tests
│   └── [other modules...]
├── start_proxy.py                  # Startup script
├── .env.example                    # Config template
└── README.md                       # This file
```

## Performance

- **Async/await** for high concurrency
- **Connection pooling** for efficiency
- **Streaming support** for real-time responses
- **Configurable timeouts** and retries
- **Smart error handling** with detailed logging

## License

MIT License
