# Allergen Tests

**The release-gating suite.** Fixtures in `tests/fixtures/allergen/` as YAML:
`{id, description, input (ingredient text | OCR result | OFF payload | scan
context), profile, expected: [{allergen, status_code, rule_family}], forbidden_ui:
[strings]}`. Every ALLERGEN_POLICY status must be reachable and correct; the
forbidden-strings check runs on rendered output for every case.

## Fixture catalog (initial; grows with every real-world miss)

**Direct declaration**
- A1 "Contains: milk, soy" → DECLARED ×2.
- A2 "CONTAINS WHEAT" caps/no colon variant → DECLARED.
- A3 Ingredient IS allergen: "peanuts" in list, no Contains line → DECLARED.

**Synonyms & derivatives**
- B1 "whey" → milk SYNONYM (derivation text present).
- B2 "tahini" → sesame SYNONYM. B3 "albumin" → egg SYNONYM.
- B4 "semolina" → wheat SYNONYM; gluten rule also fires.
- B5 ambiguous: "natural flavor" → milk POSSIBLE_SYNONYM only (never SYNONYM).

**Compound ingredients**
- C1 "enriched flour (wheat flour, niacin)" → wheat via child ingredient.
- C2 nested: "chocolate chips (sugar, chocolate liquor, soy lecithin)" → soy.
- C3 and/or oils: "vegetable oil (canola and/or soybean)" → soy SYNONYM
  (alternative=true still warns — asymmetry).

**Statements**
- D1 "May contain traces of tree nuts" → MAY_CONTAIN.
- D2 "Processed in a facility that also processes peanuts" → FACILITY.
- D3 Both declared and may-contain for different allergens → correct pairing, S1
  above S2 ordering.

**OCR damage**
- E1 misspelling within fuzzy bound: "peanuts" OCR'd as "peanuls" → DECLARED via
  fuzzy (uncertain variant if token confidence low).
- E2 guardrail: "pine nut" must NOT match peanut; "nutmeg"/"coconut"* /"water
  chestnut"/"butternut" per ontology rules (*coconut → ambiguous note behavior).
- E3 low-confidence token match → POSSIBLE_SYNONYM + OCR-uncertain framing.
- E4 low completeness (40%) + no milk terms → INSUFFICIENT (NOT_FOUND demotion).

**Missing/partial**
- F1 no ingredient section found → INSUFFICIENT for all profile allergens.
- F2 label cut mid-list (completeness 75%, above floor) + no match → NOT_FOUND with
  completeness shown; footer present.
- F3 photo-only scan (no label) + profile milk → CLASS_RISK only if hints table has
  it; otherwise INSUFFICIENT-flavored "photos can't show ingredients" framing;
  never NOT_FOUND.

**Conflicting sources**
- G1 OFF tags say milk; OCR list shows no milk terms → both shown with provenance;
  conflict banner; no merge (test asserts DECLARED-from-OFF + NOT_FOUND-from-OCR
  coexist with source labels).

**Non-profile & custom**
- H1 label declares egg; profile has no egg → "Other allergens declared" collapsed
  section, not a profile warning.
- H2 custom allergen "annatto" exact match in list → custom-match status with the
  limited-coverage framing. H3 custom fuzzy near-miss guardrail (no match on
  "amaranth").

**UI invariants (rendered-output tests)**
- I1 forbidden strings absent in every case ("safe", "allergen-free", "all clear"…).
- I2 NOT_FOUND never green/checkmarked (style token assertion).
- I3 S1–S3 rows expanded by default; footer literal present on every evidence render.
- I4 class-hint copy contains "we have not detected anything" literal.

**Profile lifecycle**
- J1 profile edit adds sesame after scan viewed → reopening scan re-evaluates
  (sesame rows appear). J2 profile unavailable → "can't check" state, zero silent
  omissions.

## Regression policy

Any real-world allergen miss during beta becomes a fixture (with the actual OCR
text, product identifiers redacted) **before** the fix merges. The catalog only
grows.
