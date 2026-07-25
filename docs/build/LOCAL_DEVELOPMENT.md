# Local Development

Acceptance bar (ROADMAP R0): a fresh contributor reaches a working full stack in one
sitting following only this doc.

## Required tools

Docker Desktop (or colima), Python 3.12 + uv, Node 20 + pnpm, Expo CLI (via pnpm),
git + git-lfs. Optional: Android Studio emulator / physical device with Expo Go;
Maestro for E2E.

## Setup

```bash
git clone <repo> && cd snapnutrition
cp configs/.env.example .env             # fill nothing to start; defaults target compose services
uv sync --all-packages                   # python workspace deps (all members, editable)
pnpm install                             # TS workspace deps (no-op until TS packages land)
docker compose -f docker/compose.yaml up -d   # postgres(+pgvector) + minio (+ bucket init)
uv run alembic upgrade head              # migrations (available from T-006)
uv run python scripts/seed_dev.py        # nutrients, DV table, mappings, ontology,
                                         # demo fixtures, dev user (dev@local / password printed) — from T-025
```

If host port 5432/9000/9001/8000 is already in use, override it, e.g.:
`POSTGRES_HOST_PORT=5433 docker compose -f docker/compose.yaml up -d`
(also `MINIO_API_PORT`, `MINIO_CONSOLE_PORT`, `API_HOST_PORT`).

Verify the stack (T-003):
`SNAP_INTEGRATION=1 uv run pytest -m integration`
(add `POSTGRES_HOST_PORT=5433` etc. if you overrode any port).

## Running things

| What | Command | Notes |
|---|---|---|
| API (+in-process workers) | `uv run uvicorn snap_api.main:app --reload` | http://localhost:8000/docs |
| Worker role separately | `ROLE=worker uv run python -m apps.api.src.jobs.runner` | optional (compose profile `worker`) |
| Mobile | `pnpm --filter mobile start` → Expo Go scan QR | set `EXPO_PUBLIC_API_URL` to your LAN IP |
| Web demo | `pnpm --filter web-demo dev` | http://localhost:5173 |
| Model inference locally | automatic — dev model artifact auto-downloaded on first API boot (`configs/serving_model.lock`, falls back to the CI micro-model if W&B unreachable → predictions labeled `dev-micro-model`) | no GPU needed (ONNX CPU) |
| ML work | `uv run python -m ml.datasets.food101 download --subset 5` etc. | full dataset optional locally; Kaggle for real training |
| Tests | `uv run pytest` · `pnpm test` · `uv run pytest tests/e2e -m smoke` | CI mirrors these |
| Lint/type | `uv run ruff check && uv run pyright` · `pnpm lint` | pre-commit runs the fast subset |

## Seed data

`seed_dev.py` is idempotent: canonical nutrients + DV table, 101 class→FDC mappings
with cached FDC payloads (bundled snapshot — dev works offline), class→allergen
hints, ontology load, OCR/allergen fixtures registered, dev + demo users, 3 sample
scans. `seed_demo.py` (staging/beta) is the demo-account subset (DEMO_DATA).

## Gotchas documented up front

Expo Go on device needs the API on the same network (LAN IP, not localhost); MinIO
console at :9001 (dev creds in compose); email verification in dev prints links to
API logs (console email backend); first API boot downloads the dev model (~seconds
on the micro-model).
