# Backend Dockerfile for FastAPI
FROM python:3.11-slim

WORKDIR /app

# Install wget for health checks
RUN apt-get update && apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements file first for better caching
COPY src/claude_code_proxy/requirements.txt /app/requirements.txt

# Install production dependencies only (skip dev dependencies marked with #)
# Using Tsinghua PyPI mirror for faster downloads in China
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    fastapi[standard]>=0.115.11 \
    uvicorn>=0.34.0 \
    pydantic>=2.0.0 \
    python-dotenv>=1.0.0 \
    openai>=1.54.0

# Copy backend source code
COPY src/claude_code_proxy /app

# Ensure config directory exists for volume mount
RUN mkdir -p /app/config

# Health check using wget with GET method (endpoint only supports GET, not HEAD)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 -O- http://localhost:8082/health >/dev/null 2>&1 || exit 1

# Start the backend server using start_proxy.py
CMD ["python", "start_proxy.py"]

