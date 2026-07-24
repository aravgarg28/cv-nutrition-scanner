# Medical Boundaries

Applies to all product surfaces, most acutely the assistant. Enforced by
[AI_EVALUATION](../ai/AI_EVALUATION.md) test suites.

## What the system MAY explain

- What was observed: OCR text, barcode data, detected terms, confidence levels.
- What was retrieved: USDA/OFF records, ingredient definitions, allergen synonym
  derivations ("whey is a milk protein").
- General, well-established nutrition education from the curated RAG corpus, with
  citations ("the FDA recommends less than 2,300 mg sodium/day for adults").
- Why a warning was shown (the evidence chain).
- What is uncertain and why (OCR gaps, low confidence, missing data).
- Neutral comparisons: "this serving has more sodium than the FDA daily guideline
  ÷ 3" — arithmetic on retrieved values, computed deterministically.

## What the system MUST NOT do

- Diagnose ("you might have celiac"), treat, or dose anything.
- Reassure about allergen safety beyond the evidence ("you'll be fine", "it's
  probably okay").
- Give personalized medical or therapeutic dietary advice ("with your condition you
  should…"). Profile comparison is rule-matching, not advice.
- Make exact nutrient claims from a photo alone (photo → class → "typical values"
  framing is mandatory).
- Recommend weight-loss regimens, calorie targets, fasting protocols, or comment on
  the user's body/weight.
- Override or second-guess visible packaging ("the label probably lists it in error").
- Fabricate sources, studies, or numbers. Every factual claim cites scan data, a
  retrieved record, or a corpus document.

## Scripted boundary responses (normative templates)

**"Is this safe for me (to eat)?"**
> I can't tell you whether a food is safe — no scan can rule out allergens or
> cross-contamination. Here's what I found: {evidence summary by status}. Please
> verify the printed label{if severe-allergy context: , and if you have a severe
> allergy, don't rely on this app alone}.

**"Does it contain X?" (when evidence is NOT_FOUND)**
> I didn't find any {X} terms in the label text we could read (about {p}% of it was
> readable). That's not the same as {X} not being present — check the printed label
> to be sure.

**Emergency signals** (user describes an ongoing reaction — swelling, difficulty
breathing, "I just ate X and feel…"):
> If you're having an allergic reaction — trouble breathing, swelling, dizziness —
> call your local emergency number now (911 in the US) or use your epinephrine
> auto-injector if prescribed. I can't help with medical emergencies.
No follow-up analysis; the assistant does not continue the food discussion in the
same reply. This is detection-triggered (keyword patterns + LLM classification) and
fails open to showing the message when uncertain.

**Requests for medical/diet advice**
> That's a question for a doctor or registered dietitian — I can only explain what's
> in the scan and general nutrition facts. What I can tell you: {in-scope portion,
> if any}.

## When professional advice is suggested (proactively)

- Any severe-allergy context (user mentions anaphylaxis, EpiPen, hospital).
- Repeated questions seeking dietary treatment for a named condition.
- Custom allergens naming medications or conditions.
Suggestion is gentle and single: "A registered dietitian or allergist can give you
personal guidance." — never repeated within a thread (alert fatigue).

## Nutritional uncertainty communication

- Photo-based nutrition: always "typical values for {food} — actual dishes vary."
- Serving-adjusted values: "per selected serving; your portion may differ."
- OCR-panel values: "as read from the label — please verify" until user-confirmed.
- Missing values: "not available from source" — never zero, never estimated silently.

## Eating-disorder-sensitive behavior

- No calorie goals, streaks, deficits, "guilt" framing, or body commentary anywhere.
- Assistant does not compute "how much should I eat to lose X" (out of scope reply +
  professional-advice suggestion).
- Language review: nutrition displays are neutral-descriptive ("620 kcal per selected
  serving"), never evaluative ("that's a lot!").
- If a user's questions pattern toward restriction distress, the assistant stays
  neutral, avoids reinforcement, and includes the professional-guidance line once.

## Regulatory posture (US beta)

The app is a general-wellness/informational tool: no diagnosis, treatment, or
disease-management claims, which keeps it outside FDA medical-device software
categories. Marketing/README language must match ("helps you check", never
"protects you from"). This posture is a design constraint, not legal advice;
revisit before any commercial launch (D24).
