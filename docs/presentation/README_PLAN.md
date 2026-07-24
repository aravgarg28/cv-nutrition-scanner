# README Plan

The README is the 90-second version of the project for a recruiter and the 15-minute
map for an engineer. Written at T-063 with **measured values only**.

## Structure

1. **Hero:** name, one-liner ("Photograph food or labels → evidence-typed nutrition
   and allergen information that never pretends to be a guarantee"), badges (CI,
   license), 2 GIFs (scene 1 + scene 4 from DEMO_SCENARIOS), **live demo link** +
   demo credentials.
2. **The problem** (3 sentences): label reading is slow and dangerous to get wrong;
   apps that answer confidently without evidence are part of the problem.
3. **What it does:** the 4 scan modes, evidence-typed allergen statuses (screenshot
   of the status taxonomy), the safety model in one paragraph + link to
   docs/safety/.
4. **Architecture:** one diagram (mobile/web → FastAPI monolith [modules] →
   Postgres+pgvector / R2 / ONNX+PaddleOCR in-process → FDC/OFF/LLM) + "designed
   AWS target" thumbnail linking AWS_ARCHITECTURE; bullet list of deliberate
   choices (modular monolith, Postgres queue, tools-not-RAG for facts) each linking
   its ADR.
5. **ML methodology:** dataset (Food-101 + honest domain-gap note), experiment
   table (all waves, real numbers, negative results kept), calibration/reliability
   figure, OOD behavior, ONNX parity + CPU serving numbers, link to model card and
   reports.
6. **Evaluation results:** the headline table — official-test AND phone-domain
   columns (top-1, top-5, macro-F1, ECE) + latency p50/p95; every number generated
   from eval JSONs by a script (no hand-typed metrics).
7. **Safety model:** status taxonomy table, the asymmetry principle, forbidden-
   renderings list, "what this app will never tell you".
8. **Screenshots:** 6-panel grid (candidates, nutrition, evidence, OCR review,
   assistant with citations, history).
9. **Demo:** link, credentials, 3-scene suggested walkthrough, note on free-tier
   cold start.
10. **Running locally:** the LOCAL_DEVELOPMENT quickstart block.
11. **Testing:** suite inventory with counts + the safety-suite explanation (why
    allergen tests are release-gating).
12. **Deployment:** free-tier stack diagram + designed-not-deployed AWS statement
    (the honesty is the feature).
13. **Limitations (prominent, not buried):** domain gap numbers, 101-class
    vocabulary, OCR failure modes, no portion automation (link MIDAS_ASSESSMENT),
    US-only labels, beta-scale monitoring caveats.
14. **Future work:** R4/R5 roadmap summary.
15. **Attribution & licenses:** USDA FDC (public domain), Open Food Facts (ODbL),
    Food-101, PaddleOCR, model checkpoints — per license notes; MIT for this repo.

## Rules

No metric without a linked artifact; no "production-ready" claims; the word "safe"
never appears in product descriptions; screenshots show real app states (no
mockups); keep hero section readable on GitHub mobile.
