# Architecture Decision Records

Format per record: Context · Options · Decision · Rationale · Consequences · Risks ·
Revisit when. Owner-ratified product decisions live in
[DECISION_LOG](../decisions/DECISION_LOG.md) (D0–D24); ADRs record the *technical*
decisions implementing them. Detailed comparisons live in the linked docs; ADRs are
the authoritative summary.

---

**AD-1 · MVP scan modes** — Context: D13. Options: photo-only → all-modes.
**Decision:** photo + label + barcode + panel(core-fields), staged in that order
within R1–R2. Rationale: barcode is cheap/highest-fidelity; panel is riskiest → last
+ scoped. Consequences: 4 capture UIs, 3 parsing paths. Risks: panel OCR quality.
Revisit: if panel fixtures <70% field accuracy at R2 gate → slip panel to R5. 🟡 panel scoping awaits owner ratification.

**AD-2 · Food model selection** — Context: MODEL_SELECTION. Options: pre-anoint
EfficientNetV2 / experiment-driven choice. **Decision:** experiment-driven:
ResNet-50 baseline; EffV2-S vs ConvNeXt-T contenders; MobileNetV3 mobile track;
decision metric macro-F1 + ECE at equal CPU-latency budget. Rationale: serving is
CPU; résumé mention isn't evidence. Consequences: E1–E5 before commitment. Risks:
free-GPU schedule. Revisit: at Wave-1 gate.

**AD-3 · Cloud vs on-device inference** — Context: D15, Expo Go limits.
**Decision:** cloud ONNX Runtime CPU for MVP; on-device (distilled/quantized) R5 via
dev-builds. Rationale: one model surface, updatable, Expo-Go-compatible.
Consequences: offline can't classify; cold-start UX work. Revisit: R5.

**AD-4 · OCR system** — Context: OCR_ARCHITECTURE. Options: Tesseract / PaddleOCR /
EasyOCR / ML Kit / paid cloud. **Decision:** PaddleOCR server-side behind `OcrEngine`
protocol; ML Kit as R5 on-device option; paid cloud rejected (D0). Rationale:
packaging-text accuracy vs Tesseract; zero cost; privacy. Consequences: ~1 GB deps
in image; CPU latency budget. Risks: PaddleOCR version churn → pinned + benchmark
protocol. Revisit: if fixture allergen-term recall unsatisfactory at R2 gate.

**AD-5 · Portion estimation** — Context: D18, MIDAS_ASSESSMENT. **Decision:** FDC
serving presets + manual adjust; depth/volume = R4 research with pre-registered
go/no-go (PORTION_EVALUATION). Rationale: monocular metric volume from one
uncalibrated image is not defensible. Consequences: no "auto portion" marketing
claim. Revisit: after R4 measurements.

**AD-6 · Lambda vs container service** — Context: INFERENCE_DEPLOYMENT.
**Decision:** container (HF Space free now; ECS Fargate in AWS target); Lambda only
for spiky offline jobs in the AWS design. Rationale: interactive CV/OCR + cold
starts don't mix; warm model cache matters. Revisit: at AWS migration.

**AD-7 · Modular monolith vs microservices** — **Decision:** modular monolith,
import-linted module boundaries, in-process workers. Rationale: one team, one host,
coupled domain; boundaries = future seams. Consequences: discipline via tooling.
Revisit: if a module needs independent scaling (OCR first candidate).

**AD-8 · Job system** — Context: ASYNC_JOB_DESIGN. Options: Celery/Dramatiq/RQ/
Postgres-queue/SQS. **Decision:** Postgres-backed queue (SKIP LOCKED) behind
`JobQueue` interface; SQS as documented AWS swap. Rationale: zero new infra,
transactional enqueue with scan state machine. Risks: DB load at scale (fine for
beta). Revisit: sustained queue depth or >5 rps enqueue.

**AD-9 · PostgreSQL + pgvector roles** — **Decision:** Postgres = system of record +
job queue + external cache; pgvector = corpus-chunk embeddings ONLY (no user-content
embeddings; no structured-data RAG). Rationale: deterministic queries for facts;
privacy boundary. Revisit: only with a reviewed feature needing user-content
vectors.

**AD-10 · Nutrition sources** — Context: NUTRITION_DATA_STRATEGY. **Decision:** USDA
FDC (generic, public domain) + OFF (barcode, ODbL w/ attribution) + user-confirmed
OCR panels; precedence & conflict rules as documented; paid DBs rejected (D0).
Revisit: EU expansion (R5+).

**AD-11 · Image retention** — Context: D21. **Decision:** keep-until-delete;
canonical re-encode at ingest; EXIF/GPS stripped; signed 15-min GETs; 7-day
soft-delete window. Revisit: user feedback on retention preferences (R5
configurable-retention feature).

**AD-12 · Authentication** — **Decision:** self-built email+password: argon2id, JWT
access (EdDSA) + rotating refresh w/ family reuse detection; no Cognito/social/MFA
in MVP. Rationale: portfolio value + zero cost + full control. Risks: crypto
implementation care → heavily tested, standard libs only. Revisit: MFA at R5;
Cognito at AWS migration (optional).

**AD-13 · RAG boundaries** — **Decision:** RAG for explanatory corpus only;
deterministic tools for all facts; bge-small embeddings in-process; no LangChain
(provider SDK + thin adapter) unless multi-provider pain proves otherwise.
Revisit: if provider-swapping code exceeds ~300 lines, adopt an abstraction.

**AD-14 · Model feedback** — Context: D16, FEEDBACK_LOOP. **Decision:**
consent-gated collection now, human-reviewed dataset builds R5, per-user caps,
no auto-pseudo-labeling. Revisit: at first retrain.

**AD-15 · React Native architecture** — **Decision:** Expo managed + Expo Router +
TanStack Query + Zustand + SecureStore; no analytics/crash SDKs in beta.
Rationale: D7 distribution; server-state-first app shape. Revisit: dev-build move
at R5 (on-device ML Kit/ONNX).

**AD-16 · AWS deployment posture** — Context: D0/D6. **Decision:** free-tier stack
(HF Space + Neon + R2) deployed; AWS target (ECS/RDS/S3/SQS/CloudFront/Secrets/WAF)
fully designed + Terraform-validated but unapplied. Rationale: honest zero-cost beta
with credible, reviewable cloud design. Revisit: when budget exists (COST_MODEL
priority ladder).

**AD-17 · No ML orchestration platform** — **Decision:** Makefile + CLIs + CI smoke
(TRAINING_PIPELINE); no Airflow/Kubeflow/Prefect. Rationale: one model, free
compute; orchestration theater rejected. Revisit: multiple recurring pipelines.

**AD-18 · Web demo surface** — Context: D8. **Decision:** small Vite React page on
the same API with `demo` role + fixture gallery (no public uploads by default).
Rationale: recruiter access without app install; abuse-resistant. Revisit: post-beta.
