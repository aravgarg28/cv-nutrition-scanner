# Demo Scripts

Three lengths, all built from DEMO_SCENARIOS scenes. Numbers cited during demos come
from the model card only.

## 3-minute (recruiter / career fair)

0:00 Hook: "Point it at food or a label; it tells you what it found, what it
couldn't, and why — it never tells an allergic user something is safe."
0:20 Scene 1 (clear classification) on device.
1:00 Scene 4 (allergen evidence: declared + may-contain + whey→milk).
2:00 Scene 5 (insufficient info) — "this 'we can't tell' is the hardest-designed
screen in the app."
2:40 Close: stack one-liner (fine-tuned classifier + ONNX CPU serving, PaddleOCR
pipeline, FastAPI/Postgres/pgvector, Expo RN, free-tier deploy) + repo/demo link.

## 7-minute (technical screen)

Scenes 1→2→3→4→5→7, narrating: calibration & thresholds at scene 2 (why top-5 +
confirmation UX), OCR pipeline stages at scene 3, evidence typing & asymmetry
principle at scenes 4–5, tools-vs-RAG split and injection defenses at scene 7.
End on the model card: measured metrics, phone-domain vs official-test gap,
limitations.

## 15-minute (technical walkthrough / onsite)

1. Product frame (2 min): personas, safety model, why "decision support".
2. Live demo (4 min): scenes 1–5 condensed + 7.
3. ML deep-dive (4 min): experiment matrix in W&B (waves, negative results),
   calibration/reliability diagram, OOD thresholding, ONNX parity + CPU serving
   rationale, error-analysis findings.
4. System deep-dive (3 min): modular monolith + Postgres queue (why not
   microservices/Celery), scan state machine, evidence-typed schema (non-null
   provenance), free-tier architecture vs documented AWS target.
5. Honest limits + roadmap (2 min): domain gap numbers, OCR failure modes, portion
   assessment (why MiDaS alone can't do volume), R4/R5 tracks. Questions.

Prep checklist per run: staging warm (keep-warm verified), demo account reset script
run, device charged + screen-mirror ready, fallback video recorded for scenes 1–7,
model-card printout/tab open.
