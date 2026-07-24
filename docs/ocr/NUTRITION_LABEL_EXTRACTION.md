# Nutrition Label Extraction

US Nutrition Facts panels (2016 FDA format primary; legacy format tolerated).
**MVP scope (D13/D17, 🟡 ratified scoping): core fields only** — serving size,
servings per container, calories, total fat, sodium, total carbohydrate, dietary
fiber, total sugars, added sugars, protein. Saturated/trans fat, cholesterol,
vitamins/minerals: parsed opportunistically but not surfaced until R5.

## Extraction approach

Panel is detected as a section (OCR_ARCHITECTURE stage 8: "Nutrition Facts" anchor +
box geometry). Within it:
1. **Row segmentation** by y-coordinate clustering of tokens.
2. **Field anchoring** by fuzzy keyword match per field (`Calories`, `Total Fat`,
   `Sodium`, …) with known synonyms (`Sugars` vs `Total Sugars` legacy).
3. **Value+unit capture** right-of-anchor (or same-row) regex:
   `(\d+[\.,]?\d*)\s*(g|mg|mcg|kcal|Cal)?` plus `%DV` column capture (ignored for
   display, used for cross-validation).
4. **Serving size**: quantity + unit + optional gram weight in parentheses
   (`2/3 cup (55g)`); fraction glyphs (⅔) normalized.

## Structured output

`NutritionPanel{ serving_size:{text, quantity?, unit?, grams?}, servings_per_container?,
fields: {calories:{value, unit, ocr_confidence, span}, total_fat_g, sodium_mg,
carbohydrate_g, fiber_g, total_sugars_g, added_sugars_g, protein_g, …},
completeness, format_detected }` — every field carries confidence + source span;
absent fields are absent (never 0).

## Units, validation, normalization

- Canonical units: g / mg / kcal; conversions deterministic (NUTRITION_CALCULATION).
- **Plausibility validation** per field (flag, don't silently fix):
  - calories 0–1200/serving; sodium 0–5000 mg; macros 0–150 g; fiber ≤ carbs;
    added sugars ≤ total sugars; sugars ≤ carbs.
  - **Atwater cross-check:** 4×protein + 4×carbs + 9×fat within ±30% of stated
    calories → else `inconsistent` flag on the panel.
  - %DV cross-check where captured (e.g., sodium %DV × 2300 mg ≈ value) → mismatch
    flags likely OCR digit error.
- Flagged fields render with a "check this value" chip and require user confirmation
  before the panel is saved to history (SAFETY_MODEL human-confirmation rule).

## Missing values & OCR confidence

- Missing → "not read from label"; the UI offers manual entry.
- Fields below token-confidence floor → shown struck-light with "unreadable — tap to
  enter" affordance.
- Whole-panel completeness < threshold → panel labeled partial; totals never
  extrapolated.

## Regional differences

Out of scope for MVP (D11): EU per-100g format, kJ energy, different rounding rules.
The schema keeps `format_detected` and per-field units so EU support (R5+) extends
rather than rewrites. A non-US panel detected (kJ anchor, "per 100g" header) →
honest error: "Only US Nutrition Facts panels are supported right now."

## User confirmation flow

Extracted panel → review screen (editable fields, flags visible) → user confirms →
values stored as `user_confirmed: true` and only then usable in serving math. Raw
panel + corrections retained for provenance.
