# User Journeys

Numbered steps are user-visible. `[type]` tags show the information type displayed,
per the typed-information principle. Screens referenced here are specified in
[SCREEN_SPECIFICATIONS](../mobile/SCREEN_SPECIFICATIONS.md).

## J1. First launch & account creation

1. Splash → value proposition carousel (3 cards: scan, evidence, your profile).
2. Card 3 is the **decision-support disclosure**: "SnapNutrition helps you check food —
   it cannot guarantee any food is free of allergens. Always verify labels yourself,
   especially for severe allergies." Requires explicit "I understand" tap (consent
   recorded with timestamp + app version).
3. Sign up: email + password (validation inline). No guest mode (D22).
4. Email verification (free transactional email or verification-link-on-demand; see
   AUTHENTICATION_AND_AUTHORIZATION).
5. Optional training-data opt-in, default OFF: "Help improve the model: allow your
   corrections and photos to be used for training." Separately toggleable for
   corrections-only vs corrections+images (D16).

## J2. Dietary-profile configuration

1. Allergen picker: 9 US majors as cards (milk, egg, fish, crustacean shellfish,
   tree nuts, peanuts, wheat, soy, sesame) + "add custom allergen" free text.
2. Custom allergens get a caution note: synonym coverage for custom terms is
   exact/fuzzy text match only [missing/uncertain framing].
3. Diet rules: vegetarian / vegan / gluten avoidance toggles (D19).
4. Optional managed profile: "scanning for someone else? Add a second profile"
   (e.g., Dana's son) — owned by the account holder (D12).
5. Severity is deliberately NOT collected (we do not modulate warnings by severity;
   everyone gets conservative behavior — see SAFETY_MODEL §severity).
6. Profile editable any time in Settings.

## J3. Camera permission

1. Permission requested on first scan attempt, not at onboarding (higher grant rate,
   clearer context).
2. Pre-permission explainer: "The camera is used only to scan food and labels. Photos
   are uploaded to analyze them and stay in your history until you delete them."
3. Denial → graceful state: upload-from-gallery alternative + link to OS settings.

## J4. Capturing a meal (single-food photo)

1. Home → Scan → mode selector defaults to "Food photo".
2. Live guidance overlay: fill the frame, one food, good light (CAMERA_UX).
3. Capture → client-side quality pre-check (blur/brightness heuristic) [estimated];
   fail → retake suggestion (never a hard block).
4. Upload with progress; processing state with staged status ("checking image…",
   "identifying food…").
5. Candidates screen: top-5 with confidence bars [predicted], framed as "Our best
   guesses". Below threshold → low-confidence banner + search box (D14).
6. User confirms a candidate or searches [user-provided]. **Nothing proceeds without
   confirmation.**

## J5. Reviewing nutrition + adjusting serving

1. After confirmation: nutrition card for the confirmed food from USDA FDC
   [retrieved], labeled "Typical values for *fried rice* — actual dishes vary."
2. Serving selector: USDA portion presets ("1 cup — 198 g") + stepper for multiples
   [user-provided]; values recompute deterministically [estimated: serving math].
3. Source attribution row: "USDA FoodData Central · FDC ID 12345 · SR Legacy"
   [retrieved provenance].
4. Missing nutrient → shown as "—  not available from source" [missing], never 0.

## J6. Scanning a label (ingredient list)

1. Mode "Ingredient label" → overlay: flatten package, fill frame, avoid glare.
2. OCR processing → extracted text shown verbatim in a "What we read" panel
   [observed], with unreadable regions marked "…unreadable…" and an OCR-completeness
   indicator ("We read ~80% of the visible text").
3. Parsed ingredient chips below [estimated: parsed from observed text]; tapping a
   chip shows the source text span.
4. Allergen evidence section (J8).
5. Correction affordance on every OCR field (J7-style inline edit).

## J7. Reviewing low-confidence output & correcting a classification

1. Low-confidence scan → amber banner: "We're not confident. These are guesses."
2. Top-5 shown with small confidence bars; search box prominent.
3. User picks correct food (from list or search) → recorded as correction event
   [user-provided]; if opted-in (D16), queued for the retraining dataset.
4. Post-correction, all downstream data (nutrition, class-inferred allergen hints)
   recomputes from the *user-confirmed* class.
5. OCR corrections: tap any extracted field → edit inline → downstream allergen
   matching re-runs against corrected text; correction event recorded.

## J8. Reviewing allergen evidence

1. Allergen section compares scan evidence against the active profile.
2. Each profile allergen gets a **status row** with evidence type and severity styling
   per [ALLERGEN_POLICY](../safety/ALLERGEN_POLICY.md):
   - "Sesame — **declared**: label says 'Contains: sesame'" [observed]
   - "Tree nuts — **may contain**: 'may contain traces of almonds'" [observed]
   - "Milk — **synonym match**: ingredient 'whey' is derived from milk" [estimated]
   - "Peanuts — **no terms found in readable text** — this is not a guarantee" [missing]
   - "Egg — **insufficient information**: no ingredient list was readable" [missing]
3. Every status row expands to show the exact source text span and data source.
4. Persistent footer on any allergen screen: decision-support reminder.
5. For meal photos (no label): only class-inferred hints are possible — framed as
   "Foods like *pad thai* often contain peanuts. We cannot see ingredients from a
   photo." Never rendered as detection.

## J9. Asking a question (assistant)

1. "Ask about this scan" opens a per-scan thread (D23).
2. Suggested prompts: "Why this allergen warning?", "What's uncertain about this
   scan?", "High in sodium?".
3. Answers are grounded: cite scan fields, USDA record, or RAG documents with visible
   source chips. Unanswerable → explicit "I can't tell from this scan."
4. Safety-boundary questions ("is this safe for me?") → policy response per
   [MEDICAL_BOUNDARIES](../safety/MEDICAL_BOUNDARIES.md): restate evidence, decline
   verdict, recommend label verification / professional advice.
5. LLM quota exhausted → notice + deterministic scan summary instead (D20).

## J10. Scan history

1. History tab: chronological scans with thumbnail, confirmed food/product, date,
   allergen-status glyphs.
2. Tapping reopens the full result incl. evidence and conversation thread.
3. Per-scan delete (image + derived data + thread) with undo snackbar (soft-delete
   window, then hard delete per IMAGE_LIFECYCLE).

## J11. Exporting or deleting data

1. Settings → Privacy: "Export my data" → async job → downloadable JSON archive
   (profile, scans, corrections, conversations, consent records; images as signed
   URLs valid 24 h).
2. "Delete my account" → confirmation with typed phrase → hard delete of account,
   images, embeddings, threads; training-opt-in data already contributed is removed
   from future dataset builds (documented limitation: models already trained are not
   retroactively unlearned — disclosed at opt-in).
3. Both actions audited (AUDIT events per DATA_MODEL).

## J12. Barcode scan

1. Mode "Barcode" → live detection via device camera (no photo upload needed).
2. Open Food Facts lookup [retrieved] → product name, brand, ingredients, allergen
   tags, nutrition; provenance row "Open Food Facts · last updated <date>".
3. OFF data completeness varies → missing fields rendered as missing, and stale
   "last updated" dates > 2 years flagged: "This product data is old — check the
   physical label."
4. Not found → offer ingredient-label scan as fallback.
