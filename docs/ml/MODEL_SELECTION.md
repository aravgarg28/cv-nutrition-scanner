# Model Selection

For the food classifier (the one model we train). Selection is **experiment-driven**:
this doc narrows the field and defines the comparison; EXPERIMENT_PLAN runs it; the
winner is recorded in the decision log and model card. EfficientNetV2 is a contender
because it earns it on the merits below — not because it appears in the résumé target.

## Constraints (from decisions)

- Training: free Kaggle/Colab T4/P100, ~30 GPU-hrs/wk, resumable (D5).
- Serving: **CPU** inference on free-tier hosting (D6/D15) — this is the binding
  constraint. Target <2 s single-image CPU latency (PERFORMANCE_BUDGET).
- ONNX export must be clean (opset ≤ 17, no exotic ops).
- Later: quantize/distill for on-device (R5).
- License: weights must permit commercial use (D24) — timm pretrained weights vary;
  verify per-checkpoint license at selection time (most torchvision/timm ImageNet-1k
  weights are fine; some ImageNet-21k/distilled checkpoints need review).

## Candidate comparison

Sizes/latency: published figures, order-of-magnitude guides only — **our own
benchmarks decide** (BENCHMARK_PLAN). No accuracy numbers are claimed for our task
until measured.

| Model | Params | ImageNet top-1 (published) | CPU friendliness | ONNX | Fine-tune cost (T4) | Notes |
|---|---|---|---|---|---|---|
| ResNet-50 | 25.6M | ~80% (modern recipe) | Good | Excellent | Low | **Baseline.** Boring, well-understood, everything supports it. |
| EfficientNetV2-S | 21.5M | ~83.9% | Moderate (depthwise convs are CPU-mediocre) | Good | Moderate (300–384px trains) | Strong accuracy/param; progressive-resize training fits free GPUs. |
| ConvNeXt-Tiny | 28.6M | ~82.1% | Good (7×7 dw convs vectorize well) | Excellent | Moderate | Modern ConvNet; simple export; strong fine-tuning behavior. |
| MobileNetV3-Large | 5.4M | ~75.2% | Excellent | Excellent | Low | Mobile track (R5); also a distillation student. |
| MobileViT-S | 5.6M | ~78.4% | Good | Moderate (attention ops) | Low-mod | Alternative mobile track. |
| ViT-B/16 | 86M | ~81–84% (data-dependent) | Poor on CPU | Good | High | Stretch only; heavy for our serving budget. |
| Swin-Tiny | 28M | ~81.3% | Moderate | Moderate (window ops) | Moderate | No clear edge over ConvNeXt-T for this task; export friction. |
| CLIP ViT-B/32 (zero-shot/linear-probe) | 151M total | n/a | Poor | Good | None (probe: low) | **Diagnostic comparator**: zero-shot Food-101 baseline + linear probe; also candidate embedding source. Not a serving candidate. |
| Object detection (YOLO/RT-DETR class) | — | — | — | — | — | Wrong problem for MVP (single-food classification); R4 only. Note YOLO AGPL licensing issue → prefer RT-DETR/DETR-family if R4 proceeds. |

Per-model dimensions requested (accuracy, size, latency, memory, training cost,
exportability, ONNX/mobile compatibility, interpretability, dataset needs) are
summarized above and expanded in the experiment configs; interpretability for all
CNNs via Grad-CAM (ERROR_ANALYSIS), attention rollout for ViTs.

## Recommendations

- **Simple baseline:** ResNet-50, standard fine-tune recipe. Everything is measured
  against this. (E1)
- **Strong cloud model (primary contenders):** EfficientNetV2-S **vs** ConvNeXt-Tiny,
  head-to-head under equal budget (E2/E3). Decision metric: macro-F1 and
  post-calibration ECE at equal CPU latency budget, ties broken by CPU p95 latency
  (serving reality) then training cost.
- **Mobile-friendly model (R5):** MobileNetV3-Large first (best tooling), MobileViT-S
  as comparison; trained by distillation from the cloud winner (E15).
- **Stretch model:** ViT-B/16 fine-tune (E14) — only if GPU budget allows after the
  core matrix; expected to lose on CPU latency but instructive for the report.
- **Diagnostic:** CLIP zero-shot + linear probe (E4) as a "how far does no-training
  get you" reference line in the report.

## What would change the recommendation

- If CPU p95 for both contenders exceeds budget → drop to MobileNetV3-Large as the
  serving model (accepting accuracy loss, measured not guessed).
- If Food-101 fine-tuning shows the contenders within noise of ResNet-50 → ship
  ResNet-50 (simplicity wins ties; the report says so honestly).
- If a required pretrained checkpoint has a non-commercial license → substitute a
  cleanly-licensed checkpoint even at accuracy cost (D24).
