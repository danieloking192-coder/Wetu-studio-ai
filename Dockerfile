FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WETU_HOST=0.0.0.0 \
    WETU_PORT=8787

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg clamav clamav-freshclam \
    && freshclam || true\n    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 wetu \
    && mkdir -p /app/.wetu \
    && chown -R wetu:wetu /app

USER wetu

EXPOSE 8787

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/api/runtime/health', timeout=3)"

CMD ["python", "-c", "import os; from wetu_studio.creator_server import serve; serve(os.environ.get('WETU_HOST','0.0.0.0'), int(os.environ.get('WETU_PORT','8787')))"]
