FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Hugging Face Spaces only guarantees /tmp is writable for the runtime user,
    # so point HOME / caches there (yt-dlp writes a cache under $XDG_CACHE_HOME).
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    # Hugging Face routes to this port (must match `app_port` in README.md).
    PORT=7860

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Run as a non-root user (Hugging Face best practice).
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
