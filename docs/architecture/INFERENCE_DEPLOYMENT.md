# Inference Deployment

Where the classifier (and OCR) actually run. Decision: **in the monolith container,
ONNX Runtime CPU** for MVP. This doc records the comparison the résumé target's
"AWS Lambda" idea demanded.

## Requirements

Single-image, user-interactive classification (batch=1), model ~25–110 MB ONNX,
PaddleOCR models ~15–30 MB, target p95 ≤ 2 s classify / ≤ 6 s OCR on CPU
(PERFORMANCE_BUDGET), beta traffic (tens of scans/day), $0 budget.

## Options

| Option | Cold start | Model size fit | Memory | CPU/GPU | Scaling | Cost | Latency | Ops complexity | ONNX | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **In-monolith, ONNX Runtime CPU** | Container boot loads sessions once (~2–5 s at deploy) | Fine | ~1–2 GB RSS with OCR | CPU | Vertical only (fine for beta) | $0 on free tier | Best (no network hop) | Lowest | Native | ✅ **MVP** |
| AWS Lambda (container image) | **Cold start = image pull + session init, seconds+, per concurrent instance**; painful for interactive UX at low traffic | 10 GB image limit OK | 10 GB max OK | CPU (no GPU) | Excellent burst | Free tier exists but per-request beyond; NAT/egress traps | Cold-start dominated | Medium | OK | ❌ for CV+OCR interactive path; **documented as viable for spiky offline jobs only**. The résumé-target assumption "Lambda for everything" is explicitly rejected: one request chaining EfficientNet+OCR+RAG in Lambda couples worst-case cold starts with a 15-min limit and no shared warm model cache |
| ECS/Fargate service | None (always-on) | Fine | Configurable | CPU | Good | **Not free** (~$15+/mo minimum) | Good | Medium | Native | The **AWS-target design** (AWS_ARCHITECTURE), not deployable under D0 |
| SageMaker endpoint | None | Fine | Fine | CPU/GPU | Managed | **Paid always-on** | Good | Medium-high | Native | Rejected (cost; overkill) |
| EC2 (t-class) | None | Fine | Small | CPU | Manual | Free tier 12-mo only, then paid; ops burden | OK | High (patching etc.) | Native | Rejected |
| App Runner | Scale-to-zero cold starts | Fine | Fine | CPU | Managed | **No always-free tier** | OK | Low | Native | Rejected under D0; noted as nice paid path |
| On-device ONNX/TFLite | n/a | Quantized ~15–30 MB | Device | NPU/CPU | Per-device | $0 | Excellent | App-update-coupled model releases; Expo dev-build required | ORT Mobile | **R5** (D15) |
| Hybrid (on-device fast + cloud verify) | — | — | — | — | — | — | — | Two inference surfaces | — | R5+ experiment |

## MVP serving design

- ONNX Runtime `InferenceSession` (classifier) + PaddleOCR sessions loaded at boot;
  `/readyz` gates traffic until warm.
- Session shared across worker threads (ORT is thread-safe for `run`); CPU thread
  count pinned to container size (`intra_op_num_threads`).
- Preprocessing via the shared `preprocessing` module (parity-tested).
- Model file pulled at image build (baked in) — no runtime registry fetch on the
  free host (deterministic deploys); model version = image tag component + recorded
  in every inference event.
- Free-host sleep/cold-start mitigation: keep-warm ping (GitHub Actions cron every
  10 min against `/healthz`) + mobile "waking up the scanner…" state for the
  first-request path.

## OCR placement

Same container (OCR_ARCHITECTURE): the queue serializes CPU contention; separate
OCR container documented as the first split seam if profiles show interference
(DOCKER_STRATEGY includes the optional compose profile).
