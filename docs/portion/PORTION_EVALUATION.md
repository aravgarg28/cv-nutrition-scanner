# Portion Evaluation Protocol (R4 research track)

Prerequisite for ANY user-visible automated portion estimate. Cheap, kitchen-scale
science — zero budget compatible.

## Ground-truth collection

- **Known weights:** every sample weighed on a kitchen scale (±1 g class) before
  photographing. Weight is the primary target (grams), volume secondary (derived for
  a subset via water displacement for rigid items / measuring-cup packing for
  granular items).
- **Foods (≥12, spanning geometry classes):** mounded granular (rice, pasta),
  liquid/semi-liquid in vessels (soup, yogurt), discrete units (apple, bread slice,
  cookies), amorphous spreads (salad, curry), stacked/irregular (chicken pieces).
- **Portions per food:** 3–5 sizes spanning realistic range (half → double typical
  serving).
- **Plates/vessels (≥5):** small/large plates, shallow/deep bowls, dark/light/
  patterned surfaces (segmentation stressors).
- **Devices (≥2):** different phone cameras (different intrinsics/FOV).
- **Angles (3 per sample):** ~90° top-down, ~45°, ~30° oblique — protocol records
  angle bucket.
- **Reference object:** standard card placed per protocol in every frame (and one
  no-card control shot per sample for ablation).

Target ≥ 300 evaluated images (12 foods × 4 portions × 3 angles × 2 devices ≈ 288,
plus controls). Manifest with per-image metadata; this becomes a small published
dataset artifact (our own photos, license-clean).

## Metrics

- Absolute + percentage error on grams (primary): MAE, MAPE, and error distribution
  (report P50/P90 — tails matter more than means for trust).
- Volume error for the displacement subset.
- Sliced by: food geometry class, angle, device, plate type, card-visible vs control.
- Ablations: ground-truth mask vs predicted mask (error attribution per
  MIDAS_ASSESSMENT); with/without class-conditioned height prior.
- Uncertainty calibration: does the reported range contain truth at the stated rate?

## Go/no-go criteria (pre-registered)

Ship as flag-gated "experimental estimate" only if: P50 gram error ≤ 25% AND P90 ≤
60% on the held-out food set AND displayed ranges achieve ≥80% coverage. Otherwise:
publish the negative result in the research write-up (still full portfolio value)
and keep presets. These thresholds are pre-registered here to prevent
moving-the-goalposts after results exist.

## Reporting

`docs/ml/reports/portion-<date>.md`: setup photos, per-slice tables, ablation
attribution, decision. No summary number without its distribution.
