# Training Pipeline

The repeatable path from dataset to production model. Stages are CLI commands
(`ml/`), runnable on Kaggle/Colab/local; CI runs the micro-subset smoke version
end-to-end on every ML-touching PR.

```
1 data validation → 2 training → 3 evaluation → 4 export → 5 parity
→ 6 packaging → 7 registration → 8 deployment → 9 smoke
```

1. **Data validation** — manifest checksums verified; split integrity (no cross-split
   ids); class counts; schema of metadata parquet. Fails → stop (no training on
   unvalidated data).
2. **Training** — `python -m training.train --config configs/E5_convnext_lr1e4.yaml`
   (TRAINING_PLAN recipe; resumable; W&B-tracked).
3. **Evaluation** — harness (EVALUATION_PLAN) on validation (+ test only at gates);
   emits eval JSON + plots artifact; calibration fit (temperature) happens here.
4. **Export** — ONNX per ONNX_STRATEGY (T baked in, metadata_props stamped).
5. **Parity** — PyTorch↔ONNX suite; pass → artifact aliased `candidate`.
6. **Packaging** — model baked into API image (`app-{sha}-model-{ver}` tag) by CI
   when a candidate is referenced in `configs/serving_model.lock`.
7. **Registration** — registry mirror row + gates checklist (MODEL_REGISTRY).
8. **Deployment** — staging auto-deploy of the image; production by manual promote
   (ENVIRONMENTS).
9. **Smoke** — deployed-environment test: readyz, one fixture image through
   `/v1/scans` full pipeline, threshold sanity (unknown fixture routes to unknown),
   latency spot-check. Fails → no promote / rollback.

## Orchestration choice

No Airflow/Kubeflow/Prefect — a Makefile + documented commands + CI smoke is the
right size for one trainable model and free-tier compute (rejecting orchestration
theater is itself a documented decision, AD-17). The stage boundaries above are the
seams if a real scheduler ever becomes justified.

## Reproducibility contract

Any registered model re-derivable from: git SHA + config + dataset artifact version
+ seed (statistical reproducibility; TRAINING_PLAN §seeds). The pipeline refuses to
register a model whose config or dataset ref is dirty/untracked.
