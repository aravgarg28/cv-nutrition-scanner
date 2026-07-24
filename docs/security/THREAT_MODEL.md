# Threat Model

Assets, ranked: (1) allergen/dietary profiles + scan history (health-adjacent PII),
(2) account credentials/sessions, (3) user images, (4) integrity of allergen results
(a tampered "no allergens" is a physical-harm vector), (5) free-tier resources
(exhaustion = outage/cost), (6) model artifacts.

| Threat | Vector | Mitigations (doc) |
|---|---|---|
| Account takeover | credential stuffing, weak passwords, token theft | argon2id, lockout, rotating refresh tokens w/ reuse detection, SecureStore, password-strength checks (AUTHENTICATION) |
| Broken authorization / cross-user exposure | missing owner filters | repo-layer user scoping, IDOR test suite enumerating every user-scoped endpoint with two-user fixtures (TEST_STRATEGY) |
| Image URL leakage | long-lived/capability URLs | 15-min signed GETs minted per request after ownership check; private bucket; no public ACLs (IMAGE_LIFECYCLE) |
| Insecure direct object references | guessable ids | UUIDv7 + ownership checks (defense in depth — ids alone are not authz) |
| Malicious uploads | polyglot files, parser exploits | signature allowlist, size caps, subprocess decode, canonical re-encode (UPLOAD_SECURITY) |
| Decompression bombs | huge-pixel images | `MAX_IMAGE_PIXELS` 25 MP + bytes cap pre-decode |
| Image parser CVEs | Pillow/codec vulns | pinned+scanned deps (CI), subprocess isolation, minimal codecs in image |
| OCR prompt injection | instructions printed on labels | full PROMPT_INJECTION_DEFENSE stack; read-only tools; output validation |
| SQL injection | string-built queries | SQLAlchemy bound params everywhere; no raw SQL without review; sqlfluff/lint |
| XSS (web demo) | reflected OCR text | web demo escapes all rendered OCR/user text; CSP; no innerHTML |
| CSRF | browser demo session | web demo uses same-site strict cookies or bearer-only; state-changing endpoints require bearer |
| SSRF | barcode/product ids reaching URL builders | external calls only to allowlisted hosts (FDC/OFF/LLM provider) with pinned base URLs; no user-supplied URLs anywhere |
| CORS misconfig | wildcard origins | explicit origin allowlist (app scheme n/a; web demo domain only) |
| API abuse / DoS | scripted scans, LLM quota burn | per-user+IP rate limits, quotas (API_DESIGN), CAPTCHA-free friction via email verification, worker concurrency caps |
| Excessive cloud cost | free-tier overrun | hard quotas; alerts; providers chosen with hard-stop (not overage-billing) behavior (COST_MODEL) |
| Model extraction | high-volume query probing | rate limits; calibrated top-5 only (no full logit vector in API); acceptable residual for beta |
| Model evasion / adversarial images | crafted inputs forcing misclassification | confirmation UX bounds impact (user picks); no automated decisions from classifier; documented residual |
| Data poisoning (feedback) | malicious corrections opted into training | consent + review queue + provenance + anomaly screening before dataset entry (FEEDBACK_LOOP) |
| Secret leakage | keys in code/logs/git | SECRET_MANAGEMENT: env-only, secret scanning in CI, log redaction |
| S3/R2 misconfig | public bucket | private-by-default, IaC-checked config, periodic public-access audit script |
| Sensitive logs | profiles/OCR text in logs | structured logging with explicit field allowlist; redaction tests (OBSERVABILITY) |
| Dependency vulns | supply chain | Dependabot + pip-audit/npm audit in CI; lockfiles; minimal base images |
| Assistant data leakage | prompt exfil of profile/other users | tool minimality (no cross-user tools), profile never in prompt beyond rule outcomes, output validation |
| Audit tampering | covering tracks | append-only audit table (no UPDATE/DELETE grants), DB role separation |

## Trust boundaries

Client ↔ API (untrusted client), API ↔ external providers (untrusted responses:
schema-validate FDC/OFF/LLM payloads), OCR text ↔ assistant (untrusted data), user
uploads ↔ image pipeline (untrusted bytes), admin role ↔ user data (admin sees
aggregates only — no H-class access).

## Accepted residual risks (beta, documented honestly)

No WAF (free tier), no provider object-access logs, model-extraction exposure at
rate-limit ceiling, single-region free-tier durability, Sentry omitted (privacy) →
slower prod debugging. Each has an AWS-design upgrade path (AWS_ARCHITECTURE).

## Security testing

IDOR suite, upload-abuse suite, injection suites (SQL/prompt), rate-limit tests,
secret-scan CI gate, dependency scans, and a pre-beta manual pass over the OWASP API
Top 10 checklist recorded in `docs/security/reviews/`.
