"""Claude Code Proxy

A proxy server that enables Claude Code to work with OpenAI-compatible API providers.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Try .env first, fall back to .env.example if .env doesn't exist
env_file = Path(".env")
env_example_file = Path(".env.example")

if env_file.exists():
    load_dotenv(env_file)
elif env_example_file.exists():
    # Use .env.example if .env doesn't exist
    load_dotenv(env_example_file)
else:
    # Try default behavior (load .env from current directory)
    load_dotenv()

__version__ = "1.0.0"
__author__ = "Claude Code Proxy"
