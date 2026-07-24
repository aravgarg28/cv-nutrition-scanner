# Demo Data

Reproducible assets for DEMO_SCENARIOS; seeded by `scripts/seed_demo.py`
(idempotent reset).

## Demo profiles

- `demo@snapnutrition.app` — role `demo` (server-side read-mostly: can create scans
  against fixture images, cannot modify consents/delete account). Profile: tree
  nuts + sesame; vegan rule ON. Managed sub-profile "Alex" (milk) for scene 4's
  synonym demo.
- Reset script restores: profiles, 6 seeded historical scans (for scene 8),
  assistant thread on one scan, consents (training opt-in OFF — demonstrates
  default).

## Fixture images (self-captured, rights-clean, committed via LFS or generated)

| ID | Asset | Scene |
|---|---|---|
| demo-food-01 | distinctive dish photo (clear class) | 1 |
| demo-food-02 | confusion-pair dessert photo | 2, 6 |
| demo-food-03 | non-Food-101 regional dish | (backup unknown-state) |
| demo-label-01 | granola-bar-style label: "Contains: almonds", "may contain sesame", whey in list — **synthetic label render** (no real brand in public demo) | 3, 4, 7 |
| demo-label-02 | partial/torn label render, completeness ~55% | 5 |
| demo-panel-01 | clean Nutrition Facts render | (panel demo) |
| demo-barcode-01 | fixture barcode mapping to a **seeded OFF cache row** (no live OFF call) | 11/E2E |

Synthetic renders come from the OCR fixture generator (OCR_TEST_STRATEGY) — brandless,
license-free, and deliberately designed to exercise each status.

## No-live-dependency rule

Demo path never calls FDC/OFF live: all referenced records pre-seeded in the cache
tables with `fetched_at` stamps (staleness demo uses an old stamp). Assistant scenes:
live LLM when available; the deterministic fallback is itself demo-able (scene 12
E2E) — if quota hits mid-demo, the fallback *is* the talking point, not a failure.

## Web demo

Same demo account behind the web page: pre-loaded fixture gallery (visitors pick a
fixture rather than uploading, keeping the public surface abuse-resistant; an
upload-your-own toggle can be enabled for supervised sessions). Rate-limited per
AUTHENTICATION §web demo.
