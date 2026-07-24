# Data Pipeline

Reproducible path from "nothing" to "training-ready dataset + manifest artifact".
Lives in `ml/datasets/`. Every step is a CLI command; CI runs a miniature smoke
version on a 2-class subset.

## Stages

1. **Download** — `python -m datasets.food101 download --dest data/raw/food101`
   Pulls the official archive (via torchvision or direct URL). Retries + resume.
2. **Verify** — checksum the archive (known SHA-256 pinned in config); verify file
   count (101,000) and per-class counts; fail loudly on mismatch.
3. **Extract & normalize layout** — canonical layout
   `data/food101/{class_name}/{image_id}.jpg`; re-encode nothing (bytes preserved);
   quarantine unreadable files (log + exclude + count in manifest).
4. **Metadata extraction** — per image: dimensions, aspect, file size, sharpness
   (variance of Laplacian), mean brightness → `metadata.parquet`. Feeds dedup, EDA,
   and robustness sampling.
5. **Cleaning** — drop/quarantine: corrupt decodes, extreme dimensions (<64px side),
   grayscale anomalies. All exclusions logged with reasons; never silently.
6. **Deduplication** — pHash (hamming ≤ threshold) within and across splits;
   CLIP-embedding near-dupe pass (cosine ≥ threshold, human-spot-checked). Cross-split
   dupes removed from train. Dedup report in data card.
7. **Split generation** — official test split respected; validation carved from train
   (stratified 10%, seeded). Output: `splits.json` (image_id → {train,val,test}).
8. **Manifest & versioning** — `manifest.json`: dataset name/version, source URL,
   archive checksum, per-file checksums (or a rolled-up Merkle root for size), split
   file hash, pipeline git SHA, exclusion log hash, timestamps. Uploaded as W&B
   artifact `food101-dataset:vN`.
9. **Caching for training** — optional resized-image cache (e.g., 512px longest side,
   quality 95) as a *derived* artifact keyed to the manifest + resize params — raw
   data is never mutated. Kaggle/Colab runs consume the cached artifact for speed.

## Augmentation position

Augmentation (AUGMENTATION_STRATEGY) is **training-time only**, applied after
splitting, inside the dataloader — never materialized into the dataset, never applied
to val/test (except the explicit robustness suite, which is a separate evaluation
artifact built from test images with recorded corruption params).

## Reproducibility rules

- Every artifact (dataset, cache, split, robustness suite) is content-addressed and
  W&B-versioned; training configs reference artifact versions, not paths.
- Seeds: split seed and any sampling seeds recorded in the manifest.
- The pipeline is idempotent: re-running with the same config + raw archive yields
  byte-identical manifests.

## Storage & free-tier fit

- Raw Food-101 ≈ 5 GB: lives on Kaggle datasets (free hosting, attachable to
  notebooks) and locally; NOT in git.
- W&B free tier (100 GB artifact storage) holds manifests, split files, small derived
  sets, and model checkpoints — not the raw archive (reference-only artifact entry
  with checksums instead).
- Local dev uses a 5-class subset fixture (~250 MB) committed to nothing — generated
  by `--subset` flag; CI uses 2-class × 50-image micro-subset generated on the fly.

## Failure behavior

Any stage failing leaves previous artifacts untouched (write-to-temp, atomic rename).
A partial dataset can never masquerade as complete: consumers load via manifest only.
