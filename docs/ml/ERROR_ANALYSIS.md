# Error Analysis Protocol

Run after each phase gate (EXPERIMENT_PLAN) on the current best model. Output feeds
the experiment backlog, the model card's limitations section, and UI copy decisions.

## Structured passes

1. **Confusion-pair inspection** — top 30 confused class pairs from the confusion
   matrix; for each: 16 sampled misclassified images reviewed, hypothesis recorded
   (visual similarity? presentation? label noise?). Known Food-101 hard families to
   check first: steak/filet mignon/pork chop; chocolate cake/chocolate mousse;
   ravioli/gnocchi/dumplings; ramen/pho/miso soup; club/pulled-pork sandwiches.
2. **Allergen-weighted confusions** — confusion pairs annotated by whether the two
   classes differ in commonly-associated allergens (from the class→allergen hints
   table). Pairs where a miss changes an S4 hint (e.g., pad thai ↔ lo mein: peanut
   association differs) are listed in the model card and get retraining priority.
3. **High-confidence errors** — all test errors with calibrated confidence >0.85:
   individually reviewed; categorized (ambiguous image / label error / true model
   failure). This is the safety-relevant tail; count reported per model.
4. **Mixed dishes & occlusion** — sampled review of composite plates (e.g., huevos
   rancheros with many components) and heavily-occluded items; documents the
   single-food assumption's breaking point → feeds R4 multi-food scoping.
5. **Presentation & regional variants** — per-class sampling across visual styles
   (homemade vs restaurant plating); phone-domain eval set errors reviewed one by one
   (it's small); regional dishes absent from Food-101 catalogued from OOV routing.
6. **Background/context bias probe** — Grad-CAM on correct and incorrect predictions
   for 20 classes: does the model attend to the food or to plates/tables/context?
   Documented with example heatmaps in the report.
7. **Lighting/quality slice** — test metrics sliced by the metadata sharpness/
   brightness quantiles (DATA_PIPELINE metadata): does accuracy collapse in the
   bottom decile? Sets the image-quality warning threshold empirically.
8. **Class-imbalance check** — trivial for Food-101 (balanced) but the harness slices
   by class support anyway, ready for future imbalanced data.

## Tooling

- Error-browser notebook: filterable grid (true class, predicted, confidence,
  quality metrics, Grad-CAM overlay) reading evaluation JSON + image paths.
- Every reviewed error gets a one-line disposition in
  `docs/ml/reports/error-analysis-<gate>.md`.

## Exit questions per analysis round

1. What single change most likely improves macro-F1? (→ new experiment or data work)
2. Any confusion that changes allergen hints? (→ hints table or UX mitigation)
3. Any systematic overconfidence pocket? (→ calibration/threshold adjustment)
4. Anything to disclose in the model card limitations? (→ write it now)
