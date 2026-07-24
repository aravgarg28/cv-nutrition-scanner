# Human Factors

How real people will actually read, misread, and over-trust this UI — and the design
rules that follow. Applies to mobile and web surfaces.

## Alert fatigue

Risk: every scan for a 3-allergen user produces ≥3 status rows; if everything shouts,
nothing does.
Rules:
- Only S1–S3 use warning styling; S4 uses info styling; S5/S0 neutral.
- One decision-support footer per screen, not per row.
- "Other allergens declared" (non-profile) is collapsed by default.
- The professional-advice suggestion appears at most once per assistant thread.
- Track warning-rate metrics (OBSERVABILITY) — if >80% of scans show S1–S3 for
  typical testers, review matcher precision (may be over-matching).

## Color use

- **Never green / success styling for `NOT_FOUND`** — the single most dangerous UI
  mistake available to this product. `NOT_FOUND` is neutral gray/slate.
- S1 declared: high-contrast red-family; S2 trace/facility: orange-family — distinct
  hue AND distinct icon (color alone never carries meaning: ~8% of male users have
  color-vision deficiency).
- All statuses pair color + icon + text label; verified with a CVD simulator in
  design review.
- Dark-mode variants maintain the same contrast ratios (WCAG AA: ≥4.5:1 text).

## Severity wording

- Verbs describe *our reading*, not the food: "the label we read says…", "we found /
  did not find … in readable text" — never "this product contains" (except quoting a
  declaration) and never "this product is free of…".
- No superlatives, no fear language ("DANGER!") — S1 is calm and factual; the facts
  are alarming enough.
- Trace warnings phrased as manufacturer statements, which they are.

## Accessibility

- Screen-reader labels on every status row read: status name, allergen, evidence
  sentence, source ("Declared: sesame. The label says contains sesame. Source:
  scanned label text.").
- Dynamic type support up to OS accessibility sizes; status rows reflow, never
  truncate the evidence sentence.
- Touch targets ≥44 pt; one-handed reachability for the scan button (Priya in a
  store aisle).
- Camera flows usable with VoiceOver/TalkBack: capture button labeled, guidance
  overlays announced.

## Cognitive load

- Result screens layer information: status list first; evidence text behind one tap;
  raw OCR panel behind an explicit "What we read" control.
- Top-5 candidates show name + confidence bar only; details after selection.
- The confirm step is one tap on a candidate — not a separate modal chain.

## Confirmation bias

- Users scanning "to be allowed to eat it" will read S0 as permission. Mitigations:
  S0 wording contains the counter-statement in the same sentence block (not a
  separate footnote); completeness percentage sits inside the S0 row.
- History shows the status at scan time with "re-check — recipes change" hint for
  items older than 6 months.

## Overreliance on AI

- Onboarding disclosure requires interaction (D-flow J1).
- Class-inferred hints (S4) always contain "we have not detected anything" verbatim.
- The app never chains scans into an "eat/don't eat" recommendation.
- Periodic (not per-scan) reinforcement: after every 25th scan, a one-time card:
  "Reminder: SnapNutrition can miss allergens. Keep checking printed labels."

## False reassurance (the catastrophic failure)

Defense-in-depth summary (details in SAFETY_MODEL):
1. Language layer: forbidden-strings test, normative copy.
2. Logic layer: asymmetric thresholds, completeness demotion.
3. Schema layer: no `allergen_free` field can exist; statuses require evidence.
4. Review layer: allergen-surface PRs require safety checklist sign-off
   (BUILD_SEQUENCE checkpoints).

## Unnecessary fear from weak inference

The dual failure: S4 class hints ("pad thai often contains peanuts") could scare a
user off safe food or, worse, train them to ignore all warnings.
Rules:
- S4 only for allergens in the class-association table with documented "commonly
  contains" evidence (curated, sourced table — not model-generated).
- S4 capped at 3 hints per scan (most-associated first).
- S4 styling is informational (blue/neutral), spatially separated from S1–S3.
- Copy invites verification rather than avoidance: "ask about ingredients or check
  the label if one exists."

## Beta-tester feedback loop

In-app lightweight "Was this result clear?" (thumbs + optional text) on evidence
screens during beta; responses reviewed against these rules; HUMAN_FACTORS updated
with findings (this doc is living).
