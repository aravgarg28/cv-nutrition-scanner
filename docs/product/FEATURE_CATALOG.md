# Feature Catalog

Status: **INC** = included (MVP, Releases 1–3) · **POST** = postponed (Release 4–5+) ·
**EXP** = experimental/research · **EXC** = excluded.
Priority: P0 (MVP-blocking) / P1 (MVP-important) / P2 (later).
Release numbers reference [ROADMAP](ROADMAP.md).

Acceptance criteria (AC) here are summaries; task-level ACs live in
[IMPLEMENTATION_TASKS](../execution/IMPLEMENTATION_TASKS.md).

## Authentication
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Email+password signup/login | Real users need protected accounts | argon2id hashing, JWT access+refresh, email verification | P0 | R1 | — | Credential stuffing → rate limits | Auth flows pass integration tests incl. lockout | INC |
| Session revocation & password reset | Lost device/password | Refresh-token rotation, reset via emailed link | P0 | R1 | auth | Token theft | Revoked token rejected ≤60s | INC |
| Social login / MFA | Convenience/security | — | P2 | R5+ | auth | — | — | POST |
| Guest mode | Try-before-signup | — | P2 | — | — | Second data path | — | EXC (D22) |

## Onboarding
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Decision-support disclosure | Users must understand limits before use | Blocking "I understand" consent, versioned + timestamped | P0 | R1 | — | **Safety-critical**: skippable disclosure = false reassurance | Cannot reach scan without recorded consent | INC |
| Training-data opt-in | Consent for feedback loop | Default-off toggles (corrections / corrections+images) | P0 | R3 | consent storage | Privacy | Opt-out users' data never enters dataset builds (tested) | INC |

## Dietary profile
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| 9 US major allergens | Core matching input | Card picker, editable | P0 | R2 | — | — | Profile changes re-evaluate open scan views | INC |
| Custom allergens | Beyond the 9 | Free text + caution about limited synonym coverage | P1 | R2 | ontology | Weaker matching must be disclosed | Custom terms match exact+fuzzy with distinct evidence type | INC |
| Diet rules (veg/vegan/gluten) | Rule-based compatibility | Toggle per rule; per-ingredient reasoning | P1 | R2 | ingredient parsing | Ambiguous additives must show "unclear" | Rule engine fixture tests pass | INC |
| Managed second profile (child) | Parents scan for kids | Profile switcher under one account | P1 | R3 | profiles | Adults-only accounts (D12) | Results clearly badge active profile | INC |
| Halal/kosher flags | Religious needs | Flag pork/alcohol-derived ingredients, explicit non-verdict framing | P2 | R5 | ontology | Certification cannot be inferred — high miscommunication risk | — | POST |
| Intolerances (lactose, FODMAP…) | Broader needs | — | P2 | R5+ | ontology | — | — | POST |

## Camera & upload
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Camera capture + gallery upload | Input path | Expo camera, mode-specific overlays | P0 | R1 | — | Permission denial path | Denial shows gallery fallback | INC |
| Client-side quality pre-check | Wasted uploads, bad OCR | Blur/brightness heuristic → retake suggestion | P1 | R2 | — | Never hard-block | Blurry fixture triggers suggestion | INC |
| Multi-shot label capture | Long wrap-around labels | — | P2 | R4 | OCR stitching | — | — | POST |

## Image quality (server)
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Server quality assessment | Downstream confidence | Blur/exposure/resolution score stored per image; gates messaging | P1 | R2 | pipeline | Feeds uncertainty display | Score persisted; low quality reflected in result framing | INC |

## Food recognition
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Single-food top-5 classification | Identify unlabeled food | Fine-tuned Food-101 model, calibrated confidence, ONNX CPU serving | P0 | R1 | ML pipeline | Never auto-commit; below threshold → guess framing (D14) | Parity + threshold tests pass; measured metrics published | INC |
| Mandatory confirmation | Predictions ≠ facts | Nutrition only after user confirms | P0 | R1 | ↑ | Core safety behavior | No nutrition rendered pre-confirmation | INC |
| Manual food search | OOV foods, low confidence | Search USDA foods by name | P0 | R1 | nutrition module | Rescues unknown foods | Search returns and confirms any FDC food | INC |
| Unknown-food detection | Non-food / OOV images | Calibrated threshold + OOD score → "not sure" state | P1 | R2 | calibration exp. | Prevents confident nonsense | Non-food fixture yields unknown state | INC |
| Multi-food detection/segmentation | Real plates | — | P2 | R4 | detection model | Scope | — | EXP |
| On-device inference | Offline, privacy | — | P2 | R5 | ONNX mobile | — | — | POST |

## Portion estimation
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Serving presets + adjustment | "How much am I eating?" | USDA portions + stepper; deterministic recompute | P0 | R1 | nutrition | "Per selected serving" framing | Math property-tested | INC |
| Depth/volume estimation | Automatic portions | — | — | EXP | segmentation, calibration | Cannot ship unvalidated numbers (D18) | — | EXP |

## OCR
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Ingredient-label OCR | Read labels | PaddleOCR pipeline; verbatim panel; completeness indicator | P0 | R2 | OCR arch | OCR errors → allergen misses; completeness must display | Fixture suite accuracy reported; verbatim text always shown | INC |
| Inline OCR correction | OCR is imperfect | Editable fields; downstream re-evaluation | P0 | R2 | ↑ | Corrections recorded | Edit re-runs allergen matching | INC |
| Nutrition-panel scan (core fields) | Packaged nutrition | Field extraction limited to D17 set + serving size; validation vs plausible ranges | P1 | R2 (late) | OCR arch | Impossible values flagged, user confirms | Panel fixtures parse core fields or fail visibly | INC 🟡 |
| Full micronutrient panel parsing | Complete data | — | P2 | R5 | ↑ | — | — | POST |

## Barcode & products
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Barcode scan → OFF lookup | Fast accurate packaged data | On-device detection; OFF API + cache; staleness flag | P0 | R2 | — | Stale/missing OFF data disclosed | Known-product fixture returns tagged data with provenance | INC |

## Nutrition lookup
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| USDA FDC integration + cache | Authoritative generic nutrition | Class→FDC mapping table; Postgres cache; provenance stored | P0 | R1 | data module | "Typical values" framing; missing ≠ 0 | Mapped foods return D17 nutrients with FDC ID | INC |
| Deterministic serving math | Trust | Pure functions, unit conversions, rounding rules | P0 | R1 | — | Never LLM | Property + golden tests | INC |

## Allergens & dietary compatibility
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Allergen ontology + matcher | Hidden synonyms | 9 majors + synonyms/derived terms; evidence-typed matches | P0 | R2 | ontology data | **The** safety surface; policy language exact | Full ALLERGEN_TESTS fixture catalog passes | INC |
| May-contain / facility detection | Cross-contamination signals | Phrase patterns → distinct statuses, high prominence | P0 | R2 | ↑ | Must never downrank | Fixtures pass | INC |
| Class-inferred allergen hints | Meal photos have no label | "Foods like X often contain Y" framing only | P1 | R2 | class→allergen table | Must never look like detection | Framing string literal-tested | INC |
| Diet rule engine | Veg/vegan/gluten checks | Per-ingredient verdicts: yes/no/unclear + reasoning | P1 | R2 | parsing | "Unclear" is a first-class outcome | Rule fixtures pass | INC |

## Assistant
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Per-scan grounded Q&A | "Why this warning?" | Tool-calling LLM over deterministic tools + RAG citations; per-scan threads | P1 | R3 | tools, RAG | Boundaries per MEDICAL_BOUNDARIES; injection defenses | AI_EVALUATION suite passes | INC |
| Quota degradation | Free tier limits | Deterministic scan summary fallback + notice | P1 | R3 | ↑ | No silent failure | Simulated quota-exhaustion test | INC |
| General nutrition education Q&A | Broader questions | RAG over curated corpus only, cited | P2 | R3 | RAG | No medical advice | Citation correctness sampled | INC (narrow) |

## Scan history & corrections
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| History list + detail | Re-check vetted products | Thumbnails, statuses, reopenable results | P0 | R3 | storage | — | Reopened scan shows identical evidence | INC |
| Correction capture | Model improvement + honesty | Correction events stored; opt-in gating for training use | P0 | R1 | consent | Poisoning risk managed in FEEDBACK_LOOP | Events recorded with provenance | INC |

## Privacy & administration
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Data export | User ownership | Async JSON archive job | P1 | R3 | jobs | — | Archive contains all user entities | INC |
| Account deletion | User ownership | Hard delete cascade + audit | P0 | R3 | jobs | Must include images/embeddings/threads | Deletion verified by test sweep | INC |
| Admin: model status & metrics | Ops visibility | Read-only admin endpoints (model version, error rates) | P2 | R3 | observability | Admin authz | Role-gated | INC (minimal) |
| Notifications | Re-engagement | — | P2 | — | — | — | — | EXC (beta) |

## ML/MLOps & platform
| Feature | Problem | Behavior | Pri | Rel | Deps | Risks/Safety | AC | Status |
|---|---|---|---|---|---|---|---|---|
| Dataset tooling (Food-101 pipeline) | Reproducible training | Download/verify/split/version scripts | P0 | R1 | — | Leakage prevention | Checksums + split manifest committed | INC |
| Training + W&B tracking | Experiment rigor | Resumable Kaggle/Colab runs, 15+ experiments | P0 | R1+ | dataset | No invented metrics | Runs reproducible from config | INC |
| ONNX export + parity tests | Serving | Export script + tolerance tests | P0 | R1 | training | Silent numeric drift | Parity within tolerance in CI | INC |
| Model registry (W&B artifacts) | Which model is live? | Staged aliases: candidate/staging/production | P1 | R3 | W&B | Rollback path | Promotion requires eval gates | INC |
| Monitoring dashboards | Drift/degradation | Confidence & correction-rate tracking | P1 | R3 | observability | No raw-image retention w/o consent | Metrics emitted + charted | INC |
| Feedback→retraining pipeline | Improve model | Consent-gated dataset builds, review queue | P2 | R5 | consent | Poisoning controls | Only opted-in, reviewed data | POST (design now) |
| Observability (logs/traces/metrics) | Debuggability | Structured logs, request IDs, latency histograms | P0 | R1 | — | Redaction rules | No PII/health data in logs (tested) | INC |
