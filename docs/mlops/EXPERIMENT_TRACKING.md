# Experiment Tracking (W&B, free tier)

## Structure

- **Project:** `snapnutrition-food101` (one project; separation via groups/tags —
  free-tier simplicity).
- **Runs:** one per training/eval execution, named `{exp_id}-{arch}-{variant}-s{seed}`
  (e.g., `E5-convnext_t-lr1e4-s42`). Resumed sessions continue the same run id
  (TRAINING_PLAN resumability).
- **Groups:** experiment id (`E5`) groups its arms; `wave-1`…`wave-4` tags mirror
  EXPERIMENT_PLAN sequencing.
- **Tags:** `baseline`, `contender`, `calibration`, `ood`, `distill`, `quant`,
  `incomplete` (missing required outputs), `final-candidate`.
- **Config:** the full YAML (TRAINING_PLAN) logged verbatim + dataset artifact
  version + git SHA + preprocessing module version. A run whose config can't
  reproduce it is tagged `incomplete`.
- **Metrics:** train/val loss, val top-1/top-5, val macro-F1 per epoch; final test
  metrics only on gate runs (EVALUATION_PLAN discipline); system metrics on.
- **Artifacts:** dataset manifests (`food101-dataset:vN`), checkpoints
  (`{arch}-ckpt:vN`, rolling cleanup), ONNX exports (`{arch}-onnx:vN`), evaluation
  JSONs + plots (`eval-{run}:vN`), OCR/portion report inputs.
- **Reports:** W&B Reports per wave gate summarizing arms → linked from
  `docs/ml/reports/` (repo markdown remains the canonical archive; W&B report is
  the interactive view).
- **Sweeps:** only E5 (LR grid) uses W&B Sweeps; config committed to repo.

## Lineage rules

model artifact → references dataset artifact + config + git SHA; eval artifact →
references model artifact + eval fixtures version. `wandb.use_artifact()` everywhere
(no path-based loads in tracked runs) so lineage graphs are complete — this is the
data-provenance story (D2/MLOps) made concrete.

## Free-tier hygiene

100 GB artifact quota: rolling checkpoint retention (last-3 + best per experiment;
final candidates keep all), datasets as reference artifacts (checksums, not bytes)
where the raw source is public, cleanup script `ml/scripts/wandb_gc.py` run at wave
gates.

## Offline/failed-session behavior

Kaggle sessions run `WANDB_MODE=online`; if the API is unreachable, `offline` mode
+ `wandb sync` on next session (checkpointed runs make this safe).
