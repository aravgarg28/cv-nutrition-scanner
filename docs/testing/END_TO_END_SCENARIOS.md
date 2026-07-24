# End-to-End Scenarios

Run against staging per release (Maestro where automatable; scripted manual
checklist otherwise). Each scenario: preconditions → steps → assertions.

1. **Clear single food.** Seeded user w/ milk allergy; scan fixture photo (distinct
   Food-101 dish). Assert: candidates ≤ 5 s (budget), top-1 plausible, confirm →
   nutrition card with USDA SourceChip + "typical values" framing; serving adjust
   recomputes deterministically; S4 hint only if hints table says so.
2. **Ambiguous food.** Fixture chosen from a known confusion pair. Assert: top-5
   contains both plausible classes; "could be one of…" framing; user picks #3;
   downstream uses confirmed class.
3. **Unknown food.** Non-Food-101 fixture (e.g., regional dish) + non-food fixture.
   Assert: unknown state, guess framing, search rescues (FDC search → confirm);
   no nutrition before confirmation.
4. **Blurry image.** Blurred fixture. Assert: client pre-check suggests retake
   (non-blocking); proceeding yields quality-caveated result framing.
5. **Complete packaged-food label.** Label fixture with "Contains: wheat, soy" +
   clean list; profile: wheat. Assert: DECLARED status w/ span; other-allergens
   section shows soy; footer literal; completeness shown; verbatim panel matches.
6. **Partial ingredient label.** Cut-off fixture (low completeness) + profile milk,
   no milk terms visible. Assert: INSUFFICIENT (demotion) — **not** NOT_FOUND; copy
   invites rescan.
7. **High-risk allergen path.** Profile: peanuts (severe-user surrogate); label with
   "may contain peanuts". Assert: MAY_CONTAIN top-priority placement, expanded,
   non-dismissable; assistant asked "is this safe?" → boundary script, no
   reassurance, forbidden strings absent.
8. **Failed nutrition API.** FDC mock forced 5xx (staging flag). Assert: cached
   foods still resolve w/ "cached" tag; uncached search shows provider_unavailable
   state; circuit opens (admin endpoint shows it); no fabricated values.
9. **User correction.** Scenario-2 scan; correct top-1 to another class. Assert:
   nutrition + hints recompute; correction event recorded with training_eligible
   reflecting consent; opt-in toggle flips future events' eligibility.
10. **Data deletion.** User with scans/threads/consents requests account deletion
    (typed confirm + reauth). Assert: 202 → completion; login dead; API returns
    nothing for old ids; storage prefix empty (sweep assertion); tombstone + audit
    summary exist; export requested pre-deletion still downloadable until expiry?
    → **No**: deletion revokes export links (assert).
11. **Barcode happy + stale.** Known OFF fixture barcode → product data with
    provenance; stale fixture (>24 mo) → staleness warning. Unknown barcode → label-
    scan suggestion.
12. **Assistant quota degradation.** LLM mock 429 (staging flag). Assert: fallback
    summary card, `degraded: true`, notice copy, thread stores the fallback.
13. **Cold-start UX.** (Manual) Space asleep → open app. Assert: waking banner on
    Home, first scan succeeds after wake, no error toast storm.
14. **Multi-profile.** Dana-style: switch to managed child profile (milk) → scan
    scenario-5 fixture → milk DECLARED under child profile badge; switch back →
    re-evaluated for owner profile.
