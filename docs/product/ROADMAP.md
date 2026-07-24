# Roadmap

Six releases. R0–R3 constitute the public MVP/beta; R4–R5 extend it. No calendar dates
(D3: no deadline, quality first); each release ends with its exit criteria met.

---

## Release 0 — Scope, contracts, and evaluation design

**User outcome:** none user-visible; the foundation that prevents downstream invention.
**Features:** none.
**ML work:** dataset audit (Food-101 license/quality), evaluation design finalized,
class→FDC mapping table drafted, class→allergen-hint table drafted.
**Application work:** monorepo scaffold, shared schema package (Pydantic + TS types),
CI (lint/type/test), Docker Compose local stack (Postgres+pgvector, MinIO), seed
scripts.
**Safety requirements:** ALLERGEN_POLICY language frozen v1; safety fixture catalog
written *before* any allergen code.
**Tests:** CI green on scaffold; schema round-trip tests.
**Success metrics:** a contributor (Implementer) can run the full local stack from
LOCAL_DEVELOPMENT.md in one sitting.
**Risks:** over-scaffolding. Mitigation: only structures needed by R1 tasks.
**Exclusions:** any product feature.

## Release 1 — Classification + nutrition walking skeleton

**User outcome:** photograph a single food → confirm from top-5 → see USDA nutrition
per adjustable serving, with confidence and sources. Web demo shows the same pipeline.
**Features:** auth, capture/upload, classification, confirmation, search, nutrition,
serving math, minimal history record, consent disclosure.
**ML work:** data pipeline, ResNet-50 baseline, first fine-tuned contender,
W&B tracking live, ONNX export + parity, evaluation harness (top-1/5, F1, ECE),
serving via ONNX Runtime CPU.
**Application work:** FastAPI monolith modules (identity, scans, inference, nutrition),
Postgres schema v1, image storage, async job runner, mobile screens 1–8 (minimal),
web demo page, free-tier deployment.
**Safety requirements:** confirmation-before-nutrition enforced; low-confidence
framing (D14); typed-information UI components exist.
**Tests:** API integration, model parity, serving-math property tests, E2E happy path.
**Success metrics:** E2E scan works on a real phone against the hosted backend;
model card v1 with measured metrics.
**Risks:** free-tier cold starts hurting demo; mitigate with keep-warm ping +
"waking up" UI state.
**Exclusions:** OCR, barcode, allergens, assistant.

## Release 2 — Label OCR, barcode, and allergen evidence

**User outcome:** Priya's core journey: scan a label or barcode and see evidence-typed
allergen statuses against her profile.
**Features:** dietary profile, ingredient-label OCR + correction, barcode/OFF lookup,
allergen ontology + matcher, may-contain/facility detection, diet rule engine,
class-inferred hints, image-quality assessment, unknown-food state, nutrition-panel
scan (core fields, staged last).
**ML work:** OCR pipeline evaluation on fixture set; calibration + threshold
experiments; continued classifier experiment matrix.
**Application work:** ocr/allergens/products modules; evidence UI; profile screens.
**Safety requirements:** full ALLERGEN_POLICY rendering; ALLERGEN_TESTS catalog green;
completeness indicator; human-factors review of warning hierarchy (HUMAN_FACTORS).
**Tests:** OCR fixtures, allergen rule fixtures, injection-shaped OCR content tests.
**Success metrics:** label→evidence journey <30 s on fixtures; zero "safe" verdicts
possible by construction (UI has no such component).
**Risks:** OCR quality on curved/glossy packaging → completeness indicator + barcode
fallback + correction UX are the mitigations, not perfect OCR.
**Exclusions:** assistant, export/delete UI (data model ready).

## Release 3 — Personalization polish, history, grounded assistant (MVP cut)

**User outcome:** full beta product: history, managed child profile, per-scan
assistant, export/delete. **This is the public beta / MVP.**
**Features:** history list/detail, managed profiles, assistant with tools + RAG +
citations + quota fallback, training-data opt-in, export, deletion, admin read-only
endpoints, monitoring dashboards.
**ML work:** RAG corpus curation + embedding pipeline; AI evaluation suite; model
registry aliases + promotion gates.
**Application work:** assistant module, pgvector retrieval, jobs for export/delete,
observability hardening.
**Safety requirements:** MEDICAL_BOUNDARIES behaviors tested; injection suite green;
assistant refusal quality sampled ≥50 prompts.
**Tests:** AI_EVALUATION, E2E scenarios catalog, load smoke test.
**Success metrics:** ≥10 beta testers onboarded; correction rate and warning rates
being measured; recruiter demo script executable start-to-finish.
**Risks:** LLM free-quota exhaustion mid-demo → deterministic fallback tested.
**Exclusions:** everything in R4/R5.

## Release 4 — Portion & multi-food experiments (research track)

**User outcome:** optional "experimental" badge features; primary value is the
published research write-up (portfolio depth).
**Features (experimental, flag-gated):** reference-object portion estimation
prototype; multi-food detection prototype; multi-shot label stitching.
**ML work:** MIDAS_ASSESSMENT experiments executed (relative-depth demo + honest
write-up); segmentation trials; PORTION_EVALUATION protocol with known-weight ground
truth.
**Safety requirements:** experimental outputs never feed allergen logic; portion
numbers labeled "experimental estimate".
**Success metrics:** written evaluation with real error bars; go/no-go decision
recorded for each experiment.
**Risks:** rabbit holes — timebox each experiment to its stop criteria.
**Exclusions:** shipping any unvalidated estimate as a default.

## Release 5 — Hardening, wider coverage, on-device

**User outcome:** faster, more robust app; broader food coverage.
**Features:** on-device quantized model (dev-build), offline barcode cache,
full-panel micronutrient parsing, halal/kosher flags (non-verdict), pescatarian/
low-sodium rules, EU allergen groundwork, MFA.
**ML work:** distillation/quantization for mobile; dataset expansion beyond Food-101
(licensing permitting); retraining pipeline from consented feedback.
**Application work:** performance work per BENCHMARK_PLAN; AWS migration if/when
budget exists (architecture already documented).
**Safety requirements:** re-run full safety suite after model swap; on-device model
gets its own model card.
**Success metrics:** benchmark deltas reported; feedback-loop retrain demonstrated
end-to-end on consented data.
**Risks:** Expo Go limits for native ONNX → dev-build channel (already planned, D7).
**Exclusions:** monetization (still out of scope).
