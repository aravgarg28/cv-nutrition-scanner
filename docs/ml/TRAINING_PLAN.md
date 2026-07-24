# Training Plan

## Hardware assumptions

Kaggle free tier: T4×2 or P100, 12–30 h sessions, ~30 GPU-hrs/week; Colab free as
overflow (T4, preemptible). **Every run must be resumable** — sessions die.

Practical run sizing: Food-101 (~76k train images) at 224px on a T4 ≈ 8–15 min/epoch
depending on model → a 30-epoch fine-tune ≈ 4–8 h = one Kaggle session. Progressive
resizing (EfficientNetV2 recipe) budgeted at ~1.5×.

## Recipe (baseline; experiments vary one factor at a time)

- **Transfer learning:** ImageNet-pretrained weights (license-checked per
  MODEL_SELECTION).
- **Two-stage schedule:**
  1. *Head warmup* — freeze backbone, train new 101-class head, 2–3 epochs, LR 1e-3.
  2. *Full fine-tune* — unfreeze all, discriminative LRs (backbone 1e-4, head 1e-3),
     cosine decay to 1e-6, total 25–35 epochs. Layer-wise LR decay (0.8/block) as an
     experiment variant (E7 fine-tuning depth).
- **Optimizer:** AdamW (wd 0.01) baseline; SGD+momentum comparison in E5.
- **LR schedule:** cosine with 3-epoch linear warmup (full-tune stage).
- **Loss:** cross-entropy; label smoothing 0.1 (E8 varies); class weighting
  unnecessary (balanced dataset) but supported in code.
- **Batch size:** largest fitting memory (T4 16 GB: ~64 @224px for the contenders);
  **gradient accumulation** to effective 256 where recipes want it.
- **Precision:** AMP (fp16) mixed precision — 2× throughput on T4, standard.
- **Early stopping:** patience 7 epochs on val macro-F1; always also keep
  best-val-checkpoint regardless of stop.
- **EMA of weights:** optional flag, on for final candidate runs.

## Checkpointing & resumability (free-GPU survival kit)

- Checkpoint every epoch: model + optimizer + scheduler + scaler + epoch + RNG states
  + config hash. Rolling last-3 + best-val kept.
- Checkpoints pushed to W&B artifacts every N epochs (small models ~100–250 MB fit
  free-tier limits with rolling cleanup) so a dead Kaggle session resumes anywhere:
  `python -m training.train --resume wandb://run-id/checkpoint:latest`.
- Resume is exact: deterministic dataloader order restoration via stored RNG +
  sampler epoch.

## Seed management

- Config carries `seed`; seeds Python/NumPy/Torch(+CUDA). `torch.backends.cudnn
  .benchmark=True` accepted for speed (bitwise determinism not required across
  sessions; statistical reproducibility is). Headline result re-run with 3 seeds;
  mean±std reported (EVALUATION_PLAN).

## Configuration & tracking

- Single YAML config per run (model, resolution, augmentation policy, optimizer, LR,
  schedule, epochs, seed, dataset artifact version). Config IS the experiment
  definition; W&B logs it verbatim (EXPERIMENT_TRACKING).
- No hidden defaults drift: configs are complete (no "whatever the code does today").

## Hyperparameter search

No blind sweeps on free GPUs. Sequenced manual search per EXPERIMENT_PLAN: LR ∈
{3e-5, 1e-4, 3e-4} on the winning architecture (E5) is the only dedicated sweep;
other hyperparameters ride experiment comparisons. W&B Sweeps used to organize it
(free tier), grid not Bayesian at this scale.

## Calibration stage (post-training, part of "training" deliverable)

Temperature scaling fit on validation set for every candidate promoted to evaluation;
T stored in model metadata and applied at serving. ECE before/after recorded (E11).

## Outputs per run

W&B run (config, metrics curves, system stats) + best checkpoint artifact +
evaluation JSON (EVALUATION_PLAN schema) + confusion matrix + reliability diagram.
A run missing any of these is not comparable and gets tagged `incomplete`.
