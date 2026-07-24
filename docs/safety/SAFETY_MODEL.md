# Safety Model

Binding on all implementation. Companion docs: [ALLERGEN_POLICY](ALLERGEN_POLICY.md)
(exact statuses + language), [MEDICAL_BOUNDARIES](MEDICAL_BOUNDARIES.md),
[HUMAN_FACTORS](HUMAN_FACTORS.md).

## Intended use

Decision support for adults checking food against their own dietary profile:
a fast, evidence-showing second look at labels, products, and (weakly) food photos.
The user remains the decision-maker; the physical label and professional advice
remain authoritative.

## Prohibited use (product must not enable or imply)

- Declaring any food "safe", "allergen-free", or "OK for you".
- Anaphylaxis/emergency guidance beyond directing to emergency services.
- Medical diagnosis, treatment, or dosage advice.
- Claiming ingredient knowledge of unlabeled food from a photo.
- Certifying halal/kosher/organic or any regulated claim.
- Use as sole verification for severe allergies (stated at onboarding, on every
  allergen result, and in the assistant's boundaries).

## User warnings (where and when)

| Warning | Placement | Frequency |
|---|---|---|
| Decision-support disclosure | Onboarding (blocking consent) | Once, re-shown on major version change |
| "Not a guarantee — verify the label" | Footer of every allergen-evidence view | Always |
| "Photos can't reveal ingredients" | Any class-inferred allergen hint | Always |
| "We couldn't read the whole label" | OCR results below completeness threshold | Conditional |
| "This data may be outdated" | OFF records older than 24 months | Conditional |
| "Experimental estimate" | Any R4 experimental output | Always |

## Severity levels (display taxonomy)

We deliberately do **not** collect user allergy severity (D10 conservative-for-all).
Severity here grades *evidence*, not medical risk:

- **S1 — Declared conflict** (label says "Contains: X" matching profile): strongest
  visual treatment (see HUMAN_FACTORS for color/wording rules).
- **S2 — Trace/facility conflict** ("may contain", facility statements): strong
  treatment, one step below S1, never collapsed or hidden.
- **S3 — Derived/synonym match** (ingredient implies allergen): strong treatment with
  explanation of the derivation.
- **S4 — Inferred possibility** (class-inferred hint; unverifiable): informational
  caution styling; explicitly not a detection.
- **S5 — Unknown** (insufficient/unreadable information): neutral caution; must never
  resemble an all-clear.
- **S0 — No terms found in readable text**: neutral (not green/success) styling with
  mandatory limitation text.

## Confidence thresholds

Initial values; final values set by calibration experiments (EXPERIMENT_PLAN E11–E13)
and recorded in the model card. All thresholds are config, not code constants.

- Classification τ_confident (calibrated top-1 ≥ τ): normal candidate framing.
  Placeholder τ=0.55 `[TO BE SET BY CALIBRATION]`.
- τ_unknown (top-1 < τ_u or OOD score high): "not sure" state, guesses framing, search
  prominent. Placeholder τ_u=0.20 `[TO BE SET]`.
- OCR token confidence < τ_ocr → token rendered with uncertainty mark and excluded
  from *negative* claims (it can still trigger positive allergen matches — asymmetric
  by design: uncertain text can raise warnings, never lower them).
- OCR completeness < 70% → completeness warning; negative statements ("no terms
  found") automatically demoted to "insufficient information".

## The asymmetry principle

False reassurance is the catastrophic failure; false alarm is the tolerable one.
Every threshold, parser, and fallback errs toward warnings:
- Uncertain OCR text counts FOR matches, not FOR absence.
- Unparseable ingredient segments make the scan "insufficient info", not "clean".
- Matcher ties break toward the match.
- Missing OFF allergen tags ≠ empty allergen list (missing → unknown).

## Escalation & failure behavior (required responses)

| Situation | Required behavior |
|---|---|
| Blurry image | Quality score → retake guidance; if processed anyway, results carry quality caveat |
| Label partially visible / incomplete | Completeness indicator; negative claims demoted to S5 |
| Low OCR confidence | Uncertain tokens marked; asymmetry rule applies |
| Unknown food class | "Not sure" state + guesses + search; no nutrition until user picks |
| Several plausible classes | Top-5 shown as alternatives; wording "could be one of…" |
| Packaged product, no visible ingredient list | S5 for all profile allergens + prompt to photograph the ingredient panel or scan barcode |
| Severe allergen can't be ruled out | S5 status; assistant restates evidence gap; never reassures |
| "May contain" present | S2, top-of-list placement, cannot be dismissed or collapsed |
| User asks "is this safe?" | MEDICAL_BOUNDARIES script: evidence summary + decline verdict + verify-label guidance |
| Nutrition value undeterminable | "— not available from source"; never 0, never interpolated silently |
| Sources conflict (e.g., OCR vs OFF) | Both shown with provenance; conflict banner; no silent merge |
| External data source down | Explicit degraded state; cached data used with "cached <date>" tag; no fabrication |
| Model service down | Scan queued or failed visibly; no stale prediction reuse across images |

## Human confirmation requirements

- Food identity: always user-confirmed before nutrition attaches (J4).
- OCR-derived nutrition-panel values: user reviews before saving to history.
- Corrections always available post-hoc; downstream results recompute.

## Evidence requirements

Any allergen/diet status must reference: evidence type (per ALLERGEN_POLICY), source
text span or data-source record ID, and matcher rule ID. A status without stored
evidence is a bug (enforced by schema: evidence fields non-nullable).

## High-risk user flows (extra review + tests)

1. Label scan → allergen evidence (Priya flow) — full fixture catalog, human-factors
   review, release-blocking.
2. Barcode → OFF allergen tags — staleness and missing-tag handling.
3. Assistant answering allergen questions — injection + reassurance suites.
4. Profile edit → re-evaluation of previously viewed scans (no stale reassurance).
5. Meal photo → class-inferred hints — framing tests (must never read as detection).
