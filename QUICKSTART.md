# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Step 2: Configure Your Provider(s)

Choose your configuration method:

#### Option A: Multi-Provider Configuration (Recommended)

```bash
# Copy the example configuration
cp config/providers.example.json config/providers.json

# Set your API keys
export OPENAI_API_KEY="sk-your-openai-key"
export AZURE_API_KEY="your-azure-key"
export AZURE_BASE_URL="https://your-resource.openai.azure.com"

# Edit config/providers.json to enable/disable providers
```

#### Option B: Single Provider (Legacy)

**OpenAI:**
```bash
cp .env.example .env
# Edit .env:
# OPENAI_API_KEY="sk-your-openai-key"
# BIG_MODEL="gpt-4o"
# SMALL_MODEL="gpt-4o-mini"
```

**Azure OpenAI:**
```bash
cp .env.example .env
# Edit .env:
# OPENAI_API_KEY="your-azure-key"
# OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/deployments/your-deployment"
# BIG_MODEL="gpt-4"
# SMALL_MODEL="gpt-35-turbo"
```

**Local Models (Ollama):**
```bash
cp .env.example .env
# Edit .env:
# OPENAI_API_KEY="dummy-key"
# OPENAI_BASE_URL="http://localhost:11434/v1"
# BIG_MODEL="llama3.1:70b"
# SMALL_MODEL="llama3.1:8b"
```

### Step 3: Start and Use

```bash
# Start the proxy server
python start_proxy.py

# In another terminal, use with Claude Code
ANTHROPIC_BASE_URL=http://localhost:8082 claude
```

## 🎯 How It Works

### Multi-Provider Mode

| Your Input | Proxy Action | Result |
|-----------|--------------|--------|
| Claude Code sends `claude-3-5-sonnet-20241022` | Selects highest priority provider with `big` models | Uses first available model (e.g., `gpt-4o`) |
| Claude Code sends `claude-3-5-haiku-20241022` | Selects highest priority provider with `small` models | Uses first available model (e.g., `gpt-4o-mini`) |
| Provider fails | Automatically switches to next priority provider | Seamless fallback to backup provider |
| Model fails | Tries next model in same provider | Automatic model failover |

### Legacy Single-Provider Mode

| Your Input | Proxy Action | Result |
|-----------|--------------|--------|
| Claude Code sends `claude-3-5-sonnet-20241022` | Maps to your `BIG_MODEL` | Uses `gpt-4o` (or whatever you configured) |
| Claude Code sends `claude-3-5-haiku-20241022` | Maps to your `SMALL_MODEL` | Uses `gpt-4o-mini` (or whatever you configured) |

## 📋 What You Need

- Python 3.9+
- API key(s) for your chosen provider(s)
- Claude Code CLI installed
- 2 minutes to configure

## 🔧 Default Settings

### Multi-Provider Mode
- Server runs on `http://localhost:8082`
- Automatic provider selection based on priority
- Automatic fallback when providers fail
- Colored terminal output for better visibility
- Circuit breaker pattern for failed providers

### Legacy Mode
- Server runs on `http://localhost:8082`
- Maps haiku → SMALL_MODEL, sonnet/opus → BIG_MODEL
- Single provider configuration

### Both Modes Support
- Streaming responses
- Function calling
- Image support
- Custom headers

## 🧪 Test Your Setup
```bash
# Quick test
python src/test_claude_to_openai.py
```

That's it! Now Claude Code can use any OpenAI-compatible provider! 🎉