# Test Strategy

CI-blocking unless marked otherwise. Test code lives beside its module; cross-cutting
suites in `tests/`. Coverage philosophy: safety-critical paths get exhaustive
fixtures; the rest gets meaningful (not percentage-theater) coverage.

| Layer | Scope & tools | Blocking? |
|---|---|---|
| **Unit (Python)** | pytest: parsers, matchers, nutrition-core math (property tests via hypothesis), serving logic, validators | ✅ |
| **API integration** | pytest + httpx against app with test Postgres+MinIO containers: every endpoint happy+error paths, idempotency, rate limits (time-mocked) | ✅ |
| **Database** | migration up/down tests; constraint tests (evidence non-null, consent append-only); query-scoping tests | ✅ |
| **Authorization/IDOR** | two-user fixture sweep: every user-scoped endpoint × other-user's ids → 403/404; admin-role matrix; demo-role write-block | ✅ |
| **Mobile component** | RN Testing Library: safety-kernel components (StatusRow copy literal tests, ConfidenceBar, TypedFact), flows with mocked API | ✅ |
| **Mobile E2E** | Maestro on Android emulator (CI): J4→J8 happy path, low-confidence path, offline banner | ✅ (smoke set) |
| **Model/ML** | ML_TESTS doc: shapes, preprocessing parity, ONNX parity, threshold behavior, invalid inputs | ✅ (micro-model in CI; full on artifacts) |
| **OCR fixtures** | OCR_TEST_STRATEGY tiers 1–2 in CI; corpus benchmark nightly/manual | ✅ / reportable |
| **Nutrition calculation** | golden + property tests; FDC recompute cross-checks | ✅ |
| **Allergen rules** | ALLERGEN_TESTS full fixture catalog + forbidden-strings + framing literals | ✅ **release-gating** |
| **RAG** | retrieval eval set recall@k threshold; chunking round-trips; citation resolution | ✅ deterministic parts |
| **Prompt injection** | PROMPT_INJECTION_DEFENSE fixtures: deterministic tier in CI; live tier pre-release | ✅ / pre-release |
| **Upload security** | malicious-fixture suite: polyglots, bombs, oversized, wrong-signature, GPS-EXIF persistence check | ✅ |
| **Load (light)** | k6 smoke (B3 profile) against staging per release | pre-release |
| **Failure-recovery** | chaos-ish integration: provider-down (mocked 5xx/timeout) → circuit + degraded states; job crash → sweep recovery; partial pipeline states | ✅ |
| **Accessibility** | RN a11y lint + manual screen-reader script per release (checklist in repo) | lint ✅ / manual pre-release |
| **Deployment smoke** | post-deploy: readyz, seeded-fixture scan E2E, threshold sanity, latency spot-check (TRAINING_PIPELINE §9) | ✅ gates promote |
| **E2E scenarios** | END_TO_END_SCENARIOS catalog against staging | pre-release |

## Cross-cutting rules

- **No weakened assertions to pass** (IMPLEMENTATION_HANDOFF rule 9): fixing a failing test
  means fixing code or, with recorded justification, the fixture.
- Safety copy is **literal-string tested** (ALLERGEN_POLICY normative strings) —
  paraphrase = failure.
- Deletion completeness: dedicated sweep test creates a full user graph (scans,
  images, threads, consents), deletes account, asserts zero rows/objects remain
  (+ tombstone/audit exist).
- Log-redaction tests: capture logs during requests containing H-class data, assert
  forbidden patterns absent.
- Determinism: unit/integration suites run with fixed seeds and frozen time where
  relevant; flaky tests quarantined within 24 h (tracked issue) not retried-forever.
- Fixtures versioned; fixture changes to safety catalogs require the safety
  checklist (BUILD_SEQUENCE).
