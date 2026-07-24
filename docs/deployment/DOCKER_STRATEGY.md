# Docker Strategy

## Images

| Image | Contents | Notes |
|---|---|---|
| **`api`** (the deployable) | FastAPI app + in-process workers + ONNX Runtime + PaddleOCR + models baked at build | Multi-stage: builder (uv/pip wheels) → slim runtime (python:3.12-slim); no torch in runtime (ONNX only, ONNX_STRATEGY); target < 2.5 GB with models; non-root user; healthcheck `/healthz` |
| `worker` | **same image**, `ROLE=worker` env (no separate build) | ASYNC_JOB_DESIGN escape hatch |
| `ocr` (optional profile) | OCR-only service split | Only if profiling shows interference (INFERENCE_DEPLOYMENT); compose profile exists, unused by default |
| local Postgres | `pgvector/pgvector:pg16` | Compose |
| local object storage | `minio/minio` | S3-compatible like R2 |
| `ml` (dev/CI only) | torch + training deps | For local ML work + CI smoke training; never deployed |

## Compose (local)

`docker compose up` → api (hot-reload bind mount), postgres (+init: extensions,
seeds), minio (+bucket bootstrap). Profiles: `worker` (separate worker), `ocr`
(split OCR). `.env` from `.env.example`. One command to a working stack
(LOCAL_DEVELOPMENT acceptance).

## Build discipline

- Lockfile-driven installs (uv); BuildKit cache mounts for pip/uv; layer order:
  deps → models → code (code changes don't re-download models).
- Models pulled at build from W&B artifact (pinned version arg) — image tag encodes
  `app-{gitsha}-model-{version}`.
- Image scanning (Trivy) in CI; base images pinned by digest; monthly rebuild cron
  for patch pickup.
- SBOM generated (syft) and attached to releases — cheap supply-chain credibility.

## Registry & deploy

GHCR (free) as registry; HF Space pulls/builds from repo Dockerfile (Space variant
builds in-place — the Dockerfile stays the single source); AWS design pushes same
image to ECR.
