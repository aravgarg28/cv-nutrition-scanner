# MVP Definition

The MVP is the smallest release a real allergy-managing beta tester (Priya) can use
end-to-end **and** that credibly demonstrates the four target roles (D2). It maps to
Releases 1–3 of the [ROADMAP](ROADMAP.md) delivered as one usable beta; Release 1
alone is the internal "walking skeleton".

## Included

| # | Item | Challenge & justification |
|---|------|---------------------------|
| 1 | Expo React Native app (camera, upload, results, history, profile, settings) | Challenged: a web app would be cheaper. Kept — React Native is a stated résumé goal (D2/D7) and camera UX is core. |
| 2 | Email+password accounts; no guest mode | Challenged: could skip auth for demo. Kept — real beta testers + health-adjacent profiles demand real auth (D1, D22). |
| 3 | Dietary profile: 9 US allergens, custom allergens, vegetarian/vegan/gluten rules | Core value; without a profile the product is a generic scanner (D19). |
| 4 | Single-food photo classification, top-5 + confidence, mandatory user confirmation | The CV centerpiece (D13, D14). |
| 5 | Low-confidence behavior: banner + manual food search | Safety-critical honesty (D14). Search also rescues out-of-vocabulary foods. |
| 6 | USDA FDC nutrition for the confirmed food: calories, protein, carbs, fat, fiber, sugar, sodium | Challenged: full panel? Trimmed to D17 core fields — reliable coverage, honest display. |
| 7 | Serving presets + manual adjustment, deterministic recompute | Smallest credible portion story (D18). No volume estimation. |
| 8 | Ingredient-label OCR: verbatim text, parsed ingredients, completeness indicator, inline correction | The allergen-evidence centerpiece (D13). |
| 9 | Allergen-term extraction with evidence-typed statuses (per ALLERGEN_POLICY) incl. synonym ontology and may-contain/facility detection | The differentiator; the safety model's main surface. |
| 10 | Barcode scan → Open Food Facts product data | Cheap, high-fidelity, rescues weak OCR. Challenged: could defer — kept because it is the *most accurate* allergen source and low effort. |
| 11 | Nutrition-facts panel scan — **core fields only** (serving size, calories, the D17 nutrient set) | Owner selected for MVP (D13). Scoped down from full-panel parsing; riskiest MVP item, staged last within the MVP (🟡 ratify scoping). |
| 12 | Scan history with per-scan delete | Needed for real use (Priya re-checks products) and demonstrates persistence design (D21). |
| 13 | Confidence/uncertainty display + source attribution on every result | Non-negotiable guardrail; also the portfolio differentiator. |
| 14 | Per-scan assistant Q&A, grounded in scan data + RAG over curated explainer docs, with citations and quota degradation | Challenged hard (LLM = extra surface + free-quota risk). Kept — RAG/LLM integration is a stated résumé goal (D2, D20); scope limited to grounded per-scan questions. |
| 15 | Data export + account deletion | Required by privacy principles with real users (D1, D21). |
| 16 | Containerized FastAPI modular monolith; PostgreSQL (+pgvector); object storage for images; free-tier hosting | Backbone (D6, D15). |
| 17 | Fine-tuned Food-101 classifier served via ONNX Runtime CPU; W&B-tracked experiments; evaluation report + model card | The ML/MLOps résumé core (D5). MVP ships with the best model available at cut time; experiments continue after. |
| 18 | Web demo page (upload → same pipeline) for recruiters | D8. Read-only demo account; no signup needed. |

## Explicitly excluded from MVP (with reasons)

- **Automated portion/volume estimation (MiDaS or otherwise)** — cannot be validated
  credibly from single uncalibrated images; research track (D18,
  [MIDAS_ASSESSMENT](../portion/MIDAS_ASSESSMENT.md)).
- **Multi-food plate detection/segmentation** — large ML scope; Release 4 experiment.
- **Menu, recipe, receipt, pantry scan modes** — separate parsing domains; postponed.
- **On-device inference** — Release 5 (D15).
- **Micronutrients, %DV goals, daily-intake aggregation** — D17/D9 deferrals.
- **Halal/kosher** — post-MVP, non-verdict framing required (D19).
- **EU/other regional allergen regimes** — D11.
- **Guest mode, social login, MFA** — D22; MFA revisited post-beta.
- **Push notifications, sharing, multi-device sync of drafts** — no MVP value.
- **Full nutrition-panel micronutrient parsing** — see #11 scoping.

## MVP acceptance bar

Priya's journey (J2 → J12 → J6 → J8 → J10) works on a real device via Expo Go against
the free-tier deployment; every result screen shows typed evidence and source
attribution; the classifier's measured metrics are published in the model card; no
screen anywhere renders a "safe" verdict. All safety-invariant tests
([ALLERGEN_TESTS](../testing/ALLERGEN_TESTS.md)) pass in CI.
