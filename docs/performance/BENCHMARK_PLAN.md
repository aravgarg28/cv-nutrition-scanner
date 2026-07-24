# Benchmark Plan

All published numbers come from these procedures; anything else is a placeholder.
Reports: `docs/ml/reports/bench-<date>.md` (environment, versions, raw distributions).

## Principles

Warmup before measurement (≥20 iterations inference; ≥5 requests API); report
p50/p95 (p99 only where n ≥ 1000); fixed inputs (versioned benchmark fixture set:
20 photos, 10 labels, 5 panels); record environment (host class, CPU, container
limits, library versions); 3 runs, worst run reported alongside median run
(free-tier variance honesty).

## Benchmarks

| # | What | How |
|---|---|---|
| B1 | PyTorch vs ONNX vs ONNX-INT8 inference | `ml/evaluation/bench_inference.py` — batch-1 latency + memory on (a) dev machine, (b) serving container class; preprocessing broken out |
| B2 | OCR pipeline stages | per-stage timing over the label fixture set on serving container |
| B3 | API endpoint latency | k6 (or locust) against staging: auth, scan create, poll, history, nutrition endpoints; low concurrency (1/5/10 VUs — beta realism, not fantasy load) |
| B4 | DB query latency | pg query timings for the hot queries (scan aggregate read, history page, cache hit) with EXPLAIN ANALYZE archived |
| B5 | USDA cold vs cached lookup | scripted 100-lookup comparison (respecting rate limits) |
| B6 | Image upload path | presign→PUT→complete timing from a mobile-network-shaped connection (throttled) |
| B7 | End-to-end scan | Maestro-driven device test with timestamps at capture/upload/candidates/evidence; 20 repetitions per scan mode |
| B8 | Mobile memory/launch | Xcode Instruments / Android Studio profiler sessions, recorded methodology |
| B9 | Backend memory under load | RSS tracking during B3 |
| B10 | Cold start | Space-sleep → first-request timing, 5 samples |
| B11 | Assistant latency | first-token + complete over 20 canned questions (quota-aware) |

## Cadence

B1 on every model candidate (part of promotion gates); B2 on OCR changes; B3/B4/B9
per release; B7 before beta releases; others on demand. Regression rule: p95 worse
than budget (PERFORMANCE_BUDGET) or >25% worse than last report → investigate before
release.
