"""Application entrypoint.

Wires the FastAPI app: request-id middleware, canonical error handlers, health
probes, and the domain routers as they are implemented (see BUILD_SEQUENCE).
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from snap_api import __version__
from snap_api.core.errors import register_error_handlers
from snap_api.identity.router import router as identity_router

app = FastAPI(
    title="SnapNutrition API",
    version=__version__,
    docs_url="/docs",
)


@app.middleware("http")
async def request_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Attach a request id used in the error envelope and returned as a header."""
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


register_error_handlers(app)
app.include_router(identity_router)


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    """Liveness probe. Returns ok when the process is serving."""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
async def readyz() -> dict[str, str]:
    """Readiness probe.

    As modules land (DB, model session), this will report 'not ready' until each
    dependency is confirmed (docs/architecture/INFERENCE_DEPLOYMENT.md).
    """
    return {"status": "ready"}
