# Model Monitoring

What we watch in production to know the model is healthy — computed from
**metadata only** (inference_event, feedback_event, ocr_result stats). Raw images
are never retained or inspected for monitoring without the training-images consent
(D16/PRIVACY_MODEL); monitoring is designed to not need them.

## Signals

| Signal | Source | Baseline | Alert condition |
|---|---|---|---|
| Confidence distribution (calibrated top-1 histogram) | inference_event | distribution at deploy time | weekly KS-test drift beyond threshold `[SET AFTER BASELINE]` |
| Prediction class distribution (top-20 share) | inference_event | deploy-time mix | sustained shift (new user population or drift) |
| Unknown/"not sure" rate | scan states | deploy-time rate | ±50% relative change |
| OOD score distribution | inference_event | deploy-time | drift |
| **User correction rate** (per class + overall) | user_correction | deploy-time | overall +5 pts absolute, or any top-10 class doubling |
| Confirmation-without-correction rate | user_confirmation | — | falling = quality proxy degrading |
| Image-quality mix (blur/exposure buckets) | image_quality_result | — | shift explains accuracy changes before blaming the model |
| Class-specific degradation | corrections + confirmations per class | — | worst-5 classes reviewed monthly |
| OCR failure + completeness rates | ocr_result | — | failure >10% weekly or completeness median drop |
| Latency (inference p95) | metrics | budget | PERFORMANCE_BUDGET breach |
| Model-version comparison | all above, segmented by model_version | — | side-by-side table for 2 weeks after any promotion |

## Cadence & mechanics

Weekly aggregate job (OBSERVABILITY) → admin endpoint JSON + email digest;
monthly review note in `docs/ml/reports/monitoring-<month>.md` (what moved, action
taken/not and why). Alerts via the free probe stack (OBSERVABILITY §alerting).

## Response playbook

Correction spike in one class → ERROR_ANALYSIS pass on correction records (text
metadata; images only if user consented) → hints-table or threshold fix vs retrain
decision. Confidence drift + quality-mix stable → suspect real drift → schedule
retrain evaluation. Quality-mix shift → CAMERA_UX/device investigation, not retrain.
Latency creep → B1/B9 re-run, host investigation.

## Honest limits (beta)

Small-n: with ~10 testers, weekly stats are noisy — alerts tuned loose, trends over
months matter more than weeks; documented so nobody over-reacts to n=7 weeks.
