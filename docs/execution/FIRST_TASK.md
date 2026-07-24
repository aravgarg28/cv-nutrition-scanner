# First Implementer Task — Exact Prompt

*Copy-paste below into a fresh Implementer session in the repository root.*

---

Read `docs/execution/IMPLEMENTATION_HANDOFF.md` and follow its session protocol for this and
every future task.

Your task is **T-001 · Monorepo scaffold & tooling** — the full card is in
`docs/execution/IMPLEMENTATION_TASKS.md` (it is a FULL CARD; every field is
binding). Required reading before you write anything:

- `docs/decisions/DECISION_LOG.md` (D0 zero-budget and the guardrails bind even a
  scaffold: MIT license, no paid tooling, gitleaks hook)
- `docs/architecture/REPOSITORY_STRUCTURE.md` (the exact tree + dependency
  boundaries you are creating and the import-linter rules that enforce them)
- `docs/build/LOCAL_DEVELOPMENT.md` (the commands your scaffold must make true)
- `docs/build/CI_CD.md` (context only — CI itself is T-002, do not create workflows)

Key constraints, restated:

- Scope is exactly the T-001 card: tree, uv workspace + tooling configs, pnpm
  workspace, four package stubs with placeholder tests, FastAPI app with `/healthz`
  only, pre-commit (ruff, format, gitleaks), .gitignore/.gitattributes, MIT LICENSE,
  README stub linking `docs/`, `configs/.env.example` with named-but-blank keys per
  `docs/security/SECRET_MANAGEMENT.md`.
- Explicit exclusions: **no** CI workflows, **no** docker/compose, **no** mobile
  app, **no** business logic, **no** dependencies beyond tooling + FastAPI/uvicorn/
  pytest/httpx/pydantic — every dependency you add must be free and justified in
  your report.
- Acceptance: fresh-clone sequence from the card works verbatim; `pre-commit run
  --all-files` passes; import-linter config present and passing.

When done, produce the completion report per IMPLEMENTATION_HANDOFF format and stop. Do not
begin T-002.
