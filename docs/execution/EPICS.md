# Epics

| Epic | Outcome | Release | Key docs |
|---|---|---|---|
| EP-01 Repository foundation | monorepo scaffold, tooling, CI, compose stack | R0 | REPOSITORY_STRUCTURE, LOCAL_DEVELOPMENT, CI_CD |
| EP-02 Shared schemas & contracts | Pydantic models, enums (statuses/states), OpenAPI→TS client, error envelope | R0 | ALLERGEN_POLICY, API_DESIGN |
| EP-03 Identity & auth | signup/login/verify/reset/revoke, JWT, lockout | R1 | AUTHENTICATION_AND_AUTHORIZATION |
| EP-04 User profiles & consent | dietary profiles, allergen/rule config, managed profiles, consent records, disclosure flow | R1–R3 | PRIVACY_MODEL, J1/J2 |
| EP-05 Image storage & upload | presign flow, validation, canonicalization, EXIF strip, thumbnails, signed GETs | R1 | IMAGE_LIFECYCLE, UPLOAD_SECURITY |
| EP-06 Scan workflow engine | scan state machine, jobs queue, orchestration, polling API | R1 | BACKEND_ARCHITECTURE, ASYNC_JOB_DESIGN |
| EP-07 ML data pipeline | Food-101 download/verify/dedup/split/manifest, W&B artifacts, subsets | R1 | DATA_PIPELINE, DATASET_STRATEGY |
| EP-08 Classification baseline & training | training CLI, baseline + contender runs, W&B tracking, calibration | R1+ | TRAINING_PLAN, EXPERIMENT_PLAN |
| EP-09 Evaluation & error analysis | metrics harness, robustness suites, OOD eval, reports, model card | R1+ | EVALUATION_PLAN, ERROR_ANALYSIS |
| EP-10 ONNX export & serving | export, parity, inference module, thresholds, readiness | R1 | ONNX_STRATEGY, INFERENCE_DEPLOYMENT |
| EP-11 Nutrition integration | FDC client+cache, class→FDC mapping, serving math, search | R1 | NUTRITION_DATA_STRATEGY, NUTRITION_CALCULATION |
| EP-12 OCR pipeline | engine integration, preprocessing stages, section detection, completeness | R2 | OCR_ARCHITECTURE |
| EP-13 Ingredient & panel parsing | grammar parser, lexicon, panel field extraction, corrections | R2 | INGREDIENT_EXTRACTION, NUTRITION_LABEL_EXTRACTION |
| EP-14 Allergen engine | ontology, matcher, statements, evidence assembly, diet rules | R2 | ALLERGEN_ONTOLOGY, ALLERGEN_POLICY |
| EP-15 Products & barcode | OFF client, product cache, barcode API | R2 | NUTRITION_DATA_STRATEGY |
| EP-16 Mobile foundation | Expo scaffold, auth flows, navigation, design-system safety kernel | R1 | MOBILE_ARCHITECTURE |
| EP-17 Mobile capture & results | camera UX, upload, processing, candidates, nutrition, serving | R1–R2 | SCREEN_SPECIFICATIONS, CAMERA_UX |
| EP-18 Mobile evidence & corrections | allergen evidence UI, OCR review/correction, profile screens | R2 | J6–J8 |
| EP-19 History & privacy features | history, per-scan delete, export, account deletion | R3 | J10/J11 |
| EP-20 Assistant & RAG | corpus, ingestion, retrieval, tools, provider adapter, validators, threads | R3 | docs/ai/* |
| EP-21 Web demo | demo page, demo role, fixture gallery | R1–R3 | AD-18, DEMO_DATA |
| EP-22 Security hardening | rate limits, IDOR suite, redaction tests, secret scanning, abuse monitoring | R1–R3 | docs/security/* |
| EP-23 Observability & monitoring | logs/metrics, admin endpoints, probes/alerts, drift jobs | R1–R3 | OBSERVABILITY, MONITORING |
| EP-24 Deployment | Dockerfiles, compose, staging/beta Spaces, Neon/R2 setup, keep-warm, backups | R1 | docs/deployment/* |
| EP-25 Demo & presentation prep | demo seeds, scripts, README, model-card publication | R3 | docs/demo/*, docs/presentation/* |
| EP-26 Research track (post-MVP) | portion evaluation, multi-food, distill/quant, feedback dataset | R4–R5 | docs/portion/*, FEEDBACK_LOOP |
