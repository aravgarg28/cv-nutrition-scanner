# Demo Scenarios

The polished 8-scene demonstration (recruiters, interviews, README GIFs). All scenes
run on the **demo account** with seeded fixtures (DEMO_DATA) — reproducible, no live
external dependencies, works even if FDC/OFF/LLM are down.

1. **Clear classification.** Photo of a distinctive dish (e.g., a clean sushi
   fixture) → confident top-1, confirm in one tap → nutrition with USDA source chip.
   *Shows: the happy path is fast and sourced.*
2. **Ambiguity done honestly.** A chocolate-mousse-vs-cake-style fixture → top-5
   matters; presenter picks #2 → everything recomputes. *Shows: confirmation UX +
   calibrated humility; segue to the calibration work.*
3. **Packaged-food ingredient scan.** Granola-bar label fixture → verbatim "What we
   read" panel, parsed chips, completeness bar. *Shows: OCR pipeline + transparency.*
4. **Explicit allergen warning.** Same label, demo profile has tree-nut + sesame:
   "Contains: almonds" → DECLARED with source-span highlight; "may contain sesame"
   → MAY_CONTAIN prominent; "whey" → milk SYNONYM derivation on the milk-allergic
   sub-profile. *Shows: evidence-typed statuses — the differentiator.*
5. **Insufficient information.** Torn/partial label fixture → completeness 55% →
   INSUFFICIENT rows with "not a guarantee" framing; presenter narrates why
   NOT_FOUND would be wrong here. *Shows: the safety model working.*
6. **User correction.** Scene-2 scan corrected → downstream updates + correction
   recorded (show admin correction counter). *Shows: feedback loop + MLOps hooks.*
7. **Grounded question.** Assistant: "Why the milk warning?" → answer citing the
   whey evidence row + ingredient-definition chunk with citation chips. Then "Is
   this safe for me?" → boundary response. *Shows: RAG + tools + medical boundaries.*
8. **History & provenance.** History tab → reopen scene-4 scan → identical evidence;
   open source chips (USDA FDC id, OFF attribution, ontology version). *Shows: data
   provenance end-to-end.*

Each scene has: fixture ids, expected screen states, one-sentence narration, and a
fallback note (what to say if free-tier weather intervenes — e.g., cold start:
narrate the keep-warm design).
