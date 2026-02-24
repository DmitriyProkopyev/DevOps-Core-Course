FROM python:3.14.3-slim

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app.py app_stats.py /app

USER appuser

RUN cat > /app/healthcheck.py << 'EOF'
import os
import urllib.request
import json
import sys
url = 'http://localhost:5000/health'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=4) as resp:
    if resp.status != 200:
        sys.exit(1)
    data = json.loads(resp.read().decode())
    sys.exit(0 if data.get('status') in ('healthy', 'ok') else 1)
EOF
RUN chown appuser /app/healthcheck.py

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python /app/healthcheck.py

ARG MAJOR_VERSION
ARG MINOR_VERSION
ARG PATCH_VERSION

ENV MAJOR_VERSION=${MAJOR_VERSION} \
    MINOR_VERSION=${MINOR_VERSION} \
    PATCH_VERSION=${PATCH_VERSION}

EXPOSE 5000

CMD ["python", "app.py"]
