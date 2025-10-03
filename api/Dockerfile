# ========= Build image untuk Backend API (FastAPI + Uvicorn) =========
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000

WORKDIR /app

# System deps (openssl, curl untuk healthcheck, build deps minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Requirements (tetap terpisah agar layer cache efektif)
# Anda bisa menaruh requirements.txt di /api/requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY . /app

# Non-root user (good practice)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Jalankan Uvicorn (1 worker cukup untuk demo; di production pakai gunicorn+uvicorn workers)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
