# Feedback Loop

From user interactions to (eventually) better models — designed now, dataset-build
executed R5. Consent (D16) gates everything.

## Signal capture (MVP, live from R1/R3)

- **Confirmations:** user confirmed candidate k (rank, confidence) — implicit
  positive signal, stored always (product function).
- **Corrections:** predicted → corrected class; OCR field fixes — stored always
  (product function). `training_eligible` computed at write time from the user's
  current corrections-consent.
- **Images for training:** only under the separate images-consent; copied at
  dataset-build time (IMAGE_LIFECYCLE §9).
- **UI feedback:** thumbs + text on evidence screens (HUMAN_FACTORS) — product
  research, not training data.

## Annotation & quality review (R5 dataset builds)

1. Consent filter (query-level, not app-level ifs) → eligible corrections+images.
2. **Review queue:** every candidate sample human-reviewed (owner) before dataset
   entry: correct label? image quality? privacy check (no people/bystanders/
   documents in frame — reject otherwise)?
3. Label taxonomy: corrections to Food-101 classes map directly; OOV corrections
   (search-confirmed foods outside 101) accumulate as evidence for vocabulary
   expansion — a *separate* decision (new classes need enough samples + eval
   coverage), never silently added.
4. Accepted samples → `training-staging/` + manifest (scan id, consent version,
   review outcome, reviewer, date) → versioned dataset artifact
   (`feedback-dataset:vN`) with its own data card.

## Poisoning & bias controls

- Per-user contribution cap (≤5% of any feedback dataset) — one adversarial or
  eccentric tester can't steer the model.
- Anomaly screen: users whose corrections disagree wildly with consensus/model on
  clear cases get flagged for review-priority (not auto-excluded).
- Review queue is the primary control (human eyes on every sample at our scale).
- Bias watch: feedback data over-represents our beta demographic and their cuisines;
  data card must state composition; retrained models re-run the full cuisine-bucket
  evaluation (EVALUATION_PLAN) with before/after comparison.
- Class balance: feedback merges into training as a *minority additive* (capped
  fraction per class) — never replaces Food-101 wholesale.

## Active learning (documented, R5+)

Priority sampling for review: low-confidence confirmations, high-confidence
corrections (the scary quadrant), unknown-state scans with search-confirmed labels.
No automated pseudo-labeling — everything through the review queue.

## Retention & revocation

Correction events: with the account. Training copies: manifest-tracked; consent
revocation excludes from all future builds; already-trained models disclosed at
opt-in (J11). Deletion of a scan removes it from future builds (manifest rebuild at
next dataset version).
