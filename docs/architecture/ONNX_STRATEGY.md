# ONNX Strategy

## Export

- `ml/export/export_onnx.py`: PyTorch checkpoint → ONNX, opset 17, via
  `torch.onnx.export` (dynamo exporter evaluated when stable for our archs; recorded
  either way).
- **Dynamic axes:** batch only (`{0: "batch"}`); spatial dims fixed per model input
  size (serving is batch=1; fixed spatial simplifies runtime optimization).
- Graph includes: backbone + head + softmax + **temperature scaling** (baked as a
  final Div node with T from calibration) so serving gets calibrated probabilities
  without a separate step. Raw-logit output kept as a second graph output for
  OOD/energy scoring (E13).
- Operator compatibility: contenders (ResNet/ConvNeXt/EfficientNetV2/MobileNetV3)
  are standard-op; any exotic op discovered → export fails loudly in CI, no silent
  opset downgrade.

## Preprocessing contract

Preprocessing (resize/center-crop/normalize) stays **outside** the graph, in the
shared `preprocessing` module used by training, eval, and serving — one
implementation, parity-tested (AUGMENTATION_STRATEGY §parity). Rationale: image
decode/resize ops in-graph are brittle across ORT versions; a tested Python module
is simpler. The contract (input size, interpolation=bicubic, RGB order, float32,
ImageNet mean/std) is encoded as model metadata (ONNX metadata_props) and asserted
at session load — a model/preprocessor mismatch fails boot, not predictions.

## Validation & parity (CI-blocking, ML_TESTS)

- **Numerical parity:** N=256 sampled val images through PyTorch vs ONNX Runtime:
  max |Δprob| ≤ 1e-4, top-1 agreement 100%, top-5 set agreement ≥ 99.5%. Failures
  block artifact registration.
- **Output validation:** probabilities sum to 1 ± 1e-5; shapes; dtype; NaN guard.
- **Metadata check:** model card fields (version, dataset artifact, thresholds, T)
  present in metadata_props.

## Runtime

ONNX Runtime (CPU EP) pinned version; `intra_op_num_threads` = container CPUs;
graph optimization level `ORT_ENABLE_ALL`; session options recorded in inference
events (provenance).

## Quantization (E16)

Dynamic INT8 first (weights-only, no calibration set needed), static QDQ with
calibration subset second. Acceptance: top-1 drop ≤ 1.0 pt absolute AND macro-F1
drop ≤ 1.5 pts vs fp32 ONNX on validation, else rejected. Quantized artifacts get
their own parity suite (looser tolerance, same top-1 agreement bar vs quantized
baseline) and their own model-card row.

## Mobile support (R5)

ONNX Runtime Mobile / ORT format conversion for the distilled student (E15);
NNAPI/CoreML EPs evaluated then. Not an MVP concern beyond keeping ops standard.

## Performance benchmarking

BENCHMARK_PLAN owns methodology; this pipeline emits: p50/p95 single-image latency
(preprocess included and broken out), peak memory, model file size — on the serving
container CPU class, recorded per model version.

## Fallback behavior

Serving has **no** PyTorch fallback (torch not installed in the API image — size and
determinism). If the ONNX session fails to load → `/readyz` fails → deploy rolls
back to previous image (MODEL_REGISTRY rollback). If inference errors at runtime →
scan `classification_failed` state + retry; never a stale or random result.
