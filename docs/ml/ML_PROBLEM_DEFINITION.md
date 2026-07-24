# ML Problem Definition

The system decomposes into distinct problems. For each: I/O, ground truth, metrics,
failure modes, data needs, whether ML is necessary (vs deterministic logic), and MVP
inclusion. Guiding rule: **ML only where deterministic code cannot do the job.**

## 1. Image quality assessment
- **Input:** uploaded RGB image. **Output:** quality score + reasons (blur, exposure,
  resolution).
- **Ground truth:** synthetic degradations of clean images + small hand-labeled set.
- **Metrics:** correlation between quality score and downstream task success.
- **Failure modes:** rejecting usable images (friction); passing unusable ones
  (silent bad results).
- **ML necessary?** **No.** Deterministic: variance-of-Laplacian blur metric,
  histogram exposure stats, resolution checks. Revisit learned IQA only if heuristics
  demonstrably fail. **MVP: yes (deterministic).**

## 2. Food classification
- **Input:** photo of a single dominant food. **Output:** calibrated distribution over
  101 classes, top-5 surfaced.
- **Ground truth:** Food-101 labels (train 75,750 / test 25,250 as published).
- **Metrics:** top-1/top-5 accuracy, macro-F1, per-class F1, ECE (post-calibration),
  NLL; latency and size as serving constraints. See EVALUATION_PLAN.
- **Failure modes:** similar-class confusion (see ERROR_ANALYSIS); domain shift
  (phone photos vs dataset); high-confidence errors — the worst kind, mitigated by
  calibration + confirmation UX.
- **Data:** Food-101 (DATASET_STRATEGY); custom phone-photo eval set.
- **ML necessary?** Yes — the core CV problem. **MVP: yes.**

## 3. Unknown-food / out-of-vocabulary detection
- **Input:** classifier logits/features. **Output:** binary "in-vocabulary?" signal
  driving the "not sure" state.
- **Ground truth:** held-out non-food images (e.g., Caltech/ImageNet non-food
  subsets, license permitting) + non-Food-101 foods.
- **Metrics:** AUROC for OOD detection; false-accept rate at chosen operating point.
- **Failure modes:** confident nonsense on non-food (embarrassing + erodes trust);
  over-triggering "not sure" (friction).
- **ML necessary?** Piggybacks on the classifier: max-softmax-probability threshold
  baseline, energy score as experiment (E13). No separate model in MVP. **MVP: yes
  (threshold-based).**

## 4. Multi-food detection — **not MVP** (R4 experiment)
Object detection (e.g., fine-tuned RT-DETR/YOLO-class model) over meal plates.
Requires detection labels Food-101 lacks (UECFOOD-256 has boxes; license review
required — research-only restrictions likely make this EXP-only). Deferred.

## 5. Food segmentation — **not MVP** (R4, only if portion research proceeds)
Needed only as a portion-estimation dependency. FoodSeg103 exists (license review
needed). Deferred with portion track.

## 6. Portion estimation — **not MVP** (R4 research; see docs/portion/)
MVP uses deterministic serving presets (D18). No ML.

## 7. OCR
- **Input:** label/panel photo. **Output:** text lines + boxes + per-token confidence.
- **Ground truth:** fixture set of labeled label photos (OCR_TEST_STRATEGY) with
  transcriptions.
- **Metrics:** character/word error rate on fixtures; field-level accuracy for panel
  extraction; allergen-term recall (the safety-relevant metric — a missed "peanut"
  matters more than average CER).
- **Failure modes:** curved/glossy packaging, small fonts, low light → see
  completeness indicator + asymmetry principle.
- **ML necessary?** Yes, but **pretrained** (PaddleOCR) — we do not train OCR models.
  **MVP: yes (pretrained + deterministic pre/post-processing).**

## 8. Ingredient normalization
- **Input:** raw OCR ingredient-list text. **Output:** ordered list of canonical
  ingredient entities with spans.
- **Ground truth:** annotated fixture labels.
- **Metrics:** parse accuracy on fixtures (boundary F1, canonicalization accuracy).
- **ML necessary?** **No** for MVP: grammar/regex parser (commas, parentheses,
  "and/or") + dictionary lookup with fuzzy matching (edit distance ≤ 2 with
  guardrails). LLM-assisted normalization considered post-MVP only as a suggestion
  layer, never authoritative. **MVP: yes (deterministic).**

## 9. Allergen entity extraction
- **Input:** normalized ingredients + raw text. **Output:** evidence-typed matches
  (ALLERGEN_POLICY statuses).
- **Ground truth:** ALLERGEN_TESTS fixture catalog.
- **Metrics:** recall on declared/synonym fixtures (target: no misses on catalog);
  precision tracked to manage alert fatigue.
- **ML necessary?** **No.** Curated ontology + rule matcher. Deterministic,
  auditable, testable — exactly what a safety surface needs. **MVP: yes.**

## 10. Nutrition mapping
- **Input:** confirmed class or product. **Output:** FDC/OFF record reference.
- **Ground truth:** curated class→FDC mapping table (101 rows, hand-reviewed).
- **Metrics:** mapping coverage (101/101) + spot-check plausibility review.
- **ML necessary?** **No.** Curated table + deterministic lookup. **MVP: yes.**

## 11. Retrieval (RAG)
- **Input:** user question + scan context. **Output:** ranked corpus chunks.
- **Ground truth:** retrieval eval set (question → relevant doc) built from corpus.
- **Metrics:** recall@k on eval set; citation correctness downstream.
- **ML necessary?** Yes — pretrained embedding model (open sentence-transformers);
  no training. **MVP: yes (R3).**

## 12. Natural-language generation (assistant)
- **Input:** question + tool results + retrieved chunks. **Output:** grounded, cited
  answer within MEDICAL_BOUNDARIES.
- **Ground truth:** AI_EVALUATION suites (refusals, citations, injection).
- **Metrics:** pass rates on evaluation suites; human review sample.
- **ML necessary?** Yes — hosted free-tier LLM (D20); no training. **MVP: yes (R3).**

## Summary table

| Problem | Approach | Trained by us? | MVP |
|---|---|---|---|
| Image quality | Deterministic heuristics | No | ✅ |
| Food classification | Fine-tuned CNN/ViT | **Yes** | ✅ |
| Unknown detection | Threshold/energy on classifier | No (calibrated) | ✅ |
| Multi-food detection | Object detection | Maybe (R4) | ❌ |
| Segmentation | Pretrained/fine-tuned | Maybe (R4) | ❌ |
| Portion | Presets (deterministic) | No | ✅ (presets) |
| OCR | PaddleOCR pretrained | No | ✅ |
| Ingredient parsing | Grammar + dictionary | No | ✅ |
| Allergen extraction | Ontology + rules | No | ✅ |
| Nutrition mapping | Curated table | No | ✅ |
| Retrieval | Pretrained embeddings + pgvector | No | ✅ |
| Generation | Hosted LLM, tool-grounded | No | ✅ |

The only model *we* train in the MVP is the food classifier — which is where the
training-rigor story (W&B, evaluation, calibration, ONNX) concentrates.
