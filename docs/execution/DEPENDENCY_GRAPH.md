# Dependency Graph

Epic-level DAG (task-level prerequisites are on each task card).

```
EP-01 foundation
  └→ EP-02 schemas ─┬→ EP-03 auth ─→ EP-04 profiles/consent
                    ├→ EP-05 images ─┐
                    ├→ EP-06 scan engine ─┬→ EP-10 serving ←─ EP-08 training ←─ EP-07 data pipeline
                    │                     ├→ EP-12 OCR ─→ EP-13 parsing ─→ EP-14 allergen engine
                    │                     └→ EP-15 barcode ─────────────────┘   (EP-14 also ← EP-04)
                    ├→ EP-11 nutrition ←──────────────(EP-10 confirm flow)
                    └→ EP-16 mobile foundation ─→ EP-17 capture/results ─→ EP-18 evidence/corrections
EP-09 evaluation ← EP-08 (parallel with EP-10+)
EP-19 history/privacy ← EP-06, EP-04
EP-20 assistant ← EP-14, EP-11, EP-04 (tools need evidence/nutrition/profiles)
EP-21 web demo ← EP-06, EP-10 (minimal), grows with EP-14
EP-22 security ← EP-03 onward (continuous, checkpointed)
EP-23 observability ← EP-01 (logging early), grows continuously
EP-24 deployment ← EP-01 (compose), staging after EP-06+EP-10
EP-25 demo prep ← EP-18, EP-20
EP-26 research ← MVP complete
```

## Critical path (MVP)

EP-01 → EP-02 → EP-06 → EP-10 (with EP-07/08 feeding the model) → EP-11 → EP-17 →
EP-12 → EP-13 → EP-14 → EP-18 → EP-20 → EP-25.

## Parallelizable lanes

- **ML lane** (EP-07→08→09) runs on Kaggle parallel to all backend work after EP-01;
  serving integrates whatever model is current (micro-model until first real one).
- **Mobile lane** (EP-16→17) parallel to backend after EP-02 (generated client +
  mocked API).
- **Deployment lane** (EP-24 compose/staging) parallel from EP-01.
- OCR lane (EP-12→13) parallel to nutrition (EP-11) once EP-06 exists.

## Human decision checkpoints (BUILD_SEQUENCE marks them inline)

Wave-1 model gate (AD-2), R2 panel-scope ratification (AD-1 🟡), ALLERGEN_POLICY
copy freeze before EP-14, LLM provider terms check before EP-20 (PRIVACY_MODEL),
beta go/no-go before real testers.
