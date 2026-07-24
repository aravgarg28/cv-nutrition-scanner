# Allergen Policy

Defines the closed set of allergen statuses, their exact user-facing language, and
rendering rules. **The strings below are normative**: implementation uses them
verbatim (via a localization table keyed by status code), and tests assert them.
Changing any string requires a safety review entry in this file's changelog.

## Status taxonomy

Statuses are per (scan × profile-allergen). Codes are stable API values.

### `DECLARED` — Declared allergen (severity S1)
Trigger: an explicit allergen declaration ("Contains: …") or an ingredient that IS the
allergen (e.g., "peanuts") in OCR text or OFF `allergens` tags matching a profile
allergen.
> **Sesame declared on label**
> The label we read says: "Contains: sesame."
> _Source: label text you scanned · [view text]_

### `MAY_CONTAIN` — Cross-contamination warning (S2)
Trigger: "may contain…", "may contain traces of…", or OFF `traces` tags.
> **May contain tree nuts**
> The label we read says: "May contain traces of almonds." This is a
> cross-contamination warning from the manufacturer.
> _Source: label text you scanned · [view text]_

### `FACILITY` — Shared-facility/equipment warning (S2)
Trigger: "processed in a facility that also processes…", "made on shared equipment
with…".
> **Made in a facility that handles peanuts**
> The label we read says: "Processed in a facility that also processes peanuts."
> _Source: label text you scanned · [view text]_

### `SYNONYM` — Ingredient derived from allergen (S3)
Trigger: ontology synonym/derivative match (whey→milk, tahini→sesame, albumin→egg…).
> **Contains a milk-derived ingredient**
> The ingredient "whey" is derived from milk.
> _Matched by: ingredient dictionary · Source: label text you scanned · [view text]_

### `POSSIBLE_SYNONYM` — Uncertain synonym match (S3, uncertain variant)
Trigger: fuzzy match over OCR-uncertain token, or ambiguous term (e.g., "natural
flavor" flagged only for milk per FDA ambiguity list).
> **Possible egg-derived ingredient — uncertain**
> We read "albumen" with low confidence, which may refer to egg. Please check the
> printed label.
> _Matched by: ingredient dictionary (uncertain text) · [view text]_

### `CLASS_RISK` — Inferred from predicted/confirmed food class (S4)
Trigger: class→allergen-association table for photo scans without label text.
> **Peanuts are common in this kind of food**
> Dishes like pad thai often contain peanuts. A photo cannot show actual
> ingredients — we have not detected anything.
> _Based on: typical recipes for the food you confirmed_

### `NOT_FOUND` — No terms found in readable text (S0)
Trigger: label scan with completeness ≥ threshold and zero matches for this allergen.
> **No milk terms found in the text we could read**
> We did not find milk or milk-derived ingredients in the label text we were able to
> read. **This is not a guarantee.** Text we couldn't read, printing errors, or
> cross-contamination are still possible. Always check the printed label.
> _Source: label text you scanned (≈{completeness}% readable) · [view text]_

Rendering: neutral styling. NEVER green, NEVER a checkmark, NEVER the words "safe",
"free", "clear", or "no allergens".

### `INSUFFICIENT` — Insufficient information (S5)
Trigger: no ingredient text readable; OFF record missing ingredient data; photo-only
scan for a labeled-product question; completeness below threshold (demotion rule).
> **Not enough information about soy**
> We couldn't read enough of this label to check for soy. Try scanning the
> ingredient list directly, or check the printed label.

### `OCR_UNCERTAIN` — Text too unreliable (S5 variant)
Trigger: matches exist only in tokens below OCR confidence floor AND completeness low.
> **We couldn't read this label reliably**
> The photo was too {blurry/dark/small} to trust our reading. Please retake the
> photo or check the printed label.

### `USER_CONFIRM_REQUIRED` — Pending human confirmation
Trigger: scan states where identity/OCR review is still pending.
> **Confirm the food first**
> Allergen checks run after you confirm what this food is.

## Source attribution rule for product-database evidence

Statuses derived from Open Food Facts tags (barcode path) must attribute to the
database, never to "the label" — OFF is crowdsourced and may lag or err
(ADVERSARIAL_REVIEW 6.1). Template variant:

> **Sesame listed for this product**
> The Open Food Facts database lists sesame for this product. Database entries can
> be outdated — check the printed label.
> _Source: Open Food Facts · last updated {date}_

The same rule applies to `MAY_CONTAIN` from OFF `traces` tags and to `NOT_FOUND`
derived from OFF data (which additionally requires the product's ingredient data to
be marked complete in OFF; otherwise `INSUFFICIENT`).

## Ordering & prominence rules

1. Sort: S1 → S2 → S3 → S4 → S5 → S0. Positive findings always above negatives.
2. S1–S3 rows are expanded by default; may not be collapsed, dismissed, or hidden by
   filters.
3. S2 (`MAY_CONTAIN`/`FACILITY`) must be visually distinct from S1 but of comparable
   prominence — beta users historically under-read trace warnings (HUMAN_FACTORS).
4. The footer on every allergen view (verbatim):
   > SnapNutrition is decision support, not a guarantee. It can miss allergens.
   > Always verify the printed label — especially for severe allergies.
5. Non-profile allergens detected (e.g., label declares milk, user has no milk
   allergy) are listed in a collapsed "Other allergens declared" section — informative,
   not alarming.

## Forbidden renderings (test-enforced)

- The strings "safe", "allergen-free", "no allergens", "all clear", "you're good"
  in any allergen-related UI or assistant output.
- Green/success styling or checkmark iconography on `NOT_FOUND`.
- Collapsing S1–S3 by default.
- Displaying `NOT_FOUND` when completeness < threshold (must demote to
  `INSUFFICIENT`).
- Any status row lacking a source reference.

## "Not detected" ≠ "allergen-free" (normative interpretation)

`NOT_FOUND` is a statement about *our reading of visible text*, never about the food.
All copy, assistant behavior, API field names (`terms_found_in_readable_text: false`,
NOT `allergen_free`), and documentation must preserve this distinction.

## Changelog

- v1.0 (2026-07-12): initial policy from planning session.
- v1.1 (2026-07-12): added product-database source-attribution rule
  (ADVERSARIAL_REVIEW finding 6.1).
