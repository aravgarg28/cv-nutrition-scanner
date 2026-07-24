# Personas

Five personas. Priya is primary; when needs conflict, hers win (per D9/D10 the
allergy-management use case defines the safety bar).

---

## 1. Priya — adult with tree-nut and sesame allergies (PRIMARY)

- **Goals:** quickly check packaged foods and restaurant/potluck dishes against her
  allergens; keep a history of products she has vetted.
- **Motivation:** two ER-adjacent scares from hidden ingredients ("tahini" she didn't
  recognize as sesame). Reads every label, but it's slow and stressful.
- **Technical comfort:** high (uses several apps daily).
- **Dietary needs:** tree nuts, sesame; mild suspicion of certain additives.
- **Safety needs:** *the* critical persona. Needs evidence, not verdicts. Will
  over-trust a green checkmark — so the product must never show one for "safe".
  Needs "may contain" and facility warnings surfaced loudly, synonyms explained
  ("tahini → sesame"), and OCR uncertainty flagged.
- **Main workflow:** barcode scan in the grocery store; ingredient-label photo when
  barcode lookup fails; occasionally a meal photo at gatherings (knowing it's weak
  evidence).
- **Trust concerns:** has been burned by apps that said "no allergens found" for
  products with facility warnings. Wants to see the exact label text the app read.
- **Accessibility needs:** none specific; wants one-handed operation in a store aisle.
- **Most important features:** allergen evidence panel with source text, synonym
  explanations, may-contain surfacing, scan history.

## 2. Marcus — vegan tracking macros

- **Goals:** confirm products are vegan (hidden gelatin, casein, whey); rough
  macro/protein estimates for meals.
- **Motivation:** ethics + fitness; tired of googling additives (E-numbers, "lactic
  acid — vegan?").
- **Technical comfort:** high.
- **Dietary needs:** vegan; high-protein preference.
- **Safety needs:** low physical risk; wrong answers cost trust, not health. Still
  wants honest "can't tell" for ambiguous additives (e.g., mono- and diglycerides).
- **Main workflow:** ingredient-label scans; meal photos with serving adjustment;
  assistant questions ("is E471 vegan?").
- **Trust concerns:** knows some additives are ambiguous; respects an app that says so.
- **Accessibility needs:** none specific.
- **Most important features:** vegan rule evaluation with per-ingredient reasoning,
  nutrition per adjusted serving, assistant with cited definitions.

## 3. Dana — parent managing a child's milk allergy

- **Goals:** vet groceries, snacks, and birthday-party food against her son's milk
  allergy; share vetted-product history with her partner (post-MVP).
- **Motivation:** son is 6 (she scans on his behalf — adults-only accounts per D12);
  milk hides behind casein, whey, ghee, "natural flavor" ambiguity.
- **Technical comfort:** moderate.
- **Dietary needs:** child's milk allergy on a managed profile under her account.
- **Safety needs:** high. Needs conservative defaults, prominent "this is not a
  guarantee — check the label yourself" framing, and clear distinction between
  "declared" vs "may contain" vs "we found no milk terms in readable text".
- **Main workflow:** barcode scans while shopping; label photos for imports/bakery
  items without barcodes.
- **Trust concerns:** will abandon the app after one false "no milk terms found" that
  turns out wrong — so OCR-completeness warnings ("we could not read the full label")
  matter enormously to her.
- **Accessibility needs:** larger text option; scans quickly with a child in the cart.
- **Most important features:** managed child profile, may-contain prominence, OCR
  completeness indicator, history of previously vetted products.

## 4. Sam — nutrition-curious generalist (beta tester)

- **Goals:** point at lunch, get calories/macros; curiosity more than discipline.
- **Motivation:** wants awareness without MyFitnessPal-style manual logging.
- **Technical comfort:** moderate.
- **Dietary needs:** none; mild sodium interest.
- **Safety needs:** low; main risk is over-trusting portion estimates — needs the
  "per selected serving, your portion may differ" framing.
- **Main workflow:** single-food meal photos; confirms from top-5; adjusts serving.
- **Trust concerns:** will test the app with weird foods; a graceful "I'm not sure —
  here are guesses + search" keeps him engaged where a wrong confident answer would
  become a screenshot in the group chat.
- **Accessibility needs:** none specific.
- **Most important features:** fast confirm flow, believable serving presets, fun and
  honest low-confidence behavior.

## 5. Rachel — hiring manager / technical reviewer (portfolio persona)

- **Goals:** evaluate the owner's engineering judgment in ≤30 minutes: repo, README,
  live demo, model report.
- **Motivation:** screening candidates for ML/full-stack roles.
- **Technical comfort:** expert.
- **Dietary needs:** n/a.
- **Safety needs:** n/a — but she *evaluates* the safety model; overclaiming
  ("99% accurate allergen detection!") is an instant red flag.
- **Main workflow:** README → live web demo (one scripted scan) → skim code structure,
  tests, experiment report → interview questions.
- **Trust concerns:** wants real measured metrics, honest limitations sections, and
  evidence the candidate understands why top-5 accuracy doesn't make food "safe".
- **Most important features:** web demo requiring no install, README with real
  numbers, model card, visible test suite and CI.
