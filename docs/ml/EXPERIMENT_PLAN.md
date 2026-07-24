# Experiment Plan

16 planned experiments, each answering a real question (no count-padding). Sequenced
to fit ~30 free GPU-hrs/week; later experiments depend on earlier winners. Every
experiment: hypothesis → config delta → primary/secondary metrics → stop criteria →
baseline comparison. Resource costs are estimates for a T4.

**Primary metric across the plan:** validation macro-F1 (accuracy co-reported).
**Standing secondary metrics:** top-1/top-5, ECE (post-temp-scaling), NLL, CPU p95
latency (for serving-relevant candidates), train GPU-hours.
**Standing stop criterion:** early stopping per TRAINING_PLAN; abort if val loss
diverges >2× baseline epoch-3 loss.

| ID | Name | Hypothesis | Config delta (vs E1 baseline) | Expected tradeoff | Cost (h) |
|----|------|-----------|-------------------------------|-------------------|----------|
| E1 | ResNet-50 baseline | A standard fine-tune sets a strong floor; everything must beat it to justify itself | Baseline recipe @224 | — | 6 |
| E2 | EfficientNetV2-S | Higher published ImageNet accuracy transfers to Food-101 | Arch swap; progressive resize 300→384 per its recipe | +accuracy vs +latency, +train cost | 10 |
| E3 | ConvNeXt-Tiny | Matches E2 accuracy with better CPU latency | Arch swap @224 | Similar accuracy, better CPU profile | 7 |
| E4 | CLIP zero-shot + linear probe | Off-the-shelf CLIP is a meaningful no-training reference; if it nears fine-tuned accuracy, training story must sharpen | CLIP ViT-B/32 prompts + probe on frozen features | No training vs weaker calibration control | 2 |
| E5 | LR sweep on E2/E3 winner | LR is the highest-leverage hyperparameter; default may be off | LR ∈ {3e-5, 1e-4, 3e-4}; AdamW vs SGD arm at best LR | Small acc deltas; risk of unstable high-LR arm | 12 (4 runs) |
| E6 | Augmentation policy: light vs heavy | Heavier augmentation narrows the phone-domain gap (custom eval set) even if val accuracy dips | Baseline policy vs strong policy | −val acc vs +phone-domain acc | 8 |
| E7 | Fine-tuning depth | Full unfreeze with layer-wise LR decay beats head-only and full-uniform | head-only vs full-uniform vs LLRD 0.8 | Compute vs accuracy | 10 (arms share warmup) |
| E8 | Label smoothing 0 vs 0.1 vs 0.2 | Smoothing helps with Food-101's noisy train labels and improves calibration | ls ∈ {0, 0.1, 0.2} | Accuracy ~flat; ECE/NLL improve | 9 |
| E9 | MixUp α=0.2 | MixUp regularizes and flattens confidence on ambiguous dishes | +MixUp | +robustness/ECE vs slower convergence | 6 |
| E10 | CutMix α=1.0 | CutMix helps texture-driven classes more than MixUp | +CutMix (vs E9) | Class-dependent gains | 6 |
| E11 | Temperature scaling | Post-hoc calibration materially lowers ECE at zero accuracy cost | Fit T on val for top-3 candidates | Strictly better ECE; no downside | <1 (CPU) |
| E12 | Test-time augmentation | 5-crop+flip TTA buys accuracy but breaks the CPU latency budget | TTA at eval on winner | +0.5–1% acc vs ~6× latency | 1 (CPU) |
| E13 | Unknown-food thresholding | Energy score beats max-softmax for OOD detection at equal false-accept rate | MSP vs energy vs max-logit on OOD set | Threshold complexity vs safer unknown state | 2 (CPU) |
| E14 | ViT-B/16 stretch | ViT fine-tune can top ConvNets on Food-101 but fails the CPU budget; valuable for the report's model-choice narrative | Arch swap @224, LLRD | +accuracy vs 3–5× CPU latency | 14 |
| E15 | Distill winner → MobileNetV3-L | Distillation recovers most teacher accuracy in a mobile-size student (enables R5 on-device) | KD (T=4, α=0.7) from winner | −accuracy vs 4× smaller/faster | 10 |
| E16 | INT8 quantization | Dynamic + static PTQ keeps accuracy within 1% while cutting CPU latency ~2× | ONNX Runtime quantization of winner (+E15 student) | −accuracy tolerance vs latency/size | 2 (CPU) |

Total ≈ 105 GPU-hours ≈ 4–6 weeks of free quota alongside other work — feasible.

## Sequencing & gates

1. **Wave 1 (E1–E4):** architecture field. Gate: pick serving contender(s).
2. **Wave 2 (E5–E8):** recipe tuning on the winner. Gate: freeze recipe.
3. **Wave 3 (E9–E13):** regularization + calibration + OOD. Gate: serving candidate
   + thresholds (τ, τ_u per SAFETY_MODEL) chosen on validation.
4. **Final:** 3-seed re-run of the chosen config; **test set evaluated once here**
   for reported metrics; model card written.
5. **Wave 4 (E14–E16):** stretch/mobile/quantization — after MVP model ships.

## Comparison discipline

- One factor per comparison; shared dataset artifact version and seeds across arms.
- All runs land in one W&B project with the tag taxonomy in EXPERIMENT_TRACKING;
  the experiment report (docs/ml/reports/) links run IDs — numbers are never
  hand-copied.
- Negative results are kept and reported (e.g., "TTA rejected: +0.6% top-1 for 6.2×
  latency") — that's the evaluation-judgment story hiring managers actually value.
