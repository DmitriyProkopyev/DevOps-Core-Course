FROM python:3.14.3-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip

RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app.py .

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
  CMD python -c "import urllib.request, json; urllib.request.urlopen('http://localhost:5000/health', timeout=5)" || exit 1

EXPOSE 5000

CMD ["python", "app.py"]
