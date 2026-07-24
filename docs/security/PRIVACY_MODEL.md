# Privacy Model

Real beta users + health-adjacent data (D1). Posture: data minimization, explicit
consent, full user control. (US beta; not a legal-compliance document — a design
one. Revisit formally before commercial launch, D24.)

## Data inventory (what we store and why)

| Data | Class | Purpose | Retention |
|---|---|---|---|
| Email, password hash | P | account | until deletion |
| Allergen/dietary profiles (incl. managed) | **H** | core matching | until deletion |
| Food images + thumbnails | P | scan processing + history (D21) | until user deletes |
| OCR text + parsed fields | P | results + history | with scan |
| Scan results/evidence/servings | P | history | with scan |
| Assistant threads | P | continuity + provenance (D23) | with scan |
| Corrections/confirmations | P | product function; training only if consented | until deletion; training copies per consent |
| Consent records | P | proof | account life + audit summary |
| Device info | — | **not collected** (no analytics SDK) | — |
| Geolocation | — | **never** (EXIF GPS stripped) | — |
| Inference/ops events | O | monitoring (pseudonymous ids, no content) | 90 d |
| Audit events | O | security/accountability | 1 yr |

## Health-related preference handling (H-class rules)

- Never in logs, error messages, analytics, or crash reports.
- Never in LLM prompts as raw profile: tools return rule *outcomes*
  (TOOL_ARCHITECTURE); the provider sees "user's profile conflicts: milk (SYNONYM)"
  only when the user asks a profile question about that scan.
- Admin has no read path (AUTHENTICATION).
- Encrypted in transit (TLS) and at rest (provider disk encryption); field-level
  encryption assessed: deferred (free-tier KMS absent; documented residual, AWS
  design adds KMS).

## LLM provider boundary (the key third-party decision)

What can reach the LLM provider: user's question text, scan-derived facts via tool
outputs, corpus chunks. What cannot: images (LLM is text-only in MVP), email/
identity, full profile, other scans. Provider chosen with a **no-training-on-API-
data policy** (verify current terms of Groq / Google AI Studio at implementation —
Google AI Studio free tier historically permits training use: **if so, it is
disqualified for scan-derived content**, making Groq-class no-training terms the
default; record outcome in ARCHITECTURE_DECISIONS). Disclosure in privacy screen:
"questions you ask the assistant are processed by {provider}."

## Consent model

- Blocking decision-support disclosure (J1) — versioned acknowledgment.
- Training-data opt-ins (D16): two independent, default-off toggles (corrections /
  images); consent version + timestamp recorded append-only; revocation stops future
  dataset builds (limitation about already-trained models disclosed at opt-in).
- Email verification doubles as contact consent for transactional mail only (no
  marketing).

## Data minimization commitments

No analytics SDKs, no advertising ids, no geolocation, no contact import, no
third-party trackers in app or web demo. In-app feedback widget stores text the user
types, nothing ambient.

## Export & deletion (J11)

Export: complete JSON archive (all P/H entities + consent history) + signed image
URLs (24 h). Deletion: hard cascade (DATA_MODEL §deletion semantics) with tombstone +
audit summary; completes ≤ 72 h (target: minutes); verified by automated sweep test.

## Third-party processors (beta list)

Postgres host (Neon), object storage (Cloudflare R2), container host (HF Spaces),
LLM provider (per above), email provider, W&B (**no user data** — ML artifacts
only), USDA FDC + OFF (**queries only**: barcodes/food ids flow out, no user
identity attached). Listed in the privacy screen.

## Logging redaction

Structured logs use an explicit field allowlist; free-text fields (OCR text, user
messages, profile terms) are never logged — only lengths/hashes/enums.
Redaction verified by tests (log-capture assertions in CI) (OBSERVABILITY).
