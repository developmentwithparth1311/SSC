FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# WebSockets require sticky sessions if you run multiple workers.
# Default: single worker. Set UVICORN_WORKERS in orchestrator if you know what you're doing.
ENV ENV=production
EXPOSE 8000

# Cloud Run sets PORT (default 8080)
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]