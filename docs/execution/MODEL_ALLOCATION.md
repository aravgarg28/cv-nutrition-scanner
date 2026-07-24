# Model Allocation

Who does what across the AI agents (and the human).

## Reviewer (planning/review tier)

- Product decisions and scope changes (with the owner).
- Architecture decisions and ADR updates; ML evaluation design and gate reviews
  (🎓 checkpoints); reading experiment results and deciding next waves.
- Safety reviews (🛡): ALLERGEN_POLICY changes, matcher/evidence PRs (T-039, T-042),
  assistant validators (T-051), thresholds (T-027), model cards, README/claims
  review (T-063).
- High-risk security reviews (🔒): auth core (T-008), upload pipeline (T-014),
  deletion cascade (T-047), IDOR results (T-055).
- Final adversarial review before beta (Checkpoint H) and the Phase-25 style
  re-review after major releases.

## Implementer (implementation tier — default)

- All L/high tasks: scan engine, job queue, inference module, OCR pipeline,
  ingredient parser, allergen matcher, assistant orchestration, deletion cascade,
  training CLI, evaluation harness.
- Debugging, integration work, data pipelines, difficult tests (property tests,
  chaos/failure suites), Kaggle run babysitting scripts.
- Anything touching SAFE-A surfaces implements under senior review.

## Builder (routine tier)

- Scaffolding (T-001–T-003, T-005), straightforward CRUD, standard UI screens
  (T-035, T-044, T-052, T-057), fixtures authoring from specs, documentation sync,
  repetitive test tables, seed scripts, demo assets (T-062), Terraform boilerplate
  (T-061).
- Never solo on: allergen logic, auth, upload security, thresholds, consent/
  deletion, assistant validators.

## Owner (human)

- Ratify checkpoints (👤): policy freeze, architecture pick, panel scoping, provider
  terms, beta go/no-go, R4 scoping.
- Physical-world chores: fixture photo capture, phone-domain eval set, portion
  ground-truth weighing (R4), Kaggle account/session starts, provider account
  creation (D0 rule: never attach payment methods).
- Curation sign-offs: class→FDC mapping, class→allergen hints, ontology additions.
- Beta-tester recruitment and feedback triage.

## Escalation rule

Any model hitting a decision not covered by docs **stops and asks** (IMPLEMENTATION_HANDOFF
rule 16) — allocation never overrides the no-invention rule.
