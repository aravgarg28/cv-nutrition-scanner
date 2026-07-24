# Camera UX

Capture quality is the top determinant of OCR and classification quality — the
camera screen is where accuracy is won. Guidance is mode-specific, visual (overlay),
and never blocking.

## Mode-specific overlays & guidance

**Food photo:** rounded-frame guide ~80% of viewport; hints rotate: "fill the frame
with one food" · "shoot from slightly above" · "good light helps".
*Live preview-frame analysis (blur variance sampling) requires camera frame
processors that Expo Go cannot host (ADVERSARIAL_REVIEW 3.1) — it is a dev-build
enhancement (R5). Expo-Go-compatible quality signals used in MVP: post-capture
blur/exposure check on the captured image (screen 6), gyro level line, and
exposure-metadata dim-light detection.*

**Ingredient label:** rectangular guide, portrait; hints: "flatten the package if you
can" · "fill the frame with just the ingredient list" · "avoid glare — tilt slightly"
· torch suggestion in low light (auto-detected via exposure). Post-capture client
check adds "text looks small — get closer" when detected text height is low
(fast heuristic, not full OCR).

**Nutrition panel:** same as label + "capture the whole panel including the top
'Nutrition Facts' line" (anchor needed by the parser).

**Barcode:** reticle + live detection (expo-camera); success haptic + auto-proceed;
>8 s without detection → "try moving closer / steady" then manual-entry fallback.

## Distance / rotation / lighting rules communicated

- Distance: labels sharpest at 10–20 cm with fill-the-frame guide (drives text
  height ≥ ~20 px at capture res).
- Rotation: overlay level line (device gyro) nudges within ±10° — the OCR pipeline
  corrects more, but starting straight is free accuracy.
- Lighting: exposure-based dim warning + one-tap torch; backlight detection ("light
  behind the package — turn around") when histogram is bimodal-extreme.

## Multiple images / retake

- MVP: one image per scan; retake replaces pre-upload (screen 6) or post-result via
  "rescan" (new scan, linked in history).
- Wrap-around labels: guidance text sets expectation ("can't fit it all? scan the
  part with the ingredient list; completeness will show what we read") — multi-shot
  stitching is R4 (FEATURE_CATALOG).

## Client-side pre-upload processing (contract with IMAGE_LIFECYCLE)

Downscale longest side → 1600 px, JPEG q85, apply EXIF orientation, strip metadata
client-side too (belt+suspenders; server re-strips). Target payload ≤ ~500 KB.

## Never-block principle

All quality signals are suggestions; users can always proceed (SAFETY_MODEL: results
then carry quality caveats). Rationale: a hard gate that misfires teaches users to
fight the app; a soft gate plus honest downstream framing preserves trust.
