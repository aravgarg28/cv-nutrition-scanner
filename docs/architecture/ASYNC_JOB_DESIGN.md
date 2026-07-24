# Async Job Design

## What runs async

| Operation | Why async | Latency class |
|---|---|---|
| Image post-processing (EXIF strip, thumbnail) | I/O + CPU, not user-blocking | seconds |
| Classification inference | CPU-bound (~0.5–2 s) + queueing fairness | seconds |
| OCR pipeline | CPU-heavy (2–6 s) | seconds |
| Label parsing + allergen evidence | Fast but pipeline-ordered | sub-second |
| Nutrition lookup (cold cache) | External API | seconds |
| Corpus embedding/ingestion | Batch | minutes |
| Export assembly | Batch | minutes |
| Account deletion cascade | Batch, must be reliable | minutes |
| Cache refresh (FDC/OFF) | Scheduled | background |
| Feedback/dataset build prep (R5) | Batch | background |

Synchronous (deliberately): serving-math recompute, profile edits, history reads,
barcode lookup on warm cache (fast path), auth.

## Options considered

| System | Verdict |
|---|---|
| Celery (+Redis/RabbitMQ broker) | Heavyweight for one container; broker = extra free-tier dependency; famous operational sharp edges. Rejected for MVP |
| Dramatiq (+Redis) | Nicer than Celery, still needs broker | Rejected for MVP |
| RQ (+Redis) | Simple, but Redis dependency + separate worker process | Runner-up |
| **Postgres-backed queue, in-process workers** | Zero new infrastructure (Postgres already there), transactional enqueue (job + state change commit atomically — a real correctness win for the scan state machine), `FOR UPDATE SKIP LOCKED` polling, asyncio worker tasks in the API process | **Chosen for MVP** |
| AWS SQS + worker service | The documented AWS-target design (AWS_ARCHITECTURE); slots in behind the same interface | Later |
| Lambda orchestration / Step Functions | Wrong fit for a monolith beta; vendor-coupled | Documented, not used |

## Design

- **Interface:** `JobQueue.enqueue(job_type, payload, idempotency_key, run_at?)` /
  worker registry `@job("scan.classify")`. Implementations: `PostgresJobQueue` (MVP),
  `SqsJobQueue` (AWS design). No business code touches the implementation.
- **Table:** `jobs(id, type, payload jsonb, idempotency_key unique, state
  queued|running|succeeded|failed|dead, attempts, max_attempts, run_at, locked_by,
  locked_at, last_error, created_at)`.
- **Workers:** N asyncio consumers in the API process (CPU-bound steps run in a
  thread/process pool sized to container CPUs; ONNX session is shared, thread-safe).
  Poll with `SELECT … FOR UPDATE SKIP LOCKED`; visibility timeout via `locked_at`
  sweep for crashed workers.
- **Retries:** exponential backoff (1 m/5 m/25 m), max 3 default; terminal failure →
  `dead` + scan state `*_failed` with user-visible retry affordance. External-API
  jobs get provider-aware backoff.
- **Idempotency:** every job idempotent by (scan_id, stage); re-delivery safe;
  results written with upsert semantics.
- **Ordering:** pipeline order enforced by the scan state machine (stage N enqueues
  N+1 on success), not by queue ordering guarantees.
- **Observability:** queue depth, oldest-queued age, per-type latency/failure
  metrics (OBSERVABILITY); job_id in all logs.
- **Graceful shutdown:** workers drain current job on SIGTERM (host redeploys);
  locked-job sweep recovers the rest.

## Scale escape hatch

If one container saturates: run the same image with `ROLE=worker` (workers only, no
HTTP) on a second free instance — the queue table already coordinates. That's the
entire "distributed" migration until AWS/SQS.
