# SnapNutrition API image (T-003 v1: API only; models are baked in a later task).
# Multi-stage: build a venv with uv, then copy into a slim, non-root runtime.
# See docs/deployment/DOCKER_STRATEGY.md.

FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Workspace metadata + lockfile first (better layer caching).
COPY pyproject.toml uv.lock ./
COPY packages/shared-schemas/pyproject.toml packages/shared-schemas/
COPY packages/nutrition-core/pyproject.toml packages/nutrition-core/
COPY packages/allergen-core/pyproject.toml packages/allergen-core/
COPY packages/preprocessing/pyproject.toml packages/preprocessing/
COPY apps/api/pyproject.toml apps/api/

# Source for the API and the packages it depends on.
COPY packages/ packages/
COPY apps/api/ apps/api/

# Install only the API package + its workspace deps, no dev tooling.
RUN uv sync --frozen --no-dev --package snap-api


FROM python:3.12-slim AS runtime

# Non-root runtime user.
RUN groupadd --system app && useradd --system --gid app --home /app app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    ENV=local

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz').status==200 else 1)"

CMD ["uvicorn", "snap_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
