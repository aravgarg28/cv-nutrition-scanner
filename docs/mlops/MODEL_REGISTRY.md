# Model Registry

W&B Artifacts + aliases = the registry (free tier); the API's `model_version` table
mirrors promotion state for runtime/audit (DATA_MODEL).

## Stages & aliases

| Alias | Meaning | How it gets there |
|---|---|---|
| `candidate` | passed training + parity, entering evaluation | automatic at export if ONNX parity passes |
| `staging` | passed evaluation gates; deployed to staging env | manual promotion after gate review |
| `production` | serving beta | manual promotion after staging smoke + checklist |
| (retired) | superseded | previous production kept (rollback target) |

## Evaluation gates (candidate → staging)

1. Evaluation JSON complete (EVALUATION_PLAN suite incl. calibration + OOD).
2. Macro-F1 and top-1 ≥ current production − 0.5 pt (no silent regressions), OR an
   explicit trade note (e.g., latency win) approved by owner.
3. ECE post-calibration ≤ current production + 0.005.
4. CPU p95 within PERFORMANCE_BUDGET on serving container class (B1).
5. ONNX parity suite green; metadata_props complete (thresholds, T, dataset version).
6. Model card drafted (MODEL_CARD template, measured fields filled).

## Promotion gates (staging → production)

1. Staging deploy serves it ≥ 48 h with smoke suite green.
2. Threshold behavior re-verified (τ, τ_u produce sane unknown-rates on staging
   traffic/fixtures).
3. Safety fixture suite green against the staging deployment (ALLERGEN_TESTS
   E2E subset + framing tests).
4. Owner sign-off recorded (BUILD_SEQUENCE checkpoint).

## Metadata (on the artifact + mirrored to DB)

name, version, W&B run link, git SHA, dataset artifact version, config hash,
thresholds (τ, τ_u), temperature T, ONNX sha256, eval report link, model card link,
promotion history (who/when/why).

## Rollback

Models are baked into images (INFERENCE_DEPLOYMENT) → rollback = redeploy previous
image tag (minutes). Registry aliases updated to match reality after rollback
(mirror table keeps history). Rollback triggers: readiness failures, correction-rate
spike (MONITORING alert), safety-suite regression discovered post-deploy.

## Cadence

No scheduled retraining in MVP (no fresh data yet). Retraining triggers: E-plan wave
completion, drift/correction-rate signals (MONITORING), or consented feedback
dataset reaching useful size (FEEDBACK_LOOP, R5).
