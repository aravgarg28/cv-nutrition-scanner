# Adversarial Review (Phase 25)

Seven personas challenged the full plan. Findings are graded: 🔴 fixed by revision
(doc edited), 🟠 accepted risk (recorded, owner-visible), 🟢 challenge withstood.

## 1. Computer-vision hiring manager

- 🟢 *"Is the classifier used beyond capability?"* — No: confirmation-gated top-5,
  OOD routing, class-hints framed as non-detections, phone-domain eval set
  quantifying the gap. This is the right shape.
- 🟢 *"15 experiments — padding?"* — E1–E16 each answer a distinct question; ~105
  GPU-hrs fits the free quota; negative results are kept.
- 🟠 *"CLIP zero-shot (E4) might land embarrassingly close to your fine-tune."* —
  Accepted: if it does, that's a finding the report states plainly; the training
  story then leans on calibration/OOD/serving rigor. Honest > flattering.
- 🟢 *"Food-101 license?"* — flagged as R0 review task with recorded outcome
  (T-018), not assumed.

## 2. Full-stack hiring manager

- 🟢 Modular monolith + Postgres queue + no-Redis: right-sized, well argued in ADRs.
- 🔴 *"Is hosting a real authenticated user API on HF Spaces free tier within its
  intended use/ToS?"* — Real risk of surprise. **Revision:** STORAGE_STRATEGY now
  carries a `[VERIFY HF ToS]` action with Render/Fly-alternatives note and a
  fallback decision path before T-059.
- 🟠 *"Neon 0.5 GB with jsonb caches?"* — TTL sweeps + 70% alert exist; accepted
  with monitoring.

## 3. Mobile engineer

- 🔴 *"Live blur hints via preview frame analysis need frame processors —
  VisionCamera — which Expo Go doesn't host."* — Correct. **Revision:** CAMERA_UX
  demoted live-frame hints to a dev-build enhancement; Expo-Go-compatible path is
  post-capture checks + gyro level + exposure heuristics from capture metadata.
- 🟢 Barcode scanning in Expo Go via expo-camera: supported.
- 🟠 Expo Go SDK-version churn during a long beta: testers must update; dev-build
  channel is the mitigation when it bites. Accepted.

## 4. MLOps engineer

- 🟢 Registry-as-W&B-aliases + models-baked-in-images + promotion gates: coherent,
  rollback story is real (image tag revert).
- 🟢 No orchestration platform (AD-17): correctly resisted.
- 🟠 Kaggle session flakiness threatening wave cadence: resumable runs + no
  deadline (D3) absorb it. Accepted.

## 5. Application-security engineer

- 🟠 Self-built auth (AD-12) is the classic risk. Contained: argon2id, rotation +
  reuse detection, lockout, senior review (T-008), IDOR suite, no-enumeration
  responses. Accepted with review gates; Cognito path documented for AWS.
- 🟢 Upload pipeline (subprocess decode, canonical re-encode, EXIF strip) is above
  the bar for a beta.
- 🟠 No WAF/object-access logs on free tier: documented residual with AWS upgrade
  path. Accepted.
- 🟢 OCR-as-injection-vector: treated seriously (capability boundary + output
  validation + fixtures), and honestly (residual-risk statement).

## 6. Food-allergy safety reviewer

- 🟢 The status taxonomy, asymmetry principle, NOT_FOUND wording, demotion rules,
  forbidden-strings enforcement, and fixture-first regression policy form a
  defensible safety core.
- 🔴 *"OFF barcode data can be wrong/crowdsourced — a DECLARED-from-OFF status
  borrows label authority the source doesn't have."* — Fair. **Revision:**
  ALLERGEN_POLICY: OFF-derived statuses must show source as "product database
  (Open Food Facts)" — never "the label" — and carry the check-the-label line in
  the evidence sentence itself.
- 🟠 Users may screenshot NOT_FOUND rows and treat them as clearance out of
  context. The footer is inside the rendered component (screenshots carry it);
  accepted beyond that — no app can prevent misuse of screenshots.
- 🟢 Severity-blind conservative design (no per-user severity modulation) is the
  right call.

## 7. Skeptical product manager

- 🟠 *"MVP too broad — four scan modes plus assistant plus export?"* — Partly
  conceded: it IS broad, but (a) owner explicitly chose all four modes (D13) with
  no deadline (D3), (b) the roadmap stages R1→R3 so a usable product exists at
  every gate, (c) panel mode — the riskiest — is last and gated (Checkpoint E can
  still slip it to R5). Accepted with the staging as the control.
- 🟢 *"Does Food-101 match the product?"* — The product's allergen core is
  OCR/barcode-driven, where Food-101 is irrelevant; the classifier serves the
  photo mode with honest framing. Matched.
- 🟢 *"Is pgvector justified or résumé decoration?"* — Narrow, real role (corpus
  retrieval with citations); explicitly barred from structured facts. Justified —
  barely, and the docs admit RAG is the most cuttable MVP item after panel mode.
- 🟢 *"Could the résumé bullets be honestly supported?"* — Every placeholder maps
  to a planned artifact; T-063 senior review enforces "show me".
- 🟠 *"Will 10 real testers actually materialize?"* — Owner's social circle;
  success metric is modest (≥10 testers × 3 scans). Accepted.

## Revisions applied

1. STORAGE_STRATEGY — HF Spaces ToS verification gate + fallback path (finding 2.1).
2. CAMERA_UX — live-frame analysis moved behind dev-build; Expo-Go-safe heuristics
   substituted (finding 3.1).
3. ALLERGEN_POLICY — OFF-sourced status attribution + inline check-the-label line
   (finding 6.1).

## Standing verdicts

The MVP survives review as staged (R1→R3 gates are the safety valve on breadth).
The two decisions most likely to be revisited under real-world pressure: panel-scan
scope (Checkpoint E) and HF Spaces as host (pre-T-059 verification).
