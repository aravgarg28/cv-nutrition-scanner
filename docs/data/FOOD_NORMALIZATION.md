# Food Normalization

Canonical entities bridging model classes, OCR text, barcodes, and nutrition sources.
Full field-level schema in [DATA_MODEL](../architecture/DATA_MODEL.md); this doc
defines semantics.

## Canonical entities

- **Food** — an abstract edible kind at "as consumed" granularity (`pad thai`,
  `apple, raw`). Keyed internally; carries links to data-source records. Two origins:
  the 101 model classes and FDC foods surfaced via search.
- **Dish** — a Food that is a prepared/composite item (attribute on Food, not a
  separate table): drives "typical values / recipes vary" framing and S4 hint
  eligibility.
- **Ingredient** — a component substance (`whey`, `enriched flour`). Has canonical
  name, lexicon of surface forms, optional parent (compound), allergen links,
  diet-rule attributes (vegetarian/vegan/gluten status: yes/no/unclear + rationale).
- **Product** — a specific packaged SKU, usually barcode-keyed; links to Brand,
  ingredient list (parsed), allergen tags, nutrition record; provenance = OFF or
  user scan.
- **Brand** — manufacturer/label owner (from OFF); display + grouping only.
- **Serving** — a named portion of a Food/Product: label (`1 cup`), gram weight,
  source (FDC portion, label serving size, user-defined). The serving-math input.
- **Nutrient** — canonical nutrient definitions (calories, protein…, FDC nutrient
  IDs, canonical units, display rounding rules) — the D17 seven first-class, others
  storable.
- **NutritionRecord** — a set of NutrientValues per 100 g (canonical basis) with
  source provenance; conversions to servings are computed, never stored as facts.
- **Allergen** — the 9 US majors + user-custom entries (custom are profile-scoped,
  not global).
- **DietaryAttribute** — vegetarian/vegan/gluten flags on Ingredients with rationale
  and `unclear` as a first-class value.
- **DataSource** — FDC / OFF / user-OCR / curated-mapping; every retrieved or derived
  fact links to one (provenance is non-nullable).
- **Synonym** — surface-form lexicon rows: text form → entity, with type (exact,
  abbreviation, misspelling, derived-term) and per-form notes; powers ingredient
  matching and food search.

## Class→nutrition mapping semantics (the honesty contract)

A Food-101 class is a *visual category*, not a recipe. Mapping `pad_thai` → FNDDS
record asserts only: "here are typical nutrition values for dishes that look like
this." Consequences (all enforced in UI copy + API naming):
- Field name is `typical_nutrition`, not `nutrition`.
- Framing string on every class-derived nutrition card: "Typical values for
  {food} — actual dishes vary with recipe and portion."
- Class-derived values never combine with OCR-observed values in a single total.
- The mapping table row stores `mapping_confidence` (curator-assigned:
  high/medium/low) — low-confidence mappings (e.g., highly variable dishes like
  "casserole"-type classes) add "varies widely" to the framing.

## Ingredient lexicon construction

Seed sources (all free/public-domain-compatible): FDA allergen guidance term lists,
curated additive/E-number table, manually curated derivations (whey/casein/ghee →
milk; albumin → egg; tahini → sesame; etc. — full list in ALLERGEN_ONTOLOGY), plus
common-ingredient list assembled during R2 fixture work. Every lexicon row has a
provenance note. The lexicon is versioned; matcher results store lexicon version
(reproducible evidence).

## Identity & dedup rules

- Foods: FDC ID is the external anchor; internal foods without FDC links (rare)
  flagged for curation.
- Products: barcode (GTIN-13 normalized) is identity; re-scans update, not duplicate.
- Ingredients: canonical name unique; surface forms many-to-one; merging two
  canonicals is a migration with audit trail (evidence rows reference them).
