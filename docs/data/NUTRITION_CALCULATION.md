# Nutrition Calculation

All numeric nutrition logic is deterministic, pure, unit-tested code in
`packages/nutrition-core/` — importable by API and (as generated TS or via API) by
clients. **No LLM ever computes or transforms a nutrient number** (non-negotiable
guardrail #3).

## Canonical basis

NutritionRecords store values **per 100 g**. Display values are derived:
`value(serving) = value_per_100g × serving_grams / 100`.

## Operations

- **Serving multiplication:** grams-based as above; count-based servings (e.g., "2
  cookies (28 g each)") resolve to grams first. Serving without a gram weight (some
  FDC portions) → volume-only servings display with "approximate — no weight
  available" and no cross-unit conversion is attempted.
- **Unit conversion:** closed table — g↔mg↔mcg (×10³), kcal only (kJ→kcal ÷4.184 at
  the parsing boundary, stored canonical). No volume→mass conversion without a
  food-specific density from the data source (we do not guess densities).
- **Daily-value comparison:** FDA adult DV table (2,300 mg sodium, 28 g fiber, 50 g
  added sugar, etc.) versioned as data; %DV = value ÷ DV, displayed only for
  nutrients with official DVs; explicitly labeled "of the FDA daily value for
  adults" (no personalization in MVP).
- **Macronutrient totals / energy check:** Atwater (4/4/9) used only as a
  *consistency check* (NUTRITION_LABEL_EXTRACTION), never to fabricate missing
  calories.
- **Recipe totals:** out of MVP scope; function signatures reserved (sum of
  ingredient records by mass) for R5.
- **Per-100g normalization:** parsing OCR panels (per-serving) → per-100g requires
  serving grams; absent → record kept per-serving-only and flagged `basis:
  per_serving` (never silently assumed).

## Precision & rounding

- Internal: float64, no intermediate rounding.
- Display rounding (applied last, per nutrient, FDA-style): calories → nearest 1
  (nearest 5 above 50); macros g → 1 decimal <10 g else nearest 1; sodium mg →
  nearest 5 (nearest 10 above 140). Rounding table is data, tested against golden
  cases.
- Display never shows more precision than the source (source significant-digits
  respected).

## Missing-value algebra

`missing` propagates: any operation with a missing operand yields missing (rendered
"— not available"), never 0. Totals over partially-missing sets display "of listed
values" qualifiers. This is encoded in the types (`Optional[NutrientValue]` with
explicit combinators), not ad-hoc `if`s.

## Testing

- Property tests: linearity (2× serving = 2× values), unit round-trips, missing
  propagation, rounding idempotence.
- Golden tests: hand-computed fixtures incl. FDA rounding edge cases.
- Cross-check test: seeded FDC records recompute to their published per-portion
  values within rounding tolerance.
