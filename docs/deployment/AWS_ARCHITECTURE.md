# AWS Architecture

Two architectures: the **free-tier beta** we actually deploy (D0/D6) and the **AWS
target** we document as designed-not-deployed (portfolio + future migration).

## A. Free-tier beta (deployed)

```
Expo app / Web demo
      │ HTTPS
      ▼
Hugging Face Space (Docker, 2 vCPU/16GB, free)
  └─ FastAPI monolith + in-process workers
     ├─ ONNX Runtime (classifier) + PaddleOCR (baked in image)
     ├─ Neon Postgres (free, pgvector)   ← SQLAlchemy
     ├─ Cloudflare R2 (free 10GB, S3 API) ← images, backups
     ├─ USDA FDC / OFF APIs (cached)
     └─ LLM provider free tier
GitHub Actions: CI + keep-warm cron + weekly pg_dump→R2
```

Constraints accepted: sleep/cold-start (mitigated per INFERENCE_DEPLOYMENT), no WAF,
single region, provider free-tier SLAs. Every component chosen for **hard-stop or
no-overage billing** (COST_MODEL).

## B. AWS target (designed, not deployed — D0)

### Service evaluation

| Service | Role | Verdict |
|---|---|---|
| **ECS on Fargate** | API + worker services (same image, `ROLE` env) | ✅ core compute — always-on, no cold starts, right for CPU inference (INFERENCE_DEPLOYMENT) |
| API Gateway | managed edge | ❌ ALB instead — cheaper at steady traffic, WebSocket-ready, simpler with ECS |
| ALB | routing/TLS | ✅ |
| Lambda | spiky offline jobs (export assembly, cache refresh) | ✅ narrow role only; ❌ for interactive CV/OCR (cold starts; see INFERENCE_DEPLOYMENT) |
| S3 | images (+ versioning, access logs, lifecycle) | ✅ |
| CloudFront | web demo static + signed image delivery | ✅ |
| RDS PostgreSQL (db.t4g.micro→small) | primary DB, **pgvector supported (PG15+)** | ✅ |
| ElastiCache Redis | cache/queue upgrade | Deferred — Postgres queue holds until metrics say otherwise |
| SQS | job queue (swap behind JobQueue interface) | ✅ at migration |
| Step Functions | multi-stage orchestration | ❌ — state machine lives in app code; revisit only if workers multiply |
| ECR | images | ✅ |
| CloudWatch | logs/metrics/alarms | ✅ |
| Cognito | managed auth | ❌ — self-built JWT auth is a portfolio point and already done; Cognito migration optional later |
| Secrets Manager | secrets + rotation | ✅ |
| WAF | edge protection | ✅ on ALB/CloudFront (rate rules, common rule set) |
| SageMaker endpoint | model serving | ❌ — cost/complexity unjustified for one CPU model |

### Target topology

VPC (2 AZ) → public subnets: ALB (+WAF); private subnets: ECS services
(api ×2, worker ×1, autoscaling on CPU/queue depth), RDS (multi-AZ optional),
VPC endpoints for S3/ECR/Secrets (no NAT for the hot path; one NAT for external
APIs) → S3 + CloudFront → Route 53 → CloudWatch dashboards/alarms → SQS between api
and workers → Secrets Manager with IAM task roles (no static keys).

### MVP-on-AWS vs later-scale

- **MVP-on-AWS (if budget appears):** single-AZ, api×1 + worker×1 Fargate spot
  where safe, db.t4g.micro, no WAF→basic rate limiting, ~$40–70/mo estimate
  `[VERIFY AT MIGRATION]`.
- **Scale-up:** multi-AZ RDS, autoscaled services, WAF, CloudFront for API edge
  caching of reference data, ElastiCache, separate inference service if profiling
  demands (BACKEND_ARCHITECTURE seams).

### Migration runbook (summary)

Images: rclone R2→S3 · DB: pg_dump/restore Neon→RDS (downtime window fine at beta
scale) · Queue: config swap PostgresJobQueue→SqsJobQueue · Config/secrets: env→
Secrets Manager · DNS cutover → decommission free tier. Prereqs: IaC in place
(INFRASTRUCTURE_AS_CODE), COST_MODEL alarms first.
