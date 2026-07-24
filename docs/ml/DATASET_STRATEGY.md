# Dataset Strategy

## Primary: Food-101

- **License:** images sourced from foodspotting; the dataset is distributed for
  research; **action item (R0):** verify current licensing terms for commercial-model
  training before beta (D24). If commercial training use is unclear, document the
  risk and decision; the trained model's *weights* usage posture is recorded in the
  model card. `[LICENSE REVIEW REQUIRED — R0 task]`
- **Coverage:** 101 classes × 1,000 images (750 train / 250 test per class, official
  split). Western/restaurant-dish skew; strong on plated dishes, weak on packaged
  foods (irrelevant — packaged foods use OCR/barcode paths), raw ingredients, and
  many regional cuisines.
- **Label quality:** training split intentionally noisy (~uncurated); test split
  clean. Plan for label noise (label smoothing E8; noise-robust findings reported).
- **Geographic bias:** documented in model card; class-inferred allergen hints table
  compensates only for covered classes.
- **Class imbalance:** none (balanced by construction) — macro vs weighted metrics
  will nearly coincide; still report both.
- **Image conditions:** user-submitted restaurant photos — closer to our domain than
  studio datasets, but still mismatched vs phone-in-kitchen/store. Mitigated by
  augmentation + custom eval set.

## Considered and deferred/rejected

| Dataset | Verdict | Reason |
|---|---|---|
| UECFOOD-100/256 | R4 candidate (detection boxes) | Research-use restrictions; Japanese-cuisine focus; license blocks product use → EXP only |
| Recipe1M(+) | Rejected for MVP | Recipe-image pairs serve retrieval/recipe tasks we don't ship; heavyweight; access restrictions |
| VIREO Food-172 | Rejected | Research-only license (D24 conflict) |
| Open Images food subset | R5 candidate | Broad but noisy labels; useful for OOD negatives + coverage expansion; CC-BY images with per-image attribution burden |
| FoodSeg103 | R4 candidate (segmentation) | Only needed for portion research; license review then |
| Nutrition-label / ingredient-OCR datasets | Use for OCR **evaluation** only | We don't train OCR; fixtures come primarily from self-captured photos (full rights) |
| Synthetic label generation | Adopted for OCR fixtures | Programmatic label renders (fonts/curvature/noise) for stress tests; unlimited, license-free |
| User-contributed images | R5, opt-in only (D16) | Consent-gated; review queue; poisoning controls (FEEDBACK_LOOP) |

## Custom evaluation sets (we build these; critical)

1. **Phone-domain eval set:** ~300–500 self-captured photos of real foods (owner +
   consenting friends), labeled with Food-101 classes where applicable + "OOV food" +
   "non-food". Measures the domain gap the product actually faces. Never used for
   training.
2. **OOD set:** non-food images + OOV foods for unknown-detection evaluation (E13).
3. **OCR fixture set:** self-captured label photos + synthetic renders
   (OCR_TEST_STRATEGY) with ground-truth transcriptions.
4. **Robustness suite:** programmatic corruptions (blur, brightness, rotation, JPEG)
   of the clean test split (EVALUATION_PLAN).

## Splits, leakage, hygiene

- **Splits:** keep Food-101's official train/test split for comparability. Carve
  validation (~10%, class-stratified) out of *train* only. Test set touched only for
  final reported metrics per experiment phase — validation drives all tuning.
- **Duplicate/near-duplicate detection:** perceptual hashing (pHash) across all
  splits at pipeline build; embedding-similarity (CLIP) pass for near-dupes;
  cross-split duplicates removed from train (never from test); counts reported in
  the data card.
- **Leakage prevention:** custom phone-domain eval photos are captured after split
  freeze and never enter training; augmentation applied only after splitting;
  class-mapping/threshold tuning uses validation only.
- **Class balancing:** not needed for Food-101; the pipeline still supports weighted
  sampling for future imbalanced additions.
- **Versioning:** every dataset build = manifest (file list + SHA-256 checksums +
  split assignment + pipeline git SHA) stored as a W&B artifact; training runs
  reference the manifest version (DATA_PIPELINE).
- **Data card:** produced per dataset version — provenance, license record, counts,
  known biases, dedup stats, split definitions. Template lives with MODEL_CARD.
- **Privacy:** Food-101 contains no user data. Self-captured eval sets: no faces/
  people/bystanders; EXIF stripped; contributors consent in writing (a one-line
  recorded consent is fine at this scale).
