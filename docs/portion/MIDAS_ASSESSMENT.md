# MiDaS Assessment

MiDaS appears in the original résumé target ("use MiDaS for portion-size
estimation"). This assessment explains why that claim, as stated, is not defensible,
and what role MiDaS can honestly play.

## What MiDaS produces

MiDaS (and successors: DPT, Depth-Anything class models) performs **monocular
relative depth estimation**: for each pixel, a value ordering scene points by
relative distance, trained across mixed datasets with scale-and-shift-invariant
losses. Output is unitless — typically an affine-ambiguous inverse-depth map.

## Relative vs metric depth — why scale is missing

A single uncalibrated 2D image is geometrically scale-ambiguous: a small bowl close
up and a large bowl far away can project identically. MiDaS's training explicitly
discards scale/shift to learn across heterogeneous data, so its output is defined
only up to an unknown affine transform per image. Recovering metric depth requires
external information:
- known camera intrinsics AND a known-size object in frame, or
- hardware depth (LiDAR/ToF/stereo), or
- known camera height/pose + planar-scene assumptions, or
- a metric-depth model fine-tuned per camera (still error-prone cross-device).

## Why food volume is especially hard

Even with metric depth from one viewpoint you get a **visible-surface** map, not a
volume: the food's underside and occluded geometry are unobserved (a dome of rice vs
a hollow shell look identical). Volume additionally needs segmentation (which foods?
where does plate end?), height/shape completion assumptions per food geometry, and
density (g/cm³ varies ~4× across foods and preparations). Errors compound
multiplicatively: segmentation error × depth error × shape-prior error × density
error. Segmentation bleed onto the plate rim alone can swing volume estimates
drastically.

## What claims would be valid vs misleading

**Valid:** "MiDaS provides relative depth that can support figure-ground separation
or qualitative 'closer/farther' cues"; "with a reference object supplying scale and
segmentation, coarse volume ranges are estimable — we measured X% MAE against
weighed ground truth" (only after PORTION_EVALUATION produces X).
**Misleading (banned):** "estimates portion size from a photo using MiDaS";
"calculates calories from your photo"; any point-estimate grams/calories from
monocular depth without validation data and error bars.

## Segmentation-error propagation

In any depth+segmentation stack, mask errors dominate: over-segmentation inflates
area (and volume) linearly; under-segmentation misses food entirely. The R4
evaluation must ablate: ground-truth masks vs predicted masks, to attribute error
honestly.

## Recommendation

| Scope | Verdict |
|---|---|
| MVP | **Excluded** (D18) |
| Research prototype (R4) | **Optional experiment**, secondary to the reference-object approach: MiDaS/Depth-Anything relative depth + reference-object scale + segmentation, evaluated per PORTION_EVALUATION with published error bars |
| Résumé/portfolio claims | Only post-measurement, with error bars; the *assessment itself* (this doc) is the portfolio artifact — it demonstrates exactly the judgment interviewers probe for |
| Excluded permanently | Any user-visible point-estimate volume from monocular depth alone |
