# Portion Estimation Options

Decision (D18): MVP ships **serving presets + manual adjustment**. This doc records
the full option analysis justifying that and scoping the R4 research track.

| Approach | Accuracy | UX cost | Device coverage | Training data needed | Calibration | Failure modes | MVP suitability |
|---|---|---|---|---|---|---|---|
| **User-selected serving presets + stepper** | As good as the user's judgment; honest framing | One tap–one slider | All | None | None | User misjudges; framed as their estimate | ✅ **Chosen** |
| Common serving-size presets (FDC portions) | Anchors user judgment with real weights | Zero extra | All | None | None | Preset misses odd portions → custom grams entry covers | ✅ part of chosen |
| Manual weight entry | Exact if user owns a scale | High (weighing food) | All | None | None | Few users bother | ✅ supported as optional input |
| Reference object in image (credit card/coin) | Area scale becomes metric; volume still needs height assumptions; literature ~20–40% volume error under good conditions | User must carry/place object; social awkwardness | All | Segmentation labels | Per-image via object | Object detection fails; partial occlusion; non-flat foods break height assumptions | ❌ MVP; **R4 candidate (primary)** |
| Dual-image capture (stereo baseline by hand) | Structure-from-motion scale ambiguity remains without known baseline; brittle handheld | Two guided shots | All | None (geometry) but heavy engineering | Needs known camera intrinsics + baseline estimate | Feature-poor food surfaces; motion | ❌; R4 secondary at best |
| ARKit/ARCore depth (LiDAR/ToF or dense depth) | Metric scale available on supported devices; genuinely promising | Native modules + guided capture | **Fragmented** (LiDAR: Pro iPhones; ARCore depth varies) | Some validation data | Built-in | Device coverage; Expo dev-build required | ❌ MVP; R4/R5 candidate where hardware exists |
| Device depth sensors (raw) | Same as above | Same | Same | — | — | — | Same |
| MiDaS monocular relative depth | **Relative** depth only — no metric scale from one uncalibrated image (see MIDAS_ASSESSMENT) | Invisible to user (tempting!) | All | Volume ground truth for any mapping attempt | **Missing scale is the fundamental gap** | Confidently wrong volumes; propagates to nutrition | ❌ (would ship indefensible numbers) |
| Segmentation + geometric priors (food-shape templates) | Literature reports 20–50% MAE with reference scale; worse without | Invisible | All | Segmentation + volume GT | Needs scale source anyway | Amorphous foods (curry, salad) defeat templates | ❌; component of R4 stack |
| No portion concept (per-100g only) | n/a | Confusing ("100g of pad thai?") | All | None | None | Users misread per-100g as per-plate | ❌ rejected — worse honesty in practice |

## Rationale for the MVP choice

Every automated single-image path either lacks metric scale (MiDaS), lacks device
coverage (AR depth), or demands validation infrastructure (reference object +
segmentation + ground-truth weighing) that would dominate the MVP for a feature
whose honest error bars would still be wide. Presets anchored to FDC gram weights
give users a *credible, transparent* estimate and give the product honest framing
("per selected serving"). The research value of depth-based estimation is preserved
in R4 where it can be evaluated properly (PORTION_EVALUATION) without shipping
unvalidated numbers (SAFETY_MODEL).

## R4 research track scope (smallest credible)

Reference-object approach: user places a standard card; pipeline = card detection →
homography → food segmentation (pretrained/FoodSeg103-tuned, license permitting) →
area × class-conditioned height prior → volume → density table → grams, with
propagated uncertainty interval displayed as a range, never a point. Evaluated
against kitchen-scale ground truth per PORTION_EVALUATION before any user-visible
exposure (flag-gated, "experimental estimate" labeling).
