# CI/CD (GitHub Actions, free on public repo)

> **Implementation status (T-002):** `ci.yml` exists with jobs `changes`
> (dorny/paths-filter), `lint-type-py` (ruff + format + pyright + import-linter +
> pytest), `lint-type-ts` (path-gated; `pnpm run lint` no-op until TS lands),
> `security` (gitleaks + pip-audit + pnpm-audit), and `schema-drift` (placeholder
> until T-005). Remaining jobs below (`safety-suite`, `ml-smoke`, `docker-build`,
> `e2e-smoke`, `test-mobile`) are added by their owning tasks. pnpm-audit is advisory
> while the JS workspace is empty and becomes strict when real JS deps land. The
> README CI badge uses an `OWNER` placeholder to replace when the repo is pushed.

## Workflows

### `ci.yml` — every PR + main (path-filtered jobs, heavy caching)

| Job | Contents | Gate |
|---|---|---|
| lint-type-py | ruff (check+format), pyright, import-linter (boundaries) | ✅ |
| lint-type-ts | eslint, prettier-check, tsc (mobile, web-demo, client) | ✅ |
| test-py | pytest units + API integration (services: pgvector Postgres, MinIO); coverage report (informational, no % gate) | ✅ |
| test-mobile | RN component tests (jest) | ✅ |
| **safety-suite** | ALLERGEN_TESTS catalog + forbidden-strings + framing literals + injection deterministic tier | ✅ **required check named visibly** |
| security | gitleaks, pip-audit, pnpm audit (fail on high), Trivy on built image | ✅ |
| ml-smoke | micro-subset pipeline: data validate → 1-epoch micro-model train → eval → ONNX export → parity (ML_TESTS CI tier) | ✅ on `ml/**`, `packages/preprocessing/**` paths |
| schema-drift | regenerate OpenAPI + TS client; fail if uncommitted diff | ✅ |
| docker-build | build api image (no push on PR); size budget check | ✅ |
| e2e-smoke | Maestro on Android emulator: J4 happy path (mocked model via micro-model) | ✅ main + nightly (emulator cost) |

### `deploy-staging.yml` — push to main
Build+push image (GHCR, tag `app-{sha}-model-{ver}` from serving_model.lock) → HF
staging Space update → wait healthy → deployment smoke suite (TRAINING_PIPELINE §9)
→ notify.

### `deploy-beta.yml` — manual (tag `release-*`)
Same image promoted (no rebuild) → beta Space → smoke → seed_demo refresh →
keep-warm re-arm. Manual approval environment gate in GH.

### Scheduled
`keep-warm.yml` (10-min cron, active hours) · `backup.yml` (weekly pg_dump → R2) ·
`nightly.yml` (OCR corpus benchmark, full e2e-smoke, dependency-update PRs via
Dependabot config, quota telemetry report) · `monthly-rebuild.yml` (base-image
refresh build).

### `infra-validate.yml` — on `infrastructure/**`
terraform fmt/validate + plan (sandbox, no apply) per INFRASTRUCTURE_AS_CODE.

## Rules

- Required checks for merge: lint/type, test-py, safety-suite, security,
  schema-drift (+ml-smoke when triggered).
- No secrets in PR-from-fork runs (SECRET_MANAGEMENT); deploy workflows restricted
  to environments with protection rules.
- Every deploy records: image tag, model version, git SHA → release notes stub.
- Flaky-test policy: quarantine within 24 h with issue (TEST_STRATEGY).
