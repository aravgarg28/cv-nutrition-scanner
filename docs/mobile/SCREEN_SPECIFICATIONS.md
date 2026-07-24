# Screen Specifications

15 screens. Every screen defines: purpose, components, actions, and the five states
(empty / loading / error / low-confidence where applicable / success). Accessibility
per HUMAN_FACTORS applies globally (dynamic type, labels, targets); noted only where
screen-specific. Responsive: phones portrait-first; tablets get centered max-width
columns; no landscape lock except camera.

## 1. Onboarding
- **Purpose:** value prop + decision-support disclosure + account entry.
- **Components:** 3-card carousel (card 3 = disclosure with required "I understand"),
  sign-up/log-in buttons.
- **Actions:** advance, acknowledge disclosure (recorded), continue to auth.
- **States:** n/a offline-tolerant (static); disclosure ack failure → retry banner.
- **A11y:** carousel navigable by buttons, not swipe-only.

## 2. Auth (sign up / log in / reset)
- **Purpose:** account access. **Components:** email/password fields (inline
  validation), verify-email notice, reset flow.
- **Error states:** invalid credentials (no user-enumeration wording: "email or
  password is incorrect"), lockout (423) with countdown, offline.

## 3. Dietary profile setup/edit
- **Purpose:** allergens + rules (J2). **Components:** 9 allergen cards, custom-
  allergen input (+ caution note), diet-rule toggles, managed-profile section.
- **States:** empty (nothing selected — allowed, warn "no allergens configured — scan
  results won't check for you"), saving spinner, save-failure retry.
- **Safety:** custom-allergen caution copy is normative (J2).

## 4. Home
- **Purpose:** entry hub. **Components:** big Scan button, recent scans (3),
  active-profile chip (switcher), waking-backend banner slot.
- **Empty:** first-use illustration + "make your first scan". **Loading:** skeleton
  rows. **Error:** cached recents + offline chip.

## 5. Camera & scan-mode selection
- **Purpose:** capture per mode. **Components:** mode tabs (Food photo / Ingredient
  label / Nutrition panel / Barcode), mode-specific overlay guides (CAMERA_UX),
  shutter, gallery picker, torch toggle; barcode mode = live detection reticle.
- **Actions:** capture, pick, switch mode, torch.
- **Error states:** permission denied → explainer + gallery + settings link; barcode
  undetected >8 s → hint + "type barcode" fallback.
- **A11y:** shutter labeled; barcode detection announces via screen reader.

## 6. Image preview & quality guidance
- **Purpose:** pre-upload check. **Components:** preview, client quality verdict
  chips (blur/dark), Retake / Use photo.
- **Low-quality state:** amber chip + copy "this may reduce accuracy" — never blocks.

## 7. Processing
- **Purpose:** pipeline feedback. **Components:** staged progress ("checking image…",
  "identifying food…" / "reading label…"), cancel.
- **Error:** stage-failure card with retry (re-enqueue) or new photo; timeout copy.
- **Waking state:** free-host cold start message ("waking up the scanner — ~30 s").

## 8. Food candidates (photo mode)
- **Purpose:** confirmation gate (J4). **Components:** top-5 list (name, ConfidenceBar,
  thumbnail), search box, "none of these" → search focus.
- **Low-confidence state:** amber banner "We're not confident. These are guesses." +
  search promoted above candidates (D14).
- **Unknown state:** "We couldn't identify this" + search + retake tips.
- **Action:** tap candidate → confirm (single tap + undo snackbar, no modal).

## 9. Nutrition result
- **Purpose:** typical values for confirmed food (J5). **Components:** framing line
  ("Typical values for X — dishes vary"), D17 nutrient rows (value + unit + missing
  "—"), serving selector summary, SourceChip (USDA/FDC id), allergen-hints section
  (S4, separated), Ask-assistant button.
- **Missing-data state:** rows show "not available from source".
- **Error:** nutrition fetch failed → retry; never fabricated values.

## 10. Allergen evidence
- **Purpose:** THE safety screen (J8). **Components:** StatusRow list (ALLERGEN_POLICY
  order), expandable evidence with source span highlight, "Other allergens declared"
  (collapsed), completeness indicator (label scans), decision-support footer
  (persistent), profile chip.
- **States:** insufficient-info rows for missing data; profile-unavailable state
  ("can't check — profile failed to load", never empty-and-silent).
- **A11y:** StatusRow composed sentences (HUMAN_FACTORS).

## 11. OCR review & correction ("What we read")
- **Purpose:** verbatim transparency + fixes (J6/J7). **Components:** verbatim text
  panel (unreadable marks), completeness bar, parsed chips (tap → source span),
  editable fields, re-run notice after edit.
- **States:** OCR failed → retake/retry; partial → completeness warning.

## 12. Serving adjustment
- **Purpose:** portion input (J5). **Components:** preset list ("1 cup — 198 g"),
  stepper (0.25×), custom grams input, live-recompute values, "per selected serving —
  your portion may differ" line.

## 13. Assistant (per-scan thread)
- **Purpose:** grounded Q&A (J9). **Components:** thread, suggested prompts, input
  (2k cap), citation chips on answers, degraded-mode banner + deterministic summary
  card.
- **States:** empty (suggestions), streaming/loading, quota-degraded, error retry.
- **Safety:** boundary responses render like normal messages (no scary styling).

## 14. Scan history
- **Purpose:** J10. **Components:** reverse-chron list (thumb, name, date, status
  glyphs), filters (mode/date), item swipe-delete (undo snackbar), "re-check —
  recipes change" hint on old items.
- **Empty:** "No scans yet" + Scan CTA. **Loading:** skeletons. **Error:** cached
  list + offline chip.

## 15. Settings & privacy
- **Purpose:** account, consents, data rights (J11). **Components:** profile edit
  links, training-data consent toggles (with current status + version), export
  button (job status inline), delete account (typed confirmation + fresh reauth),
  about/licenses (OFF/USDA attribution), sign out.
- **States:** export job running/ready (download link)/failed; deletion pending
  state locks the app pending completion.
