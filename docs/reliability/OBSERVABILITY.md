# Observability

Free-tier stack: structlog JSON to stdout (host log viewer) + Prometheus-format
`/metrics` (scraped ad hoc / by a free Grafana Cloud tier `[VERIFY free tier]`, else
metrics snapshot job writes daily summaries to the DB for the admin endpoint) +
optional OpenTelemetry traces exported only in staging (console/Jaeger-in-compose).
Pragmatic > fancy; the design keeps OTLP wiring so AWS CloudWatch slots in later.

## Structured logs

- Always: timestamp, level, event, request_id, user_id (UUID only), scan_id, job_id,
  module, latency_ms, outcome.
- **Field allowlist enforced by the logging helper** — free text (OCR content, user
  messages, profile terms, emails) cannot be logged; only lengths/hashes/enums.
  Redaction verified by CI tests (log capture asserting forbidden patterns absent)
  (PRIVACY_MODEL).
- Request/job correlation: request_id propagates into enqueued jobs (job carries
  origin_request_id).

## Metrics (per name → purpose)

**Traffic/latency:** http_requests_total{route,code}, http_duration_seconds{route},
job_duration_seconds{type}, queue_depth, queue_oldest_age_seconds.
**ML:** inference_latency_seconds{model_version}, confidence_histogram
{model_version} (bucketed calibrated top-1), prediction_class_total (top-20 classes;
drift signal), unknown_state_rate, ood_score_histogram.
**OCR:** ocr_latency, ocr_completeness_histogram, ocr_failure_total{stage}.
**Safety-relevant product metrics:** allergen_status_total{status_code} (warning
rate — alert-fatigue monitoring per HUMAN_FACTORS), user_correction_total{target}
(correction rate = live model-quality proxy), not_found_demotion_total (completeness
demotions).
**External:** provider_request_total{provider,outcome}, circuit_state{provider},
cache_hit_ratio{source}, llm_quota_429_total.
**System:** process RSS, worker concurrency, db pool stats.

## Model drift signals (MONITORING details)

Confidence-distribution shift (weekly KS vs baseline), class-distribution shift,
correction-rate trend per class, unknown-rate trend — computed by a weekly job from
inference_event + feedback tables (no raw images touched; PRIVACY_MODEL).

## Alerting (free: GitHub Actions cron probes + email)

Probes: healthz/readyz fail, error-rate >5%/15 min (via metrics snapshot), queue
oldest-age > 10 min, DB size >70%, R2 usage >70%, LLM 429 rate spike, keep-warm
failures. Alert = email to owner + admin endpoint flag.

## Dashboards (admin endpoint + optional Grafana)

Scan funnel (created→confirmed→enriched), stage latencies, warning rates, correction
rates, provider health, quota usage. The admin API returns these as JSON
(API_DESIGN) so the web demo's admin page can render them — doubles as the MLOps
monitoring demo for interviews.

## Request IDs / user support

Every API error shows request_id in the error envelope; beta testers can screenshot
it; logs joinable by it end-to-end.
