# Résumé Bullets

Templates with `{placeholders}` — **filled only from measured artifacts** (eval
JSONs, bench reports, W&B). A bullet whose placeholder is unmeasured doesn't ship.
Honest phrasing is deliberate ("cached lookup", "on CPU", "top-5 for user
confirmation").

## ML / Applied AI

- Fine-tuned and compared {n_architectures} CNN architectures (ResNet-50,
  EfficientNetV2-S, ConvNeXt-Tiny) on Food-101 (101 classes, 101k images) in
  PyTorch, reaching {top1}% top-1 / {top5}% top-5 and {macro_f1} macro-F1 across
  {n_experiments} W&B-tracked experiments with versioned dataset artifacts.
- Reduced expected calibration error from {ece_before} to {ece_after} via
  temperature scaling and label-smoothing ablations, and built OOD detection
  (energy-score, {auroc} AUROC) so out-of-vocabulary foods route to an honest
  "not sure" state instead of a wrong answer.
- Built an OCR pipeline (PaddleOCR + deterministic parsing) extracting ingredients
  and allergen statements from packaging photos at {allergen_recall}% allergen-term
  recall on a {n_fixtures}-image fixture corpus, with per-token confidence driving
  a completeness-aware safety policy.

## CV engineering

- Exported models to ONNX with CI-enforced PyTorch parity (max prob delta ≤ 1e-4)
  and served them on CPU at {p50_ms} ms p50 / {p95_ms} ms p95 single-image latency;
  INT8 quantization cut latency {quant_speedup}× at {quant_acc_delta} pt accuracy
  cost.
- Authored a robustness evaluation suite (blur/lighting/rotation/JPEG corruption
  curves) and error analysis (Grad-CAM, allergen-weighted confusion pairs) that
  drove {n_fixes} documented model/UX fixes.

## Full-stack

- Designed and built a FastAPI modular monolith (PostgreSQL + pgvector, S3-compatible
  storage, Postgres-backed job queue) powering a React Native (Expo) scanner app
  with {n_endpoints} endpoints, JWT auth with rotating refresh tokens, and cached
  nutrition lookups at {cached_p95} ms p95 (USDA FoodData Central + Open Food Facts).
- Implemented an evidence-typed allergen engine (curated ontology, {n_synonyms}+
  synonym/derivative rules, may-contain/facility statement detection) with a
  release-gating safety test suite of {n_safety_fixtures} fixtures — the app never
  renders an "allergen-free" verdict by construction.
- Built a grounded per-scan assistant: deterministic tools + pgvector RAG over a
  curated corpus with enforced citations, prompt-injection defenses tested against
  {n_injection_fixtures} attack fixtures, and free-quota graceful degradation.

## MLOps

- Ran the full model lifecycle on $0 infrastructure: resumable Kaggle training,
  W&B experiment tracking/registry with staged promotion gates (parity, calibration,
  latency, safety suite), models baked into images for atomic rollback, and drift
  monitoring from prediction/correction metadata (no raw-image retention).
- Shipped CI/CD (GitHub Actions) with release-gating safety tests, security
  scanning, schema-drift checks, and deployment smoke tests to a free-tier
  production stack serving {n_beta} beta testers.

## Rule

Numbers marked `{…}` must trace to: model card, bench report, or W&B — reviewers
may be shown the artifact. If a claim can't survive "show me", it doesn't go on the
résumé (T-063 senior review enforces).
