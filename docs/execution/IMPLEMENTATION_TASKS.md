# Implementation Tasks

Small, independently verifiable, one-PR-sized tasks. IDs `T-###` ordered per
BUILD_SEQUENCE. **Card format** (all 32 required fields): fields that are empty for
a task are written `—` (explicitly none, not "unspecified"). Common profiles keep
cards readable:

- **SAFE-0** (default safety): no user-facing allergen/nutrition claims touched; if
  any UI copy is rendered, forbidden-strings test applies.
- **SAFE-A** (allergen surface): ALLERGEN_POLICY normative strings verbatim;
  asymmetry rules; evidence non-null; safety-suite green; **senior review required**.
- **SEC-0** (default security): input validation via shared-schemas; repo-layer user
  scoping on any user data; no secrets; no new deps without COST_MODEL row.
- **PRIV-0** (default privacy): no H-class data in logs (redaction tests must stay
  green); data minimization.
- **VERIFY-0** (default verification): `uv run ruff check && uv run pyright &&
  uv run pytest <paths>` + CI green; plus task-specific commands listed.
- **DOD-0** (definition of done): scope implemented, exclusions untouched, all
  listed tests added & passing, VERIFY commands pass locally and in CI, docs updated
  as listed, completion report per IMPLEMENTATION_HANDOFF format.

Complexity: S/M/L (≤half-day / day / multi-day session). Risk: low/med/high.
Model: Implementer (default) or Builder. senior review: only where marked.

---

## EP-01 Repository foundation

### T-001 · Monorepo scaffold & tooling — **[FULL CARD]**
- **Objective:** create the repository skeleton so every later task has a home and
  CI enforces structure from day one.
- **Product context:** R0; the reviewable-repo artifact (D8) starts here.
- **Technical context:** REPOSITORY_STRUCTURE layout; uv workspace + pnpm workspace;
  pre-commit.
- **Prerequisites:** none (first task).
- **Exact scope:** directory tree exactly per REPOSITORY_STRUCTURE; root
  `pyproject.toml` (uv workspace, ruff, pyright configs); `pnpm-workspace.yaml`;
  package stubs (`shared-schemas`, `nutrition-core`, `allergen-core`,
  `preprocessing` — empty modules with `__init__`, one placeholder test each);
  `apps/api` FastAPI hello app with `/healthz`; `.pre-commit-config.yaml` (ruff,
  format, gitleaks); `.gitignore`, `.gitattributes` (lfs patterns); LICENSE (MIT),
  root README stub linking docs/; `configs/.env.example`.
- **Explicit exclusions:** no CI workflows (T-002), no compose (T-003), no mobile
  app (T-030), no business logic anywhere.
- **Repository paths:** `/` (root), `apps/api/src/snap_api/main.py` (installable
  package `snap_api`; the earlier `apps.api.src.main` was illustrative and would not
  import as an installed module), `packages/*`, `configs/`.
- **Public interfaces:** `GET /healthz → {"status":"ok"}` (also `GET /readyz`).
- **Data-model / API / Mobile / ML / Infra changes:** — / healthz only / — / — / —.
- **Safety:** SAFE-0. **Security:** SEC-0; gitleaks hook active. **Privacy:** PRIV-0.
- **Acceptance criteria:** fresh clone → `uv sync && pnpm install && uv run pytest
  && uv run uvicorn apps.api.src.main:app` serves healthz; pre-commit runs on
  commit; import-linter config present (rules per REPOSITORY_STRUCTURE, passing).
- **Unit tests:** placeholder test per package proves harness. **Integration:**
  healthz httpx test. **ML tests:** —. **E2E:** —. **Performance checks:** —.
- **Verification commands:** VERIFY-0; `pre-commit run --all-files`.
- **Migration / Rollback:** — / delete branch.
- **Documentation updates:** root README stub; LOCAL_DEVELOPMENT cross-check.
- **DoD:** DOD-0. **Complexity:** M. **Risk:** low. **Model:** Builder.
  **senior review:** no.

### T-002 · CI pipeline v1 — **[FULL CARD]**
- **Objective:** `ci.yml` per CI_CD with lint-type-py/ts, test-py, security
  (gitleaks, pip-audit, pnpm audit), schema-drift placeholder, path filters +
  caching.
- **Product context:** review-ready repo needs visible green CI (D8).
- **Technical context:** CI_CD.md; GH Actions; services not yet needed (no DB tests
  yet).
- **Prerequisites:** T-001.
- **Exact scope:** `.github/workflows/ci.yml`; required-checks documentation;
  badge in README.
- **Exclusions:** deploy workflows (T-089), e2e/emulator jobs (T-093), ml-smoke
  (T-021), Trivy (T-088 with first Dockerfile).
- **Paths:** `.github/workflows/`, README.
- **Interfaces:** —. **Data/API/Mobile/ML/Infra changes:** — except infra: CI infra.
- **Safety:** SAFE-0. **Security:** SEC-0 + no-secrets-in-fork-PR config.
  **Privacy:** PRIV-0.
- **Acceptance:** PR to main runs all jobs; failure blocks merge (branch
  protection documented for owner to click); cache hit on second run.
- **Tests:** the workflow itself on a scratch PR. **Perf:** CI wall time < 8 min.
- **Verification:** scratch PR link in completion report.
- **Migration/Rollback:** — / revert workflow.
- **Docs:** CI_CD cross-check note.
- **DoD:** DOD-0. **Complexity:** M. **Risk:** low. **Model:** Builder. **Reviewer:** no.

### T-003 · Docker Compose local stack — **[FULL CARD]**
- **Objective:** one-command local Postgres(+pgvector)+MinIO+api per DOCKER_STRATEGY.
- **Product/Technical context:** LOCAL_DEVELOPMENT acceptance bar; compose profiles
  `worker`, `ocr` declared (unused).
- **Prerequisites:** T-001.
- **Scope:** `docker/compose.yaml`, api Dockerfile v1 (multi-stage, non-root,
  healthcheck; no models yet), MinIO bucket-init sidecar, pgvector image, `.env`
  wiring.
- **Exclusions:** model baking (T-024), deploy targets (T-089).
- **Paths:** `docker/`, `apps/api/Dockerfile`.
- **Interfaces:** compose service names as documented env defaults.
- **Changes:** infra: local only.
- **Safety/Security/Privacy:** SAFE-0/SEC-0 (no default creds in beta paths —
  compose-only creds clearly dev-labeled)/PRIV-0.
- **Acceptance:** `docker compose up -d` → healthz reachable; MinIO console up;
  `pytest` integration marker runs against compose services.
- **Tests:** integration smoke vs compose. **Perf:** image build < 5 min cached.
- **Verification:** VERIFY-0 + `docker compose up -d && curl :8000/healthz`.
- **Migration/Rollback:** —/—. **Docs:** LOCAL_DEVELOPMENT verified-by note.
- **DoD:** DOD-0. **Complexity:** M. **Risk:** low. **Model:** Builder. **Reviewer:** no.

## EP-02 Shared schemas

### T-004 · Core enums & error envelope — **[FULL CARD]**
- **Objective:** the shared vocabulary: AllergenStatusCode (ALLERGEN_POLICY codes),
  ScanState, ScanMode, EvidenceSource, error envelope + canonical error codes
  (API_DESIGN), InfoType (the 7-way typed-information enum).
- **Product context:** the typed-information principle becomes code here; every
  later surface imports these.
- **Technical context:** `packages/shared-schemas`; Pydantic v2; enums are the
  **only** source of these values repo-wide (lint rule: no string literals of
  status codes outside the package).
- **Prerequisites:** T-001.
- **Scope:** enum modules + error envelope model + unit tests asserting exact enum
  values match ALLERGEN_POLICY/API_DESIGN tables (literal tests).
- **Exclusions:** endpoint payload models (per-endpoint tasks), TS generation (T-005).
- **Paths:** `packages/shared-schemas/src/…`.
- **Interfaces:** importable enums/models.
- **Changes:** — (pure package).
- **Safety:** SAFE-A lite — status-code set is normative; **senior review: yes**
  (one-time vocabulary review). **Security/Privacy:** SEC-0/PRIV-0.
- **Acceptance:** enums exhaustive vs docs; literal tests pin values; import-linter
  allows only via package.
- **Tests:** unit literal tests. **Verification:** VERIFY-0.
- **Migration/Rollback:** —/—. **Docs:** ALLERGEN_POLICY changelog note ("codes
  frozen in code").
- **DoD:** DOD-0. **Complexity:** S. **Risk:** low (but normative). **Model:** Implementer.
  **Reviewer:** **yes**.

### T-005 · OpenAPI → TS client generation — **[FULL CARD]**
- **Objective:** generated TS client + schema-drift CI job (fail on uncommitted
  regen diff).
- **Prerequisites:** T-002, T-004.
- **Scope:** generation script (openapi-typescript or orval — pick, record in PR),
  pnpm package `@snap/api-client`, CI job wiring.
- **Exclusions:** mobile usage (T-030+).
- **Acceptance:** changing a Pydantic model without regenerating fails CI.
- Other fields: SAFE-0/SEC-0/PRIV-0; unit test = generated client typechecks;
  VERIFY-0 + `pnpm -r tsc`; docs: CI_CD note. **Complexity:** S. **Risk:** low.
  **Model:** Builder. **Reviewer:** no.

---

*(Cards below are complete but condensed: unlisted fields = `—` or profile
defaults. Model = Implementer unless noted.)*

## EP-03 Identity (R1)

- **T-006 · User table + migrations + argon2 hashing** — Alembic baseline; user
  entity per DATA_MODEL; password hashing service (argon2id params from
  AUTHENTICATION); strength+breach-list validation. Prereq T-003/004. AC: migration
  up/down tests; hash verify roundtrip; weak/breached passwords rejected 422.
  SEC-0+crypto-review checklist. M/low.
- **T-007 · Signup + email verification** — register endpoint, token issue,
  console-email backend + provider interface (pick free provider per COST_MODEL
  `[VERIFY]` row), unverified-cannot-scan gate. Prereq T-006. AC: full flow in
  integration test; enumeration-safe responses. M/med.
- **T-008 · Login + JWT + refresh rotation** — EdDSA access tokens, session table,
  family rotation + reuse detection, lockout, logout. Prereq T-006. AC:
  AUTHENTICATION acceptance incl. reuse-detection revokes family (test), revoked
  ≤60 s. **senior review: yes** (auth core). L/high.
- **T-009 · Password reset + audit events for auth** — reset flow; audit module
  baseline (append-only table + writer); auth events audited. Prereq T-008. AC:
  reset revokes sessions; audit rows immutable (no UPDATE grant test). M/med.

## EP-04 Profiles & consent (R1 core, R3 managed)

- **T-010 · Consent records + disclosure gate** — consent tables (append-only),
  disclosure endpoint + "cannot scan without disclosure consent" enforcement.
  SAFE-A (disclosure copy normative from J1). Prereq T-008. **Reviewer: yes.** M/med.
- **T-011 · Dietary profile CRUD** — profiles, allergens (canonical seed +
  custom XOR), diet rules; profile-unavailable fail-state contract in scan reads.
  Prereq T-010; seeds T-025. AC: isolation tests; J2 custom-allergen caution copy
  in API metadata. M/med.
- **T-012 · Managed sub-profiles + active-profile selection** — (R3) max 5,
  validation, active-profile on scan create. Prereq T-011. S/low. Builder.

## EP-05 Images (R1)

- **T-013 · Presign upload flow + image records** — R2/MinIO client via S3 API,
  presign policy (size/key), complete-callback, image entity. Prereq T-003/008.
  SEC per UPLOAD_SECURITY (policy caps). M/med.
- **T-014 · Validation + canonicalization pipeline** — signature check, subprocess
  decode w/ rlimits, bomb guards, re-encode, EXIF/GPS strip, thumbnail, quality
  heuristics (blur/exposure). Prereq T-013, T-016. AC: malicious-fixture suite
  (UPLOAD_SECURITY tests) green; GPS fixture clean. **Reviewer: yes** (security
  surface). L/high.
- **T-015 · Signed GET minting + ownership checks** — 15-min URLs, mint audit log
  fields. Prereq T-013. AC: IDOR two-user test. S/med.

## EP-06 Scan engine (R1)

- **T-016 · Postgres job queue + runner** — jobs table, SKIP LOCKED consumer,
  retries/backoff, idempotency keys, sweep, graceful drain; `JobQueue` interface.
  Prereq T-003. AC: crash-recovery integration test (kill worker mid-job → sweep
  requeues; idempotent completion). L/high.
- **T-017 · Scan state machine + create/poll endpoints** — scan entity, transitions
  table-driven, POST /scans + GET /scans/{id} aggregate, Idempotency-Key store,
  per-section partial states. Prereq T-013/016. AC: state-transition property tests
  (no illegal transitions); poll contract with Retry-After. L/high. **Reviewer: yes**
  (core orchestration).

## EP-07 ML data pipeline (parallel lane)

- **T-018 · Food-101 download/verify/layout + license review record** — pipeline
  stages 1–3 + the R0 license task (DATASET_STRATEGY `[LICENSE REVIEW]`): record
  findings in data card + DECISION_LOG entry. AC: checksums pinned; counts asserted;
  license memo committed. M/low.
- **T-019 · Metadata, cleaning, dedup, splits, manifest** — stages 4–8; pHash +
  CLIP near-dupe pass; stratified val carve; manifest artifact to W&B. AC: dedup
  report; split determinism test (seeded rerun byte-identical). L/med.
- **T-020 · Subsets + caching + preprocessing package** — 5-class/2-class subsets,
  resized cache artifact, `packages/preprocessing` canonical transforms + golden-
  tensor tests (ML_TESTS parity fixtures). AC: parity tests green. M/med.
  **Reviewer: yes** (parity is safety-adjacent infrastructure).

## EP-08 Training (Kaggle lane)

- **T-021 · Training CLI + resumability + W&B + CI micro-smoke** — TRAINING_PLAN
  recipe engine (config-driven), checkpoint/resume exact, W&B logging, micro-model
  CI job (ml-smoke in ci.yml). AC: kill-and-resume test on micro-model reproduces
  epoch metrics; run tagged incomplete without required outputs. L/high.
- **T-022 · E1 baseline run + first report** — execute E1 (ResNet-50) on Kaggle;
  eval JSON; report page; establishes all downstream numbers. AC: report committed
  with real numbers; no placeholder remains for E1 row. M/med (mostly GPU-time).
- **T-023 · Wave-1 contenders (E2–E4) + gate review** — runs + comparison report.
  **Owner checkpoint: architecture pick (AD-2).** M/med. *(Waves 2–3 = T-023b/c
  same shape; omitted rows ride EXPERIMENT_PLAN.)*

## EP-09 Evaluation

- **T-024 · Evaluation harness + robustness + OOD + calibration** — EVALUATION_PLAN
  CLI: metrics, ECE + reliability plots, corruption suites, OOD AUROC, temperature
  fitting; phone-domain eval-set loader (set itself is an owner data-collection
  chore logged in BUILD_SEQUENCE). AC: harness golden-tested on micro-model;
  reports auto-generated. L/med.

## EP-10 Serving

- **T-025 · Reference-data seeds** — nutrients, DV table, class→FDC mapping
  (curated rows — owner reviews mapping table: checkpoint), class→allergen hints
  (curated + sourced), FDC payload snapshot for offline dev. AC: seed idempotence;
  101/101 coverage test; hints rows all carry provenance. M/med. **Reviewer: yes**
  (hints table is a safety input).
- **T-026 · ONNX export + parity suite** — ONNX_STRATEGY export CLI (T baked,
  metadata_props), parity tests vs PyTorch. Prereq T-021. AC: parity thresholds;
  metadata completeness gate. M/med.
- **T-027 · Inference module + thresholds + readiness** — ORT session, thread pool,
  preprocessing import, τ/τ_u application → UI-state mapping, model_version
  recording, readyz gating, B1 bench script. Prereq T-026, T-017. AC: threshold
  behavior tests (ML_TESTS); concurrent-load test; readiness blocks pre-warm
  traffic. L/high. **Reviewer: yes** (confidence→framing is safety logic).

## EP-11 Nutrition

- **T-028 · FDC client + cache + search** — httpx client, cache table + TTL +
  stale-while-revalidate job, circuit breaker, search endpoint with data-type
  ranking. AC: provider-down integration tests (FAILURE_HANDLING behaviors);
  <100 ms cached p95 bench note. M/med.
- **T-029 · nutrition-core math + serving endpoints** — NUTRITION_CALCULATION pure
  functions (property+golden tests), serving selection API, confirm-flow wiring
  (nutrition only post-confirmation — enforced in state machine). AC: math suites;
  "no nutrition before confirmation" integration test. M/med. **Reviewer: yes**
  (deterministic-math guardrail).

## EP-16/17 Mobile (parallel lane; Builder-heavy)

- **T-030 · Expo scaffold + navigation + auth flows** — MOBILE_ARCHITECTURE stack,
  secure token storage, login/signup/verify screens (S1–S2), route guards. M/med.
- **T-031 · Safety-kernel UI components** — StatusRow, TypedFact, ConfidenceBar,
  SourceChip, Disclaimer with literal-copy tests bound to shared enums. **Reviewer:
  yes** (the safety rendering kernel). M/med. Implementer.
- **T-032 · Onboarding + disclosure + profile screens** (S1, S3) — J1/J2 flows incl.
  consent recording. SAFE-A copy. M/med.
- **T-033 · Camera + modes + quality pre-check + upload** (S5, S6) — CAMERA_UX
  overlays, downscale contract, presign upload, capture queue (offline). L/med.
- **T-034 · Processing + candidates + confirm + search** (S7, S8) — polling hooks,
  low-confidence/unknown states (D14), search rescue. AC: Maestro happy-path +
  low-confidence flows. L/med.
- **T-035 · Nutrition + serving screens** (S9, S12) — framing lines, missing-data
  rendering, recompute. M/low. Builder.

## EP-12/13/14 OCR → parsing → allergens (R2 core)

- **T-036 · OCR engine integration + pipeline stages 1–7** — PaddleOCR behind
  `OcrEngine`, preprocessing stages, layout grouping, completeness estimator,
  fixture harness tiers 1–2. L/high.
- **T-037 · Section detection + fixtures corpus v1** — anchors, block
  classification; assemble self-captured fixture corpus (owner chore checkpoint) +
  synthetic generator v1. M/med.
- **T-038 · Ingredient grammar parser + lexicon v1** — INGREDIENT_EXTRACTION
  grammar, compound/and-or handling, fuzzy with guardrails, unrecognized-token
  survival. AC: parser fixture suite. L/high.
- **T-039 · Allergen ontology + matcher + statements + evidence assembly** —
  ontology.yaml v1 (curated, sourced), matcher, statement patterns, evidence rows
  with non-null provenance, statuses per policy incl. demotion rules. AC: **full
  ALLERGEN_TESTS catalog green.** SAFE-A. **Reviewer: yes.** L/**high**.
- **T-040 · Diet rule engine** — veg/vegan/gluten evaluation with unclear outcomes +
  rationale. AC: rule fixtures. M/med.
- **T-041 · Panel field extraction (core fields)** — NUTRITION_LABEL_EXTRACTION
  parser + plausibility validation + user-confirm endpoint. 🟡 gated on owner
  ratification (AD-1). L/high.
- **T-042 · OCR review & correction UI + evidence UI** (S10, S11) — verbatim panel,
  chips/spans, inline corrections + re-run, allergen evidence screen per policy
  ordering/prominence. SAFE-A. **Reviewer: yes.** L/high.

## EP-15 Barcode

- **T-043 · OFF client + product cache + barcode endpoint + staleness** — M/med.
- **T-044 · Barcode capture mode + product result UI** — mobile live detection,
  fallback entry, provenance/staleness display. M/low. Builder.

## EP-19 History & privacy (R3)

- **T-045 · History list/detail + soft-delete + sweeps** — incl. orphan sweep job.
  M/med.
- **T-046 · Export job + archive** — JSON assembly, signed link, revocation on
  deletion. M/med.
- **T-047 · Account deletion cascade + tombstone + verification sweep test** —
  **Reviewer: yes** (privacy-critical). L/high.

## EP-20 Assistant (R3)

- **T-048 · Corpus v1 + ingestion + retrieval** — 100+ curated docs (ingredient/
  allergen/nutrition education with sources), chunker, bge-small embedding,
  pgvector HNSW, retrieval eval set + recall@k test. L/med.
- **T-049 · Tool registry + deterministic tools** — TOOL_ARCHITECTURE all 9 tools,
  schemas, authz, logging. AC: tool isolation tests (cross-scan denial). L/high.
- **T-050 · Provider adapter + orchestration loop + fallback** — provider pick with
  terms verification (PRIVACY_MODEL checkpoint), tool-calling loop, quota
  degradation path. **Reviewer: yes** (provider terms + boundary behavior). L/high.
- **T-051 · Output validators + injection defenses + AI eval harness** — forbidden
  strings, citation checks, boundary patterns, fence escaping; deterministic eval
  tier in CI; live-tier runner. SAFE-A. **Reviewer: yes.** L/**high**.
- **T-052 · Assistant UI** (S13) — thread, citations chips, degraded banner. M/low.
  Builder.

## EP-21 Web demo

- **T-053 · Web demo page + demo role + fixture gallery** — Vite page, server-side
  demo-role writes-block, seeded gallery. M/med.

## EP-22/23 Security & observability (continuous; representative tasks)

- **T-054 · Rate limiting + quotas** — per API_DESIGN table; time-mocked tests.
  M/med.
- **T-055 · IDOR sweep suite + authz matrix tests** — two-user enumeration across
  endpoints. M/med. **senior review of results: yes.**
- **T-056 · Structured logging + redaction + metrics endpoints** — allowlist
  logger, redaction CI tests, Prometheus metrics, admin read endpoints. M/med.
- **T-057 · Probes + alerts + quota telemetry** — GH cron probes, email alerts,
  weekly usage job. S/low. Builder.
- **T-058 · Drift/monitoring jobs** — MONITORING weekly aggregates + admin JSON.
  M/low.

## EP-24 Deployment

- **T-059 · Neon + R2 provisioning + staging Space deploy** — env separation,
  secrets, migrations on deploy, smoke suite. M/med.
- **T-060 · Beta Space + keep-warm + backups + deploy workflows** — deploy-beta.yml,
  keep-warm cron, pg_dump job. M/med.
- **T-061 · Terraform AWS target modules (validate-only)** — INFRASTRUCTURE_AS_CODE
  stage-1. M/low. Builder.

## EP-25 Demo & presentation

- **T-062 · Demo seeds + scenario fixtures + reset script** — DEMO_DATA. M/low.
  Builder.
- **T-063 · README + model-card publication + demo recordings** — README_PLAN
  execution with **measured numbers only**. M/low. **Reviewer: yes** (claims review).

## EP-26 Research track (R4/R5 — scoped when reached)

T-070+ reserved: portion ground-truth collection, reference-object prototype,
portion evaluation report, distillation (E15), quantization (E16), on-device build,
feedback dataset build v1. Each gets a full card at R4 planning (owner checkpoint).

---

**Anti-vagueness check:** no card says "build the app/train the model/add OCR/add
security/deploy" — each is one reviewable PR with named files, named tests, and a
verification command. Any task that grows beyond its card splits before merging.
