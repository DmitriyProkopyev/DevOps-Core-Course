FROM python:3.13-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.10.5 /uv /bin/uv

COPY pyproject.toml uv.lock /app
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \ 
	uv sync --no-dev --locked --no-install-project --no-editable


FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=appuser:appuser app.py app_stats.py healthcheck.py /app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python /app/healthcheck.py

ARG MAJOR_VERSION
ARG MINOR_VERSION
ARG PATCH_VERSION

ENV MAJOR_VERSION=${MAJOR_VERSION} \
    MINOR_VERSION=${MINOR_VERSION} \
    PATCH_VERSION=${PATCH_VERSION}

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "1"]
