#!/usr/bin/env python3
"""Start Claude Code Proxy server from backend directory."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the backend directory (where this script is located)
backend_dir = os.path.dirname(os.path.abspath(__file__))

# Get the claude_code_proxy directory
claude_code_proxy_dir = os.path.join(backend_dir, 'src', 'claude_code_proxy')

# Try to load .env from multiple locations:
# 1. backend/.env (most convenient for users)
# 2. backend/src/claude_code_proxy/.env
# 3. backend/src/claude_code_proxy/.env.example (fallback)
env_files_to_try = [
    Path(backend_dir) / ".env",
    Path(claude_code_proxy_dir) / ".env",
    Path(claude_code_proxy_dir) / ".env.example"
]

env_loaded = False
for env_file in env_files_to_try:
    if env_file.exists():
        load_dotenv(env_file)
        env_loaded = True
        if env_file.name == ".env.example":
            print(f"⚠️  Loaded environment variables from {env_file} (please create .env file)")
        else:
            print(f"✅ Loaded environment variables from {env_file}")
        break

if not env_loaded:
    # Try default behavior (load .env from current directory)
    load_dotenv()
    print("ℹ️  No .env or .env.example file found, using system environment variables")

# Change working directory to claude_code_proxy directory
# This is important for finding config files (config/providers.json)
os.chdir(claude_code_proxy_dir)

# Add the src directory to Python path so we can import src.main
# The uvicorn.run() expects "src.main:app" as module path
sys.path.insert(0, claude_code_proxy_dir)

# Import and run main function
from src.main import main

if __name__ == "__main__":
    main()

