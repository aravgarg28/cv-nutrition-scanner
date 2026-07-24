# Allergen Ontology

The curated knowledge base behind allergen matching. Deterministic, versioned data
(`packages/allergen-core/data/ontology.yaml`), never model-generated. Every entry
carries provenance. Matcher behavior consuming it is defined in
INGREDIENT_EXTRACTION; statuses in ALLERGEN_POLICY.

## Canonical allergens (FDA 9, D11)

milk · egg · fish · crustacean shellfish · tree nuts · peanuts · wheat · soy · sesame

Tree nuts and fish/shellfish are **families**: the ontology enumerates members
(almond, walnut, cashew, pecan, pistachio, hazelnut, macadamia, Brazil nut… ; salmon,
tuna, cod… ; shrimp, crab, lobster…) each mapping to the family allergen. FDA
guidance lists seed the enumeration; provenance per row.

## Entry structure

```yaml
- term: whey
  canonical_allergen: milk
  relation: derived        # is | derived | contains | ambiguous
  confidence: certain      # certain | contextual | ambiguous
  source: "FDA allergen labeling guidance; food-science reference"
  notes: "milk protein fraction"
  surface_forms: [whey, whey protein, whey powder, sweet whey]
```

## Relation & confidence semantics

- `is` — the term IS the allergen (`peanuts`) → DECLARED when in ingredient list.
- `derived` — made from it (`whey`→milk, `tahini`→sesame, `semolina`→wheat,
  `albumin`→egg, `ghee`→milk) → SYNONYM status with derivation sentence.
- `contains` — composite that reliably contains it (`worcestershire sauce`→fish
  (anchovy) typically) → SYNONYM with "typically contains" wording; confidence
  `contextual`.
- `ambiguous` — may or may not (`natural flavor` (milk per FDA ambiguity discussions),
  `lecithin` unspecified-source, `mono- and diglycerides`) → POSSIBLE_SYNONYM only;
  never DECLARED/SYNONYM.

## Seed synonym highlights (full list in ontology file; curated at R2)

milk: casein, caseinate, whey, ghee, butterfat, lactalbumin, lactoglobulin, curds,
custard, paneer · egg: albumin/albumen, ovalbumin, lysozyme, meringue, mayonnaise ·
wheat: semolina, durum, farina, spelt, kamut, seitan, couscous, malt (wheat/barley
note: malt→barley affects *gluten rule*, not wheat allergen — dual-listed) · soy:
edamame, tofu, tempeh, miso, textured vegetable protein, soy lecithin · sesame:
tahini, benne, gingelly, sesamol · peanuts: groundnut, arachis oil, goober ·
tree nuts: marzipan (almond), praline, gianduja, nut meal/paste per member ·
fish: anchovy, surimi (fish), fish sauce · shellfish: scampi, krill.

## Regional naming & cross-contamination phrases

- US-first (D11); UK/AU variants included as surface forms where harmless
  (e.g., "prawn"→shrimp).
- Cross-contamination phrase patterns live with INGREDIENT_EXTRACTION
  (`allergen_statement_patterns.yaml`) — the ontology maps only terms; statements are
  syntax.

## Diet-rule overlay (shares the lexicon)

Ingredient entries also carry vegetarian/vegan/gluten attributes with rationale:
gelatin (not vegetarian: animal collagen), carmine/E120 (not vegetarian: insect),
rennet (unclear: animal or microbial), lactic acid (vegan-usually: fermentation,
`unclear` if context suggests dairy), malt/barley/rye (gluten). `unclear` renders as
"can't tell — depends on source" (first-class outcome, D19).

## Fuzzy-match guardrail list

Curated pairs that must never merge under fuzzy matching (INGREDIENT_EXTRACTION):
maintained here with test fixtures, e.g. `pine nut`≠`peanut`, `nutmeg`≠nut-family
(nutmeg is a seed — explicitly excluded surface form), `coconut`≠tree-nut family
(FDA historically listed coconut as tree nut; current FDA guidance (2025) treats
coconut as not a major tree-nut allergen — we KEEP coconut as `ambiguous` toward
tree nuts with a note, conservative asymmetry), `water chestnut`≠nut, `butternut
squash`≠nut, `grapenut`→wheat not nut.

## Custom allergens (profile-scoped)

User-defined terms match by exact + guarded fuzzy text only (no curated synonyms) —
matched as a distinct evidence flavor with the caution shown at creation (J2). If a
custom term equals a known ontology entity (user types "casein"), it links to the
canonical entity and inherits full synonym power.

## Governance

Ontology changes require: provenance note, fixture addition (positive + negative),
ALLERGEN_TESTS pass, and a changelog entry. The ontology version is recorded on every
AllergenEvidence row (reproducibility of past scans).
