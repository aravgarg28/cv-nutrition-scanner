# ML Tests

Two contexts: **CI micro-model** (a tiny net trained seconds on the 2-class subset —
exercises the machinery on every PR) and **artifact tests** (run against real
checkpoints/ONNX at pipeline gates).

## Input/output contracts

- Input shape/dtype: (1,3,H,W) float32 per model metadata; wrong shape → typed error
  not crash.
- Output: shape (1,101); probabilities ∈ [0,1], sum 1 ± 1e-5; no NaN/Inf (NaN guard
  test with adversarial-ish extreme inputs: all-black, all-white, noise).
- Top-5 extraction: correct ordering, stable ties.

## Preprocessing parity (the classic silent killer)

- Single source: `preprocessing.py` — training-eval-serving all import it; test
  asserts training val-transform and serving transform produce **identical tensors**
  for the same bytes (byte-exact fixture set incl. EXIF-rotated, grayscale-source,
  CMYK-JPEG oddities).
- Resize interpolation, RGB order, normalization constants pinned by test against
  golden tensors (catches library-upgrade drift, e.g., Pillow resample changes).

## Determinism

- Inference: same input → same output across runs/threads (ORT determinism at fixed
  session config) — asserted on 32 fixtures.
- Training: statistical reproducibility only (TRAINING_PLAN); the *pipeline* test
  asserts config+seed round-trip (config logged == config loadable == rerunnable),
  not bitwise equality.

## Artifact loading

- Checkpoint load: strict key match (no silent missing/unexpected keys).
- ONNX session load: metadata_props complete (input size, normalization, T,
  thresholds, dataset version) — missing metadata fails boot (ONNX_STRATEGY).

## PyTorch ↔ ONNX parity (gate-blocking)

256 val images: max |Δprob| ≤ 1e-4; top-1 agreement 100%; top-5 set ≥ 99.5%
(ONNX_STRATEGY). Quantized variants: top-1 agreement vs fp32 ≥ 99%, macro-F1 delta
within E16 acceptance.

## Calibration & thresholds

- Temperature application: probs(T) match expected transform on golden logits.
- Threshold behavior: synthetic logit fixtures crossing τ and τ_u produce the right
  UI states (confident / low-confidence / unknown) through the API response mapper.
- OOD scoring: energy/MSP computation golden-tested; OOD fixture set routes to
  unknown at the shipped operating point (rate asserted within tolerance band).

## Invalid-image behavior

Corrupt bytes, zero-byte, 1×1 px, 30 MP bomb, wrong-signature files → typed
rejections at the right stage (UPLOAD_SECURITY boundary), never a prediction; scan
state lands in the correct failure state.

## Serving-layer tests

Concurrent inference (thread-pool) correctness under parallel fixture load; memory
ceiling respected (RSS budget assertion, coarse); readiness gating (no traffic
before session warm).
