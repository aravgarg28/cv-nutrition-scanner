# Performance Budget

Budgets are targets on the **free-tier serving hardware** (2 vCPU class), warm
service, measured per BENCHMARK_PLAN. They gate releases as regressions (a PR that
doubles OCR latency needs a reason), not as absolute SLAs — free-tier hardware
variance is documented honestly.

## The "<100 ms" clarification (from the résumé target)

Any "<100 ms nutrition retrieval" claim refers **only** to: cached structured
nutrition lookup (Postgres hit for an already-mapped food) measured server-side.
It never describes the end-to-end scan (upload + inference + parsing), which is a
multi-second pipeline. Résumé bullets must say "cached lookup" explicitly
(RESUME_BULLETS).

## Budgets

| Operation | Measure | Target (p50 / p95) |
|---|---|---|
| Camera preview ready | tap scan tab → live preview | 400 ms / 1 s (device-dependent; measured on mid-tier Android) |
| Client image preprocess (downscale/encode) | on-device | 300 ms / 800 ms |
| Upload (≤500 KB, decent 4G) | presign + PUT + complete | 1.5 s / 4 s |
| Server image validation + re-encode | job | 300 ms / 800 ms |
| Classification (ONNX CPU, incl. preprocess) | job stage | 800 ms / 2 s |
| OCR pipeline (label image) | job stage | 3 s / 6 s |
| Ingredient parse + allergen evidence | job stage | 100 ms / 300 ms |
| Nutrition lookup — cached/mapped | request | **40 ms / 100 ms** |
| Nutrition lookup — cold FDC | request | 800 ms / 2.5 s |
| Barcode → OFF cached | request | 60 ms / 150 ms |
| Barcode → OFF cold | request | 900 ms / 3 s |
| Serving recompute | request (sync) | 30 ms / 80 ms |
| **End-to-end photo scan** (capture→candidates) | user-perceived | 4 s / 9 s |
| **End-to-end label scan** (capture→evidence) | user-perceived | 6 s / 12 s |
| Assistant first token / full answer | request | 1.5 s / — · 6 s / 12 s |
| History list (50 items) | request | 150 ms / 400 ms |
| Cold start (Space wake) | first request after sleep | 30–60 s — outside budget, mitigated by keep-warm + waking UI (not hidden) |

## Mobile budgets

App cold launch → Home interactive: 2 s / 4 s (mid-tier Android). Memory: < 400 MB
during capture+upload. Jank: scan-results screens maintain 60 fps scroll (no heavy
work on JS thread during render; evidence text virtualization if needed).

## Backend resource budgets

Steady RSS < 3 GB (models loaded, 16 GB host); job concurrency sized so one OCR +
one classify can co-run without p95 blowout (measured, then pinned in config).
