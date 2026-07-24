# API Design

REST, JSON, versioned base path `/v1`. Auth: `Authorization: Bearer <JWT access>`.
Uniform error envelope `{error:{code,message,request_id}}`. All timestamps UTC
ISO-8601. Pagination: cursor-based (`?cursor=&limit=`). Idempotency: mutating
endpoints accept `Idempotency-Key` header (stored 24 h). Rate limits are per-user
sliding windows (values in config; listed here as initial defaults).

Full request/response schemas live in shared-schemas (OpenAPI is generated, not
hand-written); this doc specifies behavior.

## Authentication (public endpoints; IP rate limits)

| Endpoint | Notes |
|---|---|
| `POST /v1/auth/register` | email+password; 422 weak password; sends verification email. 5/hr/IP |
| `POST /v1/auth/verify-email` | token from email |
| `POST /v1/auth/login` | returns access (15 min) + refresh (30 d, rotating); lockout: 10 fails/15 min → 423. 10/hr/IP |
| `POST /v1/auth/refresh` | rotates refresh; reuse-detection revokes family |
| `POST /v1/auth/logout` | revokes refresh family |
| `POST /v1/auth/password-reset` + `/confirm` | email flow; resets revoke all sessions |

Audit: all auth events (success/fail/lockout/reset) logged to audit module.

## Profile & preferences

| Endpoint | Notes |
|---|---|
| `GET/PUT /v1/profile` | display name, settings. PUT validates; audited |
| `GET/PUT /v1/profile/dietary` | allergens[] (canonical IDs), custom_allergens[], diet_rules[]; PUT re-evaluation note: previously rendered scan views recompute on next load |
| `POST/GET/PUT/DELETE /v1/profile/managed` | managed sub-profiles (D12); max 5 |
| `GET/PUT /v1/profile/consents` | training-data opt-ins (D16); every change audited with version |

## Images & scans

| Endpoint | Notes |
|---|---|
| `POST /v1/images` | multipart upload OR `POST /v1/images/presign` → direct-to-storage PUT (preferred; UPLOAD_SECURITY gates both). Returns image_id. 30/hr/user |
| `POST /v1/scans` | `{mode: photo\|label\|panel\|barcode, image_id?, barcode?}`; validates mode↔payload; returns scan with state. Idempotency-Key honored. 30/hr/user |
| `GET /v1/scans/{id}` | full scan aggregate: state, candidates, ocr, nutrition, allergen evidence, provenance. Poll target; `Retry-After` hint while processing |
| `POST /v1/scans/{id}/confirm` | `{food_id}` from candidates or search; 409 if already confirmed (idempotent same-body) |
| `POST /v1/scans/{id}/corrections` | `{target: classification\|ocr_field, field_ref, corrected_value}`; re-runs downstream; records event |
| `PUT /v1/scans/{id}/serving` | `{serving_id \| grams}`; recompute is synchronous (fast, deterministic) |
| `POST /v1/scans/{id}/panel/confirm` | user-confirmed OCR panel values (NUTRITION_LABEL_EXTRACTION flow) |
| `DELETE /v1/scans/{id}` | soft-delete → hard sweep (IMAGE_LIFECYCLE); 204 |
| `GET /v1/scans` | history list (cursor); filters: mode, date range |

## Reference data

| Endpoint | Notes |
|---|---|
| `GET /v1/foods/search?q=` | FDC-backed search (cache-first); returns typed candidates. 60/hr/user |
| `GET /v1/foods/{id}` | food + typical nutrition + portions + provenance |
| `GET /v1/products/{barcode}` | OFF-backed (cache-first); staleness flag; 404 → suggest label scan |
| `GET /v1/allergens` | canonical allergen list + descriptions (static, cacheable) |

## Assistant

| Endpoint | Notes |
|---|---|
| `POST /v1/scans/{id}/assistant/messages` | `{content}` (2k char cap); returns message + assistant reply (or fallback summary object with `degraded: true`); 20 msgs/scan, 60/day/user (free-quota protection) |
| `GET /v1/scans/{id}/assistant/messages` | thread history |

## Privacy & account

| Endpoint | Notes |
|---|---|
| `POST /v1/account/export` | starts async job; `GET /v1/account/export/{job_id}` → signed URL (24 h). 2/day/user; audited |
| `DELETE /v1/account` | requires `{confirmation: "DELETE"}` + fresh reauth; async cascade; audited; 202 |

## Admin (role-gated)

`GET /v1/admin/model` (active version, thresholds, registry state) ·
`GET /v1/admin/health/detail` (queue depth, external API status, error rates) —
read-only in MVP; audited access.

## Cross-cutting behaviors

- **Authorization:** every user-scoped resource query filters by owner at repo layer
  (not handler layer); IDOR tests enumerate endpoints (THREAT_MODEL).
- **Validation:** shared-schemas Pydantic; unknown fields rejected; images by
  signature not extension.
- **Error codes (canonical set):** `validation_error`, `unauthorized`, `forbidden`,
  `not_found`, `conflict`, `rate_limited`, `provider_unavailable`,
  `processing_failed`, `quota_degraded`.
- **Audit-relevant endpoints:** auth, consents, export, delete, admin — all write
  audit events synchronously.
- **Public health check:** `GET /healthz` (liveness), `GET /readyz` (model loaded,
  DB reachable).
