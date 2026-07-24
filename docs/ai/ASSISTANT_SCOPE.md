# Assistant Scope

Per-scan Q&A assistant (D20, D23). Powered by a free-tier hosted LLM behind a
provider-agnostic interface, grounded via deterministic tools (TOOL_ARCHITECTURE) and
RAG over a curated corpus (RAG_ARCHITECTURE). Boundaries per
[MEDICAL_BOUNDARIES](../safety/MEDICAL_BOUNDARIES.md).

## Allowed question categories

| Category | Example | Grounding |
|---|---|---|
| Scan explanation | "Why do you think this is pad thai?" | scan result tool (confidence, candidates) |
| Nutrition explanation | "What nutrients are high in this?" | nutrition tool + deterministic %DV comparisons |
| Ingredient explanation | "What is xanthan gum?" | RAG corpus (ingredient definitions, cited) |
| Allergen-evidence explanation | "Why the milk warning?" | allergen-evidence tool (status, span, rule) |
| Dietary-profile comparison | "Which ingredient conflicts with vegan?" | profile-compare tool (rule engine output) |
| Source explanation | "Where does this nutrition data come from?" | provenance fields |
| Uncertainty explanation | "What is uncertain about this scan?" | uncertainty-summary tool |
| Serving comparison | "How does this compare with the sodium daily value?" | serving-calc tool (deterministic) |
| General educational | "Why is fiber important?" | RAG corpus only, cited |
| App help | "How do I delete a scan?" | help-docs RAG partition |

## Prohibited / restricted categories (tested in AI_EVALUATION)

- **Safety verdicts** ("is this safe?", "can I eat this?") → scripted boundary
  response (MEDICAL_BOUNDARIES).
- **Medical**: diagnosis, treatment, medication, condition management → decline +
  professional-guidance line.
- **Allergen reassurance beyond evidence** ("it's probably fine") → forbidden;
  responses restate evidence types only.
- **Exact-nutrition claims from photos** → always "typical values" framing.
- **Weight-loss/calorie-target advice, body commentary** → out of scope reply
  (eating-disorder-sensitive rules).
- **Overriding packaging** ("the label is probably wrong") → forbidden.
- **Fabricated citations/sources** → every factual sentence must trace to a tool
  result or retrieved chunk; the response validator (PROMPT_INJECTION_DEFENSE
  §output validation) rejects unsourced factual claims about the scan.
- **Cross-user/cross-scan data** → tools are scoped to the authenticated user's
  current scan; the model cannot request others (authorization at tool layer).
- **Off-domain requests** (write code, politics, etc.) → polite refusal, scope
  statement.

## Conversation model

- Threads are per-scan (D23); context = system prompt + scan context summary + thread
  history (truncated oldest-first at token budget) + tool results.
- Suggested prompts on entry (J9) bias usage toward in-scope questions.
- Quota degradation (D20): provider 429/quota → deterministic fallback: structured
  scan summary + notice "assistant is temporarily unavailable; here's everything we
  know about this scan." Never a silent failure, never a queued stale answer.

## Tone & framing rules

Factual, calm, evidence-first. Uncertainty stated plainly. No emoji in allergen
contexts. Uses the same normative vocabulary as the UI (ALLERGEN_POLICY status
names), so app and assistant never contradict each other terminologically.
