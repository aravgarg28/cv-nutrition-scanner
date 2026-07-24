# Nutrition Data Strategy

## Source evaluation

| Source | Coverage | Accuracy | License | Rate limits | Latency | Geographic | Branded vs generic | Updates | Reliability |
|---|---|---|---|---|---|---|---|---|---|
| **USDA FoodData Central (FDC)** | ~400k foods: Foundation, SR Legacy, FNDDS (survey), Branded | Authoritative for generic/foundation; branded is manufacturer-submitted | **Public domain (US gov)** — ideal for D24 | Free API key, 1,000 req/hr default | ~200–800 ms API | US | Both (branded subset large but stale-ish) | Periodic releases | High |
| **Open Food Facts (OFF)** | ~3M products worldwide, barcode-keyed | Crowdsourced: variable, often good for mainstream US products; allergen tags curated from labels | **ODbL** (database) — share-alike obligations for derived DBs; attribution required. Compatible with our use; document obligations | Polite-use (no hard key), bulk dumps available | ~300–1500 ms | Global, US decent | Branded (its purpose) | Continuous | Medium (varies per product; `last_modified` exposed) |
| UPC/barcode commercial DBs (Nutritionix, Edamam…) | Large | Good | **Paid** tiers | — | — | — | — | — | Rejected (D0) |
| Manufacturer sites | Exact | Authoritative | Scraping/ToS issues | — | — | — | — | — | Rejected as pipeline; users can verify manually |
| Curated internal mappings | 101 rows | We control | Ours | — | 0 (local) | — | Generic | With model releases | The class→FDC bridge (below) |

## Source roles & precedence

1. **Barcode scan → OFF** (product identity + label-derived tags + nutrition), with
   provenance + `last_modified` surfaced; stale >24 mo flagged (J12).
2. **Photo scan → confirmed class → curated class→FDC mapping → FDC record**
   ("typical values" framing — a class, not a specific dish).
3. **Nutrition-panel scan → OCR values** (user-confirmed) — *observed* data,
   highest-precedence for that specific product, still displayed with "as read from
   label".
4. **Manual search → FDC search API** (Foundation/SR Legacy preferred over Branded in
   ranking; data-type shown).

**Conflict rule (SAFETY_MODEL):** when two sources disagree (e.g., OCR panel vs OFF
record), show both with provenance; user-confirmed OCR wins for display default;
never silently merge.

## Class→FDC mapping (the curated bridge)

101 curated rows: Food-101 class → FDC ID (FNDDS survey foods preferred — they
represent "as consumed" mixed dishes, e.g., `pad_thai` → FNDDS "Pad Thai") + default
portion set. Hand-reviewed once (R0/R1 task with review checklist: plausible kcal,
sensible portion presets), versioned in the repo, provenance noted per row.
Explicitly documented: a class maps to *typical* nutrition — "your restaurant's
carbonara differs" framing is mandatory (FOOD_NORMALIZATION).

## Caching & rate-limit strategy

- Postgres cache table for FDC + OFF responses: key = (source, source_id), full JSON
  payload + fetched_at + source_version. TTL: FDC 90 days (data changes rarely), OFF
  30 days; stale-while-revalidate refresh in background jobs.
- All 101 mapped FDC records **pre-fetched and seeded** at deploy — the primary photo
  path never blocks on USDA at runtime (also the <100 ms cached-lookup budget,
  PERFORMANCE_BUDGET).
- OFF bulk: no full-dump import in MVP (multi-GB); per-barcode fetch + cache.
  Rate-limit courtesy: identify via User-Agent per OFF guidelines.
- Demo mode uses cache-only fixtures (DEMO_DATA) — no live external calls during
  demos.

## Fallback order

Barcode: OFF → (miss) → prompt label scan. Photo: mapping → FDC cache → (cold) FDC
API → (down) cached-only with "live source unavailable" notice. Search: FDC API →
(down) cached popular-foods subset with notice. Fabrication is never a fallback.

## ODbL note (OFF)

Caching OFF rows for serving is fine with attribution ("Data from Open Food Facts,
ODbL"). If we ever ship a *derived database* (e.g., bundled offline product DB in
R5), share-alike applies to that derivative — flagged as a future licensing decision.
Attribution string ships in the UI source rows now.
