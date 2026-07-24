# Backend Architecture

**Modular monolith** (per working rules + ARCHITECTURE_DECISIONS AD-7): one FastAPI
application, one deployable container, strict internal module boundaries enforced by
import-linting (modules may import `shared` and other modules' `public.py` interface
only). Async workers run **in-process** in MVP behind a queue interface
(ASYNC_JOB_DESIGN) so the same code deploys as separate workers later.

## Why not microservices / Kubernetes

One team (Implementer + owner), one free-tier host, coupled domain logic, no independent
scaling needs at beta scale. Microservices would add network failure modes, deploy
complexity, and cost — without one concrete benefit today. The module boundaries
below are the future service seams if scale ever demands it. Kubernetes is
explicitly rejected as résumé-driven complexity.

## Module catalog

Layout: `apps/api/src/{module}/` each with `router.py` (HTTP), `service.py` (logic),
`repo.py` (DB), `models.py` (ORM), `public.py` (cross-module interface), `jobs.py`
(async tasks).

| Module | Responsibility | Owned data | Depends on | Jobs | Security boundary | Failure behavior | Test focus |
|---|---|---|---|---|---|---|---|
| **identity** | signup, login, JWT issue/refresh/revoke, email verification, password reset | users, sessions, verification tokens | — | token cleanup | Public endpoints; rate-limited; lockout | Auth down = app down (accepted; no degraded auth) | authz matrix, lockout, token rotation |
| **profiles** | dietary profiles, allergens, diet rules, managed sub-profiles, consents | profiles, user_allergens, preferences, consent records | identity | — | Health-adjacent data: strict user-scoping, no logs | Profile unavailable → scans proceed, allergen views show "profile unavailable" (never empty-profile = no warnings!) | isolation tests; the fail-state test |
| **scans** | scan lifecycle state machine, orchestration of pipeline stages, results assembly | scans, scan states, results refs | images, inference, ocr, nutrition, allergens | pipeline orchestration | User-scoped | State machine: any stage failure → visible failed state with retry | state transitions, idempotency |
| **images** | upload, validation, storage, lifecycle | image records | identity | EXIF strip, thumbnail, deletion sweeps | UPLOAD_SECURITY rules | Upload fail → clear error, no orphan records | signature/size/pixel gates |
| **inference** | classifier serving (ONNX Runtime session), calibration, thresholds, model metadata | inference events, model version registry mirror | images | (runs in worker) | Internal only | Model load fail at boot → readiness fails (no silent fallback model) | parity, threshold, latency |
| **ocr** | OCR pipeline stages, parsing, extraction | ocr results, fields, corrections | images | OCR job | Internal | `ocr_failed` state; allergen demotion to INSUFFICIENT | fixture pipeline tests |
| **nutrition** | FDC/OFF clients, cache, class→FDC mapping, serving math (via nutrition-core) | nutrition records cache, mappings, servings | — | cache refresh, seed | External API keys server-side only | Provider down → cached-only + notice | golden math, cache, fallback |
| **allergens** | ontology load, matcher, evidence assembly, diet rules (via allergen-core) | allergen evidence, ontology version records | ocr, nutrition, profiles | — | **Safety-critical module**: changes gated by safety checklist | Matcher error → INSUFFICIENT (never silent pass) | full ALLERGEN_TESTS |
| **products** | barcode lookup, OFF integration, product cache | products, brands, barcodes | nutrition | OFF refresh | — | OFF down → cache or "unavailable" | staleness flags |
| **assistant** | threads, LLM provider adapter, tool registry, validators, RAG retrieval | conversations, messages, citations | scans, allergens, nutrition, profiles (via tools) | ingestion (corpus) | PROMPT_INJECTION_DEFENSE layers; provider key server-side | Quota/timeout → deterministic fallback summary | AI_EVALUATION deterministic tier |
| **history** | list/detail/delete of scans, export assembly | (reads others' data; owns export archives) | scans | export job, deletion job | User-scoped; export links signed + expiring | Export fail → job visible-failed, retryable | deletion completeness sweep |
| **feedback** | corrections, confirmations, training-consent gating, annotation queue (R5) | corrections, feedback events | scans, profiles(consent) | dataset build prep | Consent enforcement in queries (not app-layer if-s alone: view filters) | — | consent-gating proofs |
| **registry** | model version metadata, promotion state mirror (W&B is source of truth) | model_versions | — | — | Admin-only writes | — | promotion gate checks |
| **admin** | read-only ops endpoints (model status, error rates, queue depth) | — | observability data | — | Role-gated (admin role) | — | authz |
| **audit** | append-only audit events (consent, deletion, export, admin actions, authz denials) | audit_events | all (writes) | retention sweep | Append-only; no updates/deletes | Audit write failure → operation fails (for consent/deletion class events) | immutability |
| **jobs** | queue interface, runner, retries, idempotency keys | job records | all | — | — | ASYNC_JOB_DESIGN | retry/idempotency |
| **notifications** | (reserved, empty in MVP) | — | — | — | — | — | — |

## Cross-cutting

- **shared-schemas package:** Pydantic models for every API payload + enum
  (status codes from ALLERGEN_POLICY, scan states); TS types generated from OpenAPI
  for mobile/web (single source of truth).
- **Config:** pydantic-settings; 12-factor env; secrets never in code
  (SECRET_MANAGEMENT).
- **DB:** SQLAlchemy 2.x async + Alembic migrations; pgvector extension.
- **Observability:** structlog JSON logs w/ request_id, job_id, model_version;
  metrics endpoints (OBSERVABILITY).
- **Error envelope:** uniform `{error: {code, message, request_id}}`; codes in
  shared-schemas.

## Scan pipeline orchestration (the core flow)

`scans` owns a state machine: `created → uploaded → quality_checked →
{classifying | ocr_running | barcode_lookup} → awaiting_confirmation → confirmed →
enriched (nutrition+allergen evidence) → complete`, with `*_failed` branches and
retry transitions. Stages execute as jobs; each stage idempotent (keyed by scan_id +
stage); mobile polls `GET /scans/{id}` (WebSocket/SSE deferred — polling is fine at
beta scale and survives free-tier hosts).
