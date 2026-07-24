# Secret Management

## Inventory

| Secret | Used by | Rotation |
|---|---|---|
| Database URL/credentials (Neon) | API | on suspicion; provider-rotatable |
| Object-storage keys (R2 access key/secret) | API | 90 d |
| JWT signing key (EdDSA private) | identity module | versioned kid; rotate 180 d (old key kept for verify window) |
| USDA FDC API key | nutrition module | annual |
| LLM provider API key | assistant module | 90 d |
| Email provider key | identity | 90 d |
| W&B API key | ML pipelines only (never the API service) | 90 d |
| Demo-account seed password | deploy scripts | per redeploy |

(OCR is in-process PaddleOCR — no secret. OFF requires none.)

## Rules

- **No secrets in git, images, or client code** — CI secret scanning (gitleaks)
  blocks; mobile app contains zero API secrets (it authenticates as the user).
- **Local dev:** `.env` files (gitignored) from `.env.example` templates (keys named,
  values blank); Docker Compose reads env.
- **CI:** GitHub Actions encrypted secrets; least scope per workflow; no secrets in
  fork-triggered runs (`pull_request` without secrets; `pull_request_target`
  avoided).
- **Deployed (beta):** host-managed secret env vars (HF Spaces secrets / Render env
  groups) — the free-tier "managed secret storage". AWS design upgrades to Secrets
  Manager + IAM task roles (AWS_ARCHITECTURE).
- **Access pattern:** pydantic-settings loads at boot; secrets never logged (settings
  repr redacts); never in error payloads.
- **Blast-radius separation:** W&B key exists only in ML/CI contexts; DB credentials
  are per-environment (Neon branch per env); demo environment uses separate R2
  bucket + DB branch.
- **Incident play:** suspected leak → rotate at provider → redeploy → audit-log
  review → gitleaks history scan → note in `docs/security/reviews/`.
