# Failure Handling

Uniform principles: fail **visibly** (no silent degradation), fail **safe**
(allergen logic errs to INSUFFICIENT, never to NOT_FOUND), fail **recoverably**
(retry affordances everywhere), fabricate **nothing**.

| Failure | System behavior | User experience |
|---|---|---|
| Model service unavailable (session dead / readiness fail) | `/readyz` fails → host restarts container; in-flight scans → `classification_failed` | Processing screen → "identification failed — retry"; retry re-enqueues |
| OCR failure (crash/timeout) | job retries ×3 → `ocr_failed`; allergen statuses → INSUFFICIENT (never NOT_FOUND) | "We couldn't read this label — retry or retake"; evidence screen shows insufficient-info rows |
| Nutrition provider (FDC) down | cache-first already; cold miss → `provider_unavailable` | Values from cache tagged "cached <date>"; else "nutrition source unavailable — try later"; never fabricated |
| OFF down / product missing | same pattern; 404 distinct from outage | "Product not found — scan the ingredient label instead" vs "product database unreachable" |
| Database unavailable | API 503s fast (no long hangs — 2 s conn timeout); healthz reflects | Global "service unavailable" state; mobile keeps cached views with staleness chips |
| Object storage failure (upload) | presign/PUT errors surface; no scan row without image | "Upload failed — retry"; capture retained locally (queue) |
| Job timeout | visibility-timeout sweep re-queues (idempotent stages); max attempts → `*_failed` | stage-specific retry card |
| Assistant/LLM failure or quota | timeout 20 s / 429 → deterministic fallback summary, `degraded: true` | Notice + full structured scan summary — never silence, never stale LLM text |
| Low-confidence result | not a failure: D14 flow | guess framing + search |
| Duplicate request | Idempotency-Key store (24 h) returns original result; job idempotency by (scan, stage) | no double scans/charges (quota) |
| Scan interrupted (app killed mid-flow) | server state machine persists; draft store keeps scan id | reopening app → scan resumes from server state in history/processing |
| Mobile connectivity lost | OFFLINE_AND_EDGE: capture queue, cached reads, offline chip | honest offline UI; auto-resume |
| Partial pipeline success (classified, nutrition failed) | scan state `enrichment_partial`: candidates shown, nutrition section shows its own error+retry | per-section errors, not all-or-nothing |
| Consent/audit write failure | the guarded operation **fails** (consent changes, deletions require audit success) | error + retry; correctness over availability for these paths |
| Email provider down | verification/reset queued with retry; login unaffected | "email is delayed" notice |
| Keep-warm lapse / cold start | first request slow | waking banner (PERFORMANCE_BUDGET) |

## Patterns

- **Timeouts everywhere:** DB 2 s connect/10 s statement; external APIs 5 s (FDC/OFF)
  with one retry + jitter; LLM 20 s; jobs per-type max runtime.
- **Circuit breaker** (simple in-process) on FDC/OFF/LLM: 5 failures/60 s → open
  30 s → half-open probe; open state = immediate cached/degraded path (no thundering
  retries against a down provider).
- **Bulkheads:** job concurrency caps per type (one OCR at a time on small hosts)
  so one heavy stage can't starve the API.
- **Idempotency:** stages keyed (scan_id, stage); external mutations none (read-only
  providers); email sends deduped by token.
- **Crash recovery:** locked-job sweep (ASYNC_JOB_DESIGN); scan state machine has no
  in-memory-only states.
