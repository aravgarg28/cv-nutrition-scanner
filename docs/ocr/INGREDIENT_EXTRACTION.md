# Ingredient Extraction

From OCR text to structured, evidence-linked ingredient and allergen-statement data.
All deterministic (ML_PROBLEM_DEFINITION #8/#9). Every extracted element keeps its
source span (character offsets into the verbatim OCR text) — the evidence chain
depends on it.

## Boundary detection

- Ingredient list starts at anchor `INGREDIENTS:` (case-insensitive, OCR-tolerant
  fuzzy anchor: `1NGREDIENTS`, `INGREDlENTS` etc. within edit distance 2).
- Ends at: next section anchor ("Contains", "Distributed by", "Nutrition Facts",
  nutrition-panel geometry) or end of block.
- Absent anchor → block classified `possible_ingredients` only if it matches
  list-shape heuristics (comma density, known-ingredient hit rate >40%); such blocks
  produce statuses at reduced certainty (POSSIBLE_SYNONYM instead of SYNONYM) and the
  UI labels the section "text that may be an ingredient list".

## Parsing grammar

- **Ordering preserved** (US labels: descending predominance) — order index stored.
- **Separators:** commas and semicolons at depth 0; "and" only inside final pairs.
- **Parentheses/brackets = compound ingredients:** `enriched flour (wheat flour,
  niacin, …)` → parent + children, each a full entity (children carry allergen
  matches: `wheat flour` → wheat). Nesting depth ≤3 supported; deeper → flatten with
  flag.
- **Percentages/qualifiers:** `sugar (12%)`, `organic milk` → qualifier stripped to
  canonical token, preserved as attribute.
- **Additives:** `E322`, `lecithin (soy)`, `natural flavor` → canonical additive
  entities; E-numbers mapped via additive table (used by diet rules: E120 carmine →
  not vegetarian, etc.).
- **"and/or" (oil blends):** `contains one or more of: canola, soybean oil` → all
  alternatives extracted, each flagged `alternative: true` — soy allergen match on an
  and/or soybean oil still raises SYNONYM status (asymmetry principle).

## Allergen statements (separate from list parsing)

Pattern families (fixture-tested, per ALLERGEN_POLICY status):
- `DECLARED`: `Contains: X[, Y…]` / `Contains X ingredients`.
- `MAY_CONTAIN`: `May contain [traces of] X`.
- `FACILITY`: `Processed in a facility that also processes X` / `Made on shared
  equipment with X` / `Manufactured in a plant that handles X`.
Patterns are a curated, versioned list (`allergen_statement_patterns.yaml`) — new
real-world phrasings from beta get added with fixtures.

## Normalization & matching

1. Token cleanup: case-fold, punctuation, unicode normalization.
2. Dictionary lookup against the ingredient lexicon (FOOD_NORMALIZATION): exact →
   canonical entity.
3. Fuzzy pass for OCR damage: Damerau-Levenshtein ≤2 for tokens ≥6 chars (≤1 for
   4–5 chars; none shorter) **with a guardrail list** of dangerous near-misses that
   must never fuzzy-merge (e.g., `peanut`↔`pine nut` style pairs curated in the
   ontology; reviewed in ALLERGEN_TESTS).
4. Unmatched tokens survive as `unrecognized` entities (visible to user, editable) —
   they are never dropped, and their presence demotes the scan's negative claims if
   they exceed a ratio threshold.
5. Allergen mapping via ALLERGEN_ONTOLOGY (synonyms, derivatives, ambiguous terms).
   Fuzzy-matched allergen hits emit `POSSIBLE_SYNONYM` (uncertain variant), exact
   hits emit `SYNONYM`/`DECLARED` per context.

## Misspellings & OCR uncertainty

- Per-token OCR confidence rides through parsing; a match built on any token below
  the confidence floor is downgraded to the uncertain status variant.
- The asymmetry principle (SAFETY_MODEL): low-confidence text may CREATE warnings,
  never absence — completeness/uncertainty demote only negative claims.

## Output schema (shared-schemas package)

`ParsedIngredientList{ source_text_span, completeness, items: [ParsedIngredient{
raw_text, span, canonical_id?, qualifiers[], children[], alternative, ocr_confidence,
allergen_matches: [AllergenMatch{allergen_id, status_code, rule_id, matched_span}]}],
statements: [AllergenStatement{type, allergens[], span, pattern_id}] }`
