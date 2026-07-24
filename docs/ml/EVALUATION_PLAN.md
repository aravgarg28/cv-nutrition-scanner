# Evaluation Plan

The evaluation harness (`ml/evaluation/`) is a standalone CLI taking (model artifact,
dataset artifact, config) → versioned JSON report + plots. Metrics are never computed
ad-hoc in notebooks for reporting.

## Metric suite (per evaluated model)

**Classification quality**
- Top-1 and top-5 accuracy (test split; official Food-101 test).
- Macro-F1 and weighted-F1; per-class precision/recall/F1 (all 101 classes, tabulated).
- Confusion matrix (full 101×101 saved as artifact; top-30 confusions rendered).

**Calibration** (safety-relevant: confidence drives UI framing per SAFETY_MODEL)
- Expected Calibration Error (15 equal-mass bins), before/after temperature scaling.
- Reliability diagrams (artifact per model).
- Negative log-likelihood.

**Operational**
- CPU inference latency: p50/p95 single-image, batch-1, on the serving container's
  CPU class (not the GPU box) — ONNX Runtime, includes preprocessing.
- Model size (ONNX file MB) and peak RSS during inference.

**Robustness suites** (corrupted copies of the test set; corruption params versioned)
- Gaussian blur (3 severities), brightness ±(2 severities), rotation ±15°/±30°,
  JPEG quality {80, 50, 30}.
- Reported as accuracy-retention curves vs severity, compared across models. No
  robustness numbers exist until measured — the report template has placeholders.

**Unknown/OOD behavior**
- AUROC for in-vocab vs OOD set (DATASET_STRATEGY §custom sets); false-accept rate
  at the chosen operating threshold; % of phone-domain OOV foods correctly routed to
  the "not sure" state.

**Domain gap**
- Accuracy on the custom phone-domain eval set vs official test — the honest number
  for "how it works in your hand". Reported side-by-side in the model card.

**Subgroup/cuisine coverage**
- Per-class F1 grouped by rough cuisine buckets (Western/Asian/dessert/etc., curated
  grouping of the 101 classes) to expose uneven performance; documented in the model
  card's bias section.

## Why top-5 accuracy alone is insufficient (normative explanation)

Top-5 accuracy measures whether the right answer appears in a list — appropriate for
our *confirmation UX* (user picks from top-5). It says nothing about:
1. **Confidence honesty** — a model can be 95% top-5 accurate while wildly
   overconfident on the misses; the UI framing depends on calibrated confidence (ECE).
2. **Which classes fail** — 95% average can hide 40% F1 on specific dishes; per-class
   metrics + confusion structure matter because class-inferred allergen hints (S4)
   depend on the confirmed class.
3. **Allergen-relevant confusions are not symmetric in cost** — confusing two
   nut-free desserts is cosmetic; confusing a peanut dish for a peanut-free lookalike
   feeds a wrong S4 hint. ERROR_ANALYSIS defines an allergen-weighted confusion view:
   confusion pairs annotated by whether the confused classes differ in
   commonly-associated allergens; those pairs get priority scrutiny.
4. **OOD behavior** — top-5 is undefined for foods outside the 101 classes; the
   product meets those daily.
Therefore no single headline number is quoted anywhere (README included) without
macro-F1, ECE, and the phone-domain figure beside it.

## Statistical discipline

- Final config re-run with 3 seeds; report mean ± std for headline metrics.
- Model A vs B claims use paired comparison on identical test items; differences
  within seed-noise are reported as ties.
- Test set evaluated once per phase gate (EXPERIMENT_PLAN); all tuning on validation.

## Report artifacts

Per phase gate: `docs/ml/reports/<date>-<gate>.md` — auto-generated tables from
evaluation JSONs + linked W&B runs + written analysis (ERROR_ANALYSIS findings).
The model card (MODEL_CARD) references the final report.
