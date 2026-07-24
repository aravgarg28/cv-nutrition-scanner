# Authentication & Authorization

## Authentication

- **Method:** email + password (D22). Passwords: argon2id (memory 64 MB, iterations
  3, parallelism 4 — tune to host), min length 10, zxcvbn-style strength check,
  breach-list check via bundled top-100k list (offline, free).
- **Email verification:** signed single-use token link, 24 h expiry; unverified
  accounts can log in but cannot create scans (limits abuse; keeps onboarding
  smooth). Email delivery: free transactional tier (e.g., Brevo/Resend free tier —
  pick at implementation with D0 verification) with console-log fallback in dev.
- **Tokens:** JWT access (15 min, HS256 or EdDSA — EdDSA preferred; key in secret
  store) + opaque rotating refresh token (30 d) stored hashed (`session` table) with
  **family reuse detection**: a reused rotated token revokes the whole family
  (stolen-token containment).
- **Mobile storage:** refresh in expo-secure-store; access in memory only
  (MOBILE_ARCHITECTURE).
- **Password reset:** emailed single-use token, 1 h expiry; reset revokes all
  sessions; no user enumeration (uniform responses).
- **Lockout / rate limits:** 10 failed logins / 15 min → 423 with backoff; IP-level
  caps on auth endpoints (API_DESIGN).
- **Social login:** out of MVP (D22). **MFA:** post-beta (R5) — TOTP planned, design
  slot in `user` table (no schema change needed: separate `mfa_secret` table later).
- **Fresh-reauth gate:** destructive actions (account deletion) require password
  re-entry within 5 min.

## Authorization

- **Model:** two roles — `user`, `admin`. No org/tenant hierarchy (single-consumer
  product; D12 managed profiles are rows under the owner, not separate principals).
- **Enforcement:** repo-layer scoping — every query on P/H tables takes `user_id`
  from the verified token, applied in the repository (not per-handler); code review
  + IDOR tests enforce (THREAT_MODEL).
- **Admin:** separate role claim; admin endpoints read-only aggregates; **no admin
  access to H-class data** (profiles/allergens) by construction — the endpoints
  don't exist. Admin actions audited.
- **Managed profiles:** authorization identical to owner data (they ARE owner data);
  active-profile selection is client state validated server-side (profile must
  belong to user).

## Sessions & revocation

- Logout → revoke family. Password change/reset → revoke all. Account deletion →
  revoke all + tombstone.
- Access tokens are short-lived and not revocable individually (accepted 15-min
  window); a `token_version` claim checked against user row allows emergency
  global-invalidations.

## Web demo

Read-only demo account with pre-seeded scans; separate role claim `demo` that
disables writes server-side (not just UI); short sessions; aggressive rate limits.
