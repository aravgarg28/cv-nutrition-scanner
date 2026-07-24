# OCR Test Strategy

OCR quality is empirical; we test on a versioned fixture corpus, not vibes. Fixtures
live in `tests/fixtures/ocr/` (git-lfs or generated), each with ground-truth
transcription + expected structured extraction + expected allergen statuses.

## Fixture corpus composition

**Self-captured photos** (full rights; owner + consenting friends photograph real
products; brand names retained in private fixtures, synthetic brands for any
published fixtures):

| Category | Target count | What it stresses |
|---|---|---|
| Flat, well-lit ingredient labels | 10 | Baseline sanity |
| Curved packages (cans, bottles, wrappers) | 10 | Text-line curvature |
| Glossy/reflective packaging with glare | 8 | Contrast enhancement limits |
| Low-contrast printing (foil, embossed) | 6 | Recognition floor |
| Small-font dense labels | 8 | Resolution limits |
| Multi-column layouts | 6 | Reading-order logic |
| Rotated captures (±15°, ±45°, 90°) | 6 | Angle correction |
| Partial labels (cut off mid-list) | 6 | Completeness estimation + demotion |
| Poor lighting (dim, mixed, backlit) | 8 | Preprocessing |
| Motion blur (3 severities) | 6 | Quality gate thresholds |
| Torn/creased labels | 4 | Robustness of section detection |
| Nutrition panels (2016 + legacy formats) | 12 | Panel extraction |
| Allergen statements (Contains/May contain/Facility variants) | 12 | Safety-critical patterns |
| Spanish/bilingual US labels | 4 | Non-English graceful handling (out-of-scope notice, no garbage parse) |

**Synthetic renders** (unlimited, generated): programmatic label images from
structured ground truth — fonts × sizes × curvature warps × noise × JPEG ×
perspective. Used for: parser fuzzing, regression at scale, and stress matrices the
photo corpus can't cover. Generator lives in `ml/datasets/synthetic_labels/`; every
render's params are its provenance.

## Metrics tracked per engine/pipeline version

- Character error rate (CER) and word error rate (WER) overall + per category.
- **Allergen-term recall** (the safety metric): % of ground-truth allergen terms +
  statements recovered — reported per category; regressions here block merges.
- Field-level accuracy for nutrition panels (per field: exact / within-unit /missed).
- Section-detection accuracy (ingredient list found & bounded correctly).
- Completeness-estimate calibration: estimated vs true readable fraction.
- Latency per stage (CPU, serving container class).

## Test tiers

1. **Unit (CI, every PR):** parsers + normalizers on text fixtures (no OCR engine) —
   grammar, statements, fuzzy-guardrails; fast and deterministic.
2. **Pipeline (CI, every PR):** full pipeline on 12 canonical small fixtures with
   pinned engine version; asserts structured output + statuses; tolerance-based
   (expected-fields-present, not pixel equality).
3. **Corpus benchmark (manual/nightly):** full fixture corpus → metrics report
   committed to `docs/ml/reports/ocr-<date>.md`; run on engine upgrades and
   preprocessing changes.
4. **Safety fixtures (CI, blocking):** every ALLERGEN_TESTS OCR-dependent case.

## Engine-upgrade protocol

PaddleOCR version bumps: corpus benchmark before/after; allergen-term recall may not
regress in any category; CER regressions >2% absolute in any category require
investigation. Results recorded; engine version pinned in lockfiles and in every
stored OcrResult (provenance).
