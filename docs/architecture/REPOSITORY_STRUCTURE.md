# Repository Structure

**Monorepo** (single public GitHub repo). Rationale: one owner, shared schemas across
API/mobile/web, atomic cross-cutting changes, one CI, one thing for reviewers to
clone. Coordinated multi-repo rejected (sync overhead, no org boundary to justify it).

```
snapnutrition/
  apps/
    api/                 # FastAPI modular monolith (BACKEND_ARCHITECTURE modules)
      src/{identity,profiles,scans,images,inference,ocr,nutrition,allergens,
           products,assistant,history,feedback,registry,admin,audit,jobs,shared}/
      tests/             # module + integration tests
      alembic/
    mobile/              # Expo RN app (MOBILE_ARCHITECTURE layout)
    web-demo/            # small React (Vite) demo page — same generated API client
  packages/
    shared-schemas/      # Pydantic models + enums; OpenAPI → generated TS client
    nutrition-core/      # deterministic nutrition math (pure python)
    allergen-core/       # ontology data + matcher + statement patterns (pure python)
    preprocessing/       # THE image preprocessing module (training/serving parity)
  ml/
    datasets/            # download/verify/split/manifest + synthetic label generator
    training/            # train CLI, configs/ (experiment YAMLs)
    evaluation/          # metrics harness, robustness suites, assistant eval runner
    export/              # ONNX export + parity
    notebooks/           # EDA, error-browser, augmentation audit (outputs stripped)
    scripts/             # wandb_gc, seed helpers
  data/
    corpus/              # RAG markdown corpus (frontmattered)
    seeds/               # allergen ontology snapshots? NO — ontology lives in
                         # allergen-core/data; this holds DB seed fixtures (nutrients,
                         # class→FDC mapping, class→allergen hints, DV table)
  infrastructure/
    aws/                 # Terraform target modules (validate-only under D0)
    free-tier/           # R2/Neon config notes + any TF; HF Space config
  tests/                 # cross-cutting suites: e2e/, fixtures/{ocr,allergen,images}/
  docs/                  # (this tree)
  scripts/               # seed_demo.py, dev bootstrap, backup cron
  configs/               # runtime config templates (.env.example, logging)
  docker/                # Dockerfiles, compose.yaml
  .github/workflows/     # CI_CD
```

## Dependency boundaries (enforced by import-linter in CI)

- `packages/*` depend on nothing internal (pure; nutrition-core/allergen-core have
  zero runtime deps beyond stdlib+pydantic).
- `apps/api` → packages; modules → other modules **only via `public.py`**.
- `ml/*` → packages (esp. `preprocessing`) but never `apps/`.
- `apps/mobile`/`web-demo` → generated client from shared-schemas only (no hand-typed
  API shapes).
- `data/corpus`, `data/seeds` are data-only (no code imports upward).

## Tooling choices

Python: uv + ruff + pyright, pytest; single root `pyproject.toml` workspace with
package members. TS: pnpm workspace (mobile, web-demo, generated client), eslint +
prettier + tsc. Pre-commit: ruff/format, eslint, gitleaks. Large binaries: fixtures
via git-lfs (small: images ≤ ~30 MB total budget); models/datasets NEVER in git
(W&B artifacts).
