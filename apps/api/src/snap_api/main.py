"""Application entrypoint.

T-001 scaffold: a minimal FastAPI app exposing liveness/readiness probes. Routers
for the domain modules are wired in as they are implemented (see BUILD_SEQUENCE).
"""

from fastapi import FastAPI

from snap_api import __version__

app = FastAPI(
    title="SnapNutrition API",
    version=__version__,
    docs_url="/docs",
)


@app.get("/healthz", tags=["health"])
async def healthz() -> dict[str, str]:
    """Liveness probe. Returns ok when the process is serving."""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
async def readyz() -> dict[str, str]:
    """Readiness probe.

    T-001 has no external dependencies to check yet. As modules land (DB, model
    session), this reports 'not ready' until each dependency is confirmed
    (see docs/architecture/INFERENCE_DEPLOYMENT.md — readiness gates traffic).
    """
    return {"status": "ready"}
