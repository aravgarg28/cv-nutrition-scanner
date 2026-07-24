# Tool Architecture

Deterministic tools the assistant calls. Tools are ordinary service functions with
JSON-schema'd IO, an allowlist registry, and uniform authorization. The LLM never
touches the database, runs SQL, or sees another user's rows — tools do, under the
authenticated user's scope.

## Uniform properties (all tools)

- **Authorization:** every call carries (user_id, scan_id) resolved server-side from
  the session — never from model output. Tool layer verifies scan ownership;
  violation → tool error, logged as security event.
- **Validation:** args validated against JSON schema; unknown fields rejected;
  string args length-capped; enums closed.
- **Error behavior:** structured error {code, safe_message}; the model receives
  safe_message only; errors never fabricate data ("nutrition record unavailable").
- **Logging:** every call logged (tool, args hash, scan_id, latency, outcome) —
  no health-profile values in logs (redaction per PRIVACY_MODEL).
- **Evidence:** tool outputs carry provenance fields; the model is instructed to
  cite them and the validator checks (AI_EVALUATION).
- **Sensitive data:** tools return the minimum: e.g., profile-compare returns rule
  outcomes, not the full allergen profile; the raw profile never enters the prompt.

## Tool registry (MVP)

### `get_scan_result`
- **In:** `{}` (scan from context) · **Out:** `{scan_type, status, confirmed_food?,
  candidates[{name, confidence}], image_quality, created_at}`
- Notes: candidates capped at 5; confidences calibrated values as shown in UI.

### `get_ocr_fields`
- **In:** `{section?: "ingredients"|"nutrition_panel"|"statements"}` · **Out:**
  verbatim text + parsed fields + completeness + per-field confidence flags.
- Notes: returns the same data the UI shows — assistant and UI can't diverge.

### `get_allergen_evidence`
- **In:** `{allergen_id?: string}` · **Out:** status rows exactly as ALLERGEN_POLICY
  (status_code, allergen, evidence sentence, source span, rule_id, source).
- Notes: the assistant's allergen answers must be assembled from these rows only.

### `get_nutrition_record`
- **In:** `{}` · **Out:** typed record: basis, per-100g values, source (FDC/OFF/OCR),
  fdc_id/barcode, retrieved_at, `typical_values: bool` flag.

### `calculate_serving_nutrition`
- **In:** `{serving_id | grams}` · **Out:** computed values + serving label +
  rounding applied — calls `nutrition-core` (deterministic; the LLM does no math).

### `compare_dietary_profile`
- **In:** `{}` · **Out:** per active-profile rule/allergen: outcome
  (conflict/no-conflict-found/unclear/insufficient) + evidence refs. Mirrors UI rule
  engine results verbatim.

### `get_uncertainty_summary`
- **In:** `{}` · **Out:** structured uncertainty: classification confidence band,
  OCR completeness, missing data list, data-source staleness flags — powering "what
  is uncertain about this scan?".

### `retrieve_source_text`
- **In:** `{evidence_id}` · **Out:** verbatim OCR span + surrounding context (the
  "view text" equivalent).

### `search_corpus` (RAG entry; see RAG_ARCHITECTURE)
- **In:** `{query, category?}` · **Out:** top chunks {chunk_id, title, heading_path,
  content, reviewed_at}.

## Non-tools (deliberately absent)

No write tools (assistant cannot mutate scans/profiles), no user-lookup, no raw-SQL,
no web fetch, no cross-scan history access in MVP (a `list_my_scans` tool is a
possible R5 addition with its own review). The absence is the security boundary:
capabilities not registered cannot be prompted into existence.

## Orchestration

Simple tool-loop (provider-native function calling; LangChain optional — decision:
use the provider SDK directly + a thin adapter; LangChain only if multi-provider
abstraction proves painful, recorded in ARCHITECTURE_DECISIONS). Max 6 tool calls per
turn; loop timeout 20 s; on timeout → deterministic fallback summary.
