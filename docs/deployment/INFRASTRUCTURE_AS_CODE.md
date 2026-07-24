# Infrastructure as Code

## Evaluation

| Tool | Fit |
|---|---|
| **Terraform** | Industry-standard résumé value; provider coverage for the AWS target AND some free-tier providers (Cloudflare R2 has a provider; Neon has one). ✅ recommended |
| AWS CDK | Excellent for AWS-only; TypeScript synergy — but useless for the free-tier stack we actually run, and heavier to demo without deploying |
| Pulumi | Nice, but paid-tier pressure on state backend and less universal in job posts |
| CloudFormation | AWS-only, verbose; no |

## Decision (deferred-but-scaffolded)

**Terraform, in two stages:**
1. **Now (beta):** minimal real usage where it's free and useful — R2 bucket
   config, (optionally) Neon project/branches — plus **the complete AWS target as
   written-but-unapplied modules** (`infrastructure/aws/…`: vpc, ecs, rds, s3+cf,
   sqs, secrets, alarms). `terraform validate` + `plan` (against a sandbox account
   with no apply) run in CI — the code is reviewable portfolio artifact and the
   migration runbook's substance. **No `apply` on paid resources (D0).**
2. **Migration:** apply the AWS modules per AWS_ARCHITECTURE runbook.

HF Space itself has no useful TF provider surface — its config (Dockerfile + README
metadata + secrets) is committed in-repo, which serves the same reviewability goal.

State: local + committed plan outputs for the unapplied modules; Terraform Cloud
free tier for state if/when applying (verify current free-tier terms then).
