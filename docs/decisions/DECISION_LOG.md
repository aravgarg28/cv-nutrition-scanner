# Decision Log

Product and scope decisions made by the project owner during the planning interview
(2026-07-12). These are **binding** on all downstream documents and implementation
tasks. Changes require an explicit new entry with date and rationale.

Status legend: ✅ ratified by owner · 🟡 provisional (owner delegated; ratify at review)

| ID | Decision | Answer | Status |
|----|----------|--------|--------|
| D0 | Budget | **$0.** Free tiers only; no paid services, APIs, or infrastructure. Any doc recommending a tool must verify a free path exists. | ✅ final |
| D1 | Purpose | Portfolio-first, but with real beta testers (friends/family) and product ambition. Privacy, auth, and safety behavior must be production-real, not demo-ware. | ✅ |
| D2 | Target roles | All four: ML/Applied-AI engineer, CV engineer, Full-stack engineer, MLOps engineer. The project must credibly demonstrate breadth. | ✅ |
| D3 | Timeline | No deadline. Quality over speed. Owner guides; Implementer implements. | ✅ |
| D4 | Owner experience | Intermediate across PyTorch, FastAPI, React Native, Postgres, Docker, AWS, MLOps. Docs should explain rationale, not just prescribe. | ✅ |
| D5 | Training compute | Free Kaggle GPU (~30 hrs/wk, T4/P100) and Colab free tier. Training must be resumable/checkpointed and sized accordingly. | ✅ |
| D6 | Hosting | Free-tier PaaS for the live beta; AWS architecture documented as designed-not-deployed. Concrete picks (Postgres host, container host, object storage) decided in [STORAGE_STRATEGY](../architecture/STORAGE_STRATEGY.md) / [AWS_ARCHITECTURE](../deployment/AWS_ARCHITECTURE.md). | 🟡 delegated |
| D7 | Mobile distribution | Expo (React Native) with Expo Go + development builds. No app-store accounts. | ✅ |
| D8 | Portfolio artifacts | Public review-ready GitHub repo + live recruiter demo link (small web demo of the scan pipeline). | ✅ |
| D9 | Primary user | Allergy + dietary + nutrition scanning first; later intended to fold into a broader fitness product. Architecture stays extensible (e.g., daily-intake aggregation later); fitness features are **not** in scope now. | ✅ |
| D10 | Severe-allergy users | In scope as **decision support with heavy caveats**. Design defensively for anaphylaxis-risk users: conservative wording, evidence-typed statuses, never a "safe to eat" verdict. | ✅ |
| D11 | Region | US-first: FDA 9 major allergens, US Nutrition Facts panel, USDA FoodData Central. EU support deferred. | ✅ |
| D12 | Minors | Adults only. Parents manage a child's allergen profile under their own account. No child accounts. | ✅ |
| D13 | MVP scan modes | All four: single-food photo, ingredient-label scan, barcode lookup, nutrition-facts panel scan. Panel scan scoped to core fields (serving size, calories, macros, sodium, sugars) first. | ✅ (panel scoping 🟡) |
| D14 | Low-confidence behavior | Show top-5 with explicit low-confidence framing plus manual text search. Never auto-select a prediction. | ✅ |
| D15 | Inference location | Cloud-first: ONNX Runtime (CPU) on the backend. On-device inference is a later release. | ✅ |
| D16 | Feedback loop | User confirmations/corrections (and optionally images) become retraining data **only with explicit opt-in consent** collected at onboarding. | ✅ |
| D17 | Nutrition scope (MVP) | Calories, protein, carbohydrates, fat, fiber, sugar, sodium. Micronutrients, cholesterol detail, glycemic data deferred. | ✅ |
| D18 | Portion size (MVP) | Serving-size presets + manual adjustment; nutrition labeled "per selected serving". No automated volume estimation. MiDaS/depth = post-MVP research experiment only. | ✅ |
| D19 | Dietary profiles (MVP) | 9 US major allergens + user-defined custom allergens + vegetarian + vegan + gluten avoidance. Halal/kosher post-MVP with non-verdict framing. | ✅ |
| D20 | Assistant | Free-tier hosted LLM (Groq / Google AI Studio class) behind a provider-agnostic interface; strictly grounded in scan data + cited RAG docs; graceful degradation when quota exhausted. | ✅ |
| D21 | Image retention | Images kept as part of scan history until the user deletes them (per-scan delete + full account wipe). | ✅ |
| D22 | Guest mode | None in MVP. Email + password accounts. | ✅ |
| D23 | Assistant chat storage | Per-scan conversation threads, stored server-side, deleted with the scan/account. | ✅ |
| D24 | Commercial posture | Free beta now, possibly paid later → only commercially-usable licenses for datasets, models, and data sources. | ✅ |

## Provisional decisions awaiting ratification

- **D6 concrete hosting picks** — comparison and recommendation in
  [AWS_ARCHITECTURE](../deployment/AWS_ARCHITECTURE.md) §Free-tier beta architecture.
- **D13 panel scoping** — core-fields-first proposal in
  [NUTRITION_LABEL_EXTRACTION](../ocr/NUTRITION_LABEL_EXTRACTION.md).
- **Final classifier architecture** — determined by the experiment plan
  ([EXPERIMENT_PLAN](../ml/EXPERIMENT_PLAN.md)), not pre-committed.

## Non-negotiable guardrails (apply to every document and task)

1. Honest uncertainty everywhere; information is always typed as one of: observed /
   retrieved-authoritative / model-predicted / user-provided / estimated / missing-or-
   uncertain / safety-warning.
2. No "safe" / "allergen-free" verdicts, ever. "Not detected" ≠ "not present".
3. All nutrition math is deterministic code, never an LLM.
4. OCR text, product data, and user text are untrusted inputs to the assistant.
5. No invented metrics — placeholders until measured.
6. Training-data collection is opt-in only.
7. Full data export and deletion are first-class features.
