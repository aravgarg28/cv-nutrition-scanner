# Model Card — Template

One card per released model version (`docs/ml/model-cards/<name>-vN.md`). Fields in
`[brackets]` are filled from measured artifacts only — a card with invented numbers
is a release blocker.

---

# Model Card: Food Classifier [name] v[N]

## Model details
- **Architecture:** [e.g., ConvNeXt-Tiny, 28.6M params] · **Input:** [224×224 RGB,
  ImageNet normalization] · **Output:** 101-class distribution + temperature
  [T=… fitted on validation]
- **Training:** fine-tuned from [checkpoint + license] on [dataset artifact
  `food101-dataset:vN`]; recipe: [config artifact/run link]; W&B run: [link]
- **Format:** ONNX opset [N], [size MB]; parity vs PyTorch within [tolerance]
  (test link)

## Intended use
Ranking candidate food identities (top-5) for **user confirmation** inside
SnapNutrition. Confidence drives UI framing only. Downstream: nutrition lookup and
class-inferred allergen *hints* (S4) for the **user-confirmed** class only.

## Out-of-scope use (must not)
- Any decision without user confirmation.
- Allergen detection of any kind (a photo cannot reveal ingredients).
- Foods outside the 101-class vocabulary (routed to "not sure" state).
- Portion, freshness, spoilage, or preparation-safety inference.

## Training data
Food-101: 101 classes × 750 train images; known properties: Western/restaurant skew,
intentionally noisy train labels, balanced classes. License status: [record R0
review outcome]. Dedup: [counts from data card]. Validation: [10% stratified carve-out].

## Evaluation data
- Official Food-101 test split (25,250 images) — evaluated [once, date].
- Phone-domain eval set v[N]: [count] self-captured photos (never trained on).
- OOD set v[N]: [composition].
- Robustness suites: [corruption params version].

## Metrics (measured — see report [link])
| Metric | Official test | Phone-domain |
|---|---|---|
| Top-1 | [ ] | [ ] |
| Top-5 | [ ] | [ ] |
| Macro-F1 | [ ] | [ ] |
| ECE (post-calibration) | [ ] | [ ] |
| NLL | [ ] | — |
3-seed mean±std for headline numbers: [ ].
CPU latency (serving container, batch-1, incl. preprocessing): p50 [ ] / p95 [ ].
OOD AUROC [ ]; false-accept at τ_u: [ ]. Robustness retention curves: [link].
Operating thresholds shipped: τ=[ ], τ_u=[ ] (chosen on validation, rationale link).

## Limitations
- [From ERROR_ANALYSIS: worst class families, confusion pairs, high-confidence error
  count, quality-slice cliffs.]
- Vocabulary: 101 largely Western dishes; many cuisines unrepresented — the model
  cannot name what it never saw.
- Domain gap: official-test metrics overstate real-world performance; use the
  phone-domain column.

## Biases & ethical considerations
- Cuisine coverage bias: [per-cuisine-bucket F1 table]. Consequence: users eating
  underrepresented cuisines get more "not sure" states and weaker hints — a fairness
  asymmetry we disclose rather than hide.
- The model must never be positioned as an allergen-safety mechanism (see intended
  use); misuse risk is mitigated by product design (confirmation UX, S4 framing,
  ALLERGEN_POLICY).

## Safety boundaries
Ships only with: calibrated confidence + thresholds above; "not sure" routing; UI
that requires confirmation. Changing any threshold requires re-running the safety
fixture suite (ALLERGEN_TESTS + framing tests).

## Deployment conditions
Serving: ONNX Runtime CPU, [container image tag]; preprocessing from
`packages/…/preprocessing.py` [version]; registry alias [production/vN]; rollback:
previous alias documented in MODEL_REGISTRY.

## Data card (companion)
Dataset version, provenance, license record, exclusion log: [link].
