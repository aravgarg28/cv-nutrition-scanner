# Environments

| Env | Purpose | Compute | DB | Storage | Data |
|---|---|---|---|---|---|
| **local** | development | Docker Compose (api, worker-role optional, Postgres+pgvector, MinIO) | container PG | MinIO | seed fixtures only |
| **test** | CI | ephemeral containers (services in GH Actions) | throwaway PG | MinIO/moto | fixtures; micro-dataset |
| **staging** | pre-release verification | HF Space (separate, may sleep freely) | Neon branch `staging` | R2 bucket `-staging` | synthetic + team accounts |
| **demo** | recruiter web demo (long-lived) | shares beta Space, demo role | beta DB, demo account rows | beta bucket, demo prefix | seeded DEMO_DATA fixtures |
| **beta ("prod")** | real testers | HF Space (keep-warm) | Neon `main` | R2 main bucket | real user data |

## Configuration separation

- One settings schema (pydantic-settings); values via env per environment; `ENV`
  name gates behavior only where explicitly designed (e.g., email console-fallback
  in local/test) — no `if env == "prod"` business logic.
- Separate credentials per env (Neon branches have distinct URLs; R2 scoped tokens
  per bucket; distinct JWT keys — staging tokens can never work in beta).
- Model versions: staging runs the promotion candidate (`staging` alias); beta runs
  `production` alias (MODEL_REGISTRY).

## Data boundaries

Real user data exists **only** in beta. Never copied to staging/local (no "prod
dump" workflows — by policy and by lack of need; seeds reproduce all states).
Demo account lives in beta but is role-isolated (`demo` role: read-only server-side,
seeded content only, aggressive rate limits) — keeps one deploy while protecting
real users.

## Promotion path

local (Compose) → CI (tests + image build) → staging deploy (auto on main) →
smoke suite (deployment tests) → manual promote to beta (tag) → post-deploy smoke +
keep-warm re-arm. Rollback = redeploy previous image tag (models baked in →
model rollback rides image rollback).
