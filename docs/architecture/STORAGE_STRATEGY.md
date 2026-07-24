# Storage Strategy

## What lives where

| Store | Holds | Never holds |
|---|---|---|
| **PostgreSQL** (free tier: see pick below) | All relational entities (DATA_MODEL), job queue, external-API cache, audit | Raw images, model files |
| **pgvector** (same Postgres) | Corpus chunk embeddings only (public content) | **User-content embeddings** (privacy boundary, RAG_ARCHITECTURE) |
| **Object storage (S3-compatible)** | Original images, thumbnails, export archives | Anything needing queries |
| **Redis/cache** | **Not used in MVP** (Postgres cache table + in-process LRU suffice; one less dependency). Slot documented for AWS design (ElastiCache) | — |
| **W&B (free tier)** | Experiment runs, dataset manifests, model checkpoints/artifacts, evaluation reports | User data of any kind |
| **Model artifacts in serving** | Baked into container image at build (INFERENCE_DEPLOYMENT) | — |
| **Local mobile storage** | JWT (SecureStore), profile cache, last-N history cache (encrypted-at-rest by OS), pending-upload queue | Other users' data; long-term images |

## Free-tier picks (D6 🟡 — recommendation + rationale)

- **Postgres: Neon free tier** (0.5 GB storage, autosuspend, pgvector supported,
  branching for dev). Chosen over Supabase-as-Postgres because we self-build auth
  (D22) and want plain Postgres semantics; Supabase remains the noted alternative
  if its bundled storage proves decisive.
- **Object storage: Cloudflare R2 free tier** (10 GB, S3-compatible API, zero egress
  fees). Chosen over Supabase Storage (1 GB) for headroom and S3-API compatibility
  (the AWS-target design ports without code change — S3 client + endpoint override).
- **API/container host: Hugging Face Spaces (Docker Space, free CPU basic:
  2 vCPU/16 GB)** — fits the model+OCR memory footprint; sleeps when idle
  (keep-warm mitigations per INFERENCE_DEPLOYMENT).
  **⚠️ `[VERIFY HF ToS — gate before T-059]`** (ADVERSARIAL_REVIEW 2.1): confirm
  that hosting an authenticated user-facing API with stored user data is within
  Hugging Face Spaces' intended use/terms. If not: fallbacks are Render free tier
  (512 MB RAM — likely too tight for OCR+ORT in one container; would force the
  split-OCR compose profile or model-only hosting on HF with the API on Render) or
  an owner-machine tunnel for beta. Decision recorded in DECISION_LOG when made.
- All three sit behind interfaces (SQLAlchemy URL, S3 client config, container
  host-agnostic Docker) — the picks are config, not architecture.

## Capacity sanity (beta scale)

10 testers × 5 scans/wk × ~2 MB ≈ 100 MB/quarter object storage (R2: fine);
DB rows trivial (<<0.5 GB, biggest risk is external_cache jsonb — TTL sweeps cap it);
W&B: rolling checkpoint cleanup keeps <100 GB (TRAINING_PLAN).

## Backups & durability (beta posture, honest)

Neon free retains a limited history window (point-in-time restore days-level);
weekly `pg_dump` via GitHub Actions cron → encrypted artifact in R2 (`backups/`
prefix, 90-day retention). R2 objects: no versioning in MVP (cost of loss = one
user's images; accepted, documented). This is a beta posture — the AWS design
(RDS automated backups + S3 versioning) upgrades it.

## Migration path to AWS (documented, not deployed)

Neon → RDS PostgreSQL (pg_dump/restore), R2 → S3 (rclone; same API), HF Space →
ECS Fargate (same image), Postgres queue → SQS (interface swap). No code rewrites —
this portability was a design constraint.
