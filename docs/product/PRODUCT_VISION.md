# Product Vision

## Product statement

**SnapNutrition** (working name) is a mobile app that lets a person photograph food —
a meal, a packaged product's ingredient label, a nutrition-facts panel, or a barcode —
and get back structured, honestly-uncertain information: what the food probably is,
what it likely contains, which of *their* allergens and dietary rules it may conflict
with, and what its nutrition looks like per serving — with every claim typed by where
it came from and how confident the system is.

## Core user problem

Reading ingredient labels is slow, error-prone, and stressful — especially for people
managing allergens or dietary rules. Synonyms hide allergens ("casein" = milk,
"albumin" = egg), "may contain" statements are easy to miss, and unpackaged food gives
no label at all. Existing calorie apps either demand tedious manual entry or give
overconfident single answers with no evidence.

## Primary user

An adult managing one or more food allergens, intolerances, or dietary rules
(vegetarian/vegan/gluten avoidance) who wants a fast second pair of eyes on food and
labels — and understands (because the app repeatedly tells them) that it is decision
support, not a guarantee.

## Secondary users

- General nutrition-curious users who want photo-based nutrition estimates.
- Parents checking products against a child's allergen profile (under their own account).
- Friends/family beta testers; recruiters and hiring managers via the web demo.

## Value proposition

- **Seconds, not minutes**: point camera → structured answer.
- **Evidence, not verdicts**: every allergen status shows *why* (the exact label text,
  the matched synonym, the data source) and *what kind* of claim it is.
- **Your profile**: results are compared against the user's own allergens and diet rules.
- **One app, four inputs**: meal photo, ingredient label, nutrition panel, barcode.

## Differentiation

Versus calorie counters (MyFitnessPal-class): camera-first, allergen-evidence-first,
and honest about uncertainty rather than presenting one confident number.
Versus barcode apps (Yuka-class): also handles unpackaged food and raw label photos,
and explains its reasoning with typed evidence.
As a portfolio piece: end-to-end ML system (fine-tuned CV model, OCR pipeline,
RAG-grounded assistant, MLOps loop) with a documented safety model — not a demo notebook.

## Product principles

1. **Typed information.** Every displayed fact is one of: observed (OCR/barcode read),
   retrieved (USDA/OFF record), predicted (model output), user-provided, estimated
   (derived with assumptions), missing/uncertain, or safety warning. The UI never
   blends these into one undifferentiated answer.
2. **Confirmation over automation.** The user confirms the food identity before
   nutrition is attached to it. The app never auto-commits a prediction.
3. **Deterministic math.** Serving arithmetic, unit conversion, and %DV come from code,
   never from a language model.
4. **Evidence or silence.** If the app can't support a claim, it says "insufficient
   information" instead of guessing.
5. **The user owns their data.** Opt-in for any training use; export and delete always
   available.

## Safety principles (expanded in docs/safety/)

- Never declare food "safe" or "allergen-free". The strongest positive statement is
  "no [allergen] terms found in the text we could read", always paired with its limits.
- Allergen statuses are evidence-typed (declared / may-contain / facility / synonym /
  class-inferred / not-found-in-visible-text / insufficient info / OCR-uncertain).
- Low confidence is surfaced, never hidden; below-threshold predictions are framed as
  guesses and accompanied by manual search.
- The app is decision support. Severe-allergy users are told, at onboarding and at
  every allergen result, not to rely on it alone.

## Privacy principles (expanded in docs/security/PRIVACY_MODEL.md)

- Allergen and dietary profiles are health-adjacent data: encrypted in transit and at
  rest, never in logs, never in LLM prompts beyond the minimum needed for the current
  question.
- Images belong to the user: kept until they delete them, never used for training
  without explicit opt-in, EXIF (incl. GPS) stripped at ingestion.
- No third-party analytics SDKs in the beta.

## Success metrics

Portfolio: repo quality a hiring manager praises; live demo a recruiter can run in
<2 minutes; measured (not invented) model metrics with calibration analysis.
Product (beta): ≥10 real testers complete ≥3 scans each; user-correction rate on
top-1 predictions tracked and reported honestly; zero incidents of the app rendering
a "safe" verdict; task success — a tester can answer "does this product list any of
my allergens?" from a label photo in under 30 seconds.

## Non-goals (current scope)

- Medical or diagnostic claims of any kind; anaphylaxis risk assessment.
- Fitness coaching, daily-intake tracking, weight-loss programs (future product
  direction, out of scope now — see D9).
- Halal/kosher certification verdicts (post-MVP, non-verdict framing only).
- Automated portion/volume estimation from a single image (research track only).
- Multi-food plate decomposition in MVP (Release 4 experiment).
- Non-US labels and allergen regimes (post-MVP).
- Monetization during beta.
