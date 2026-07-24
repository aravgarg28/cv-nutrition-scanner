# Data Model

PostgreSQL 16 + pgvector. Conventions: UUIDv7 PKs; `created_at/updated_at`
timestamptz on all tables; FKs `ON DELETE` explicit per table; user-owned tables
carry `user_id` with a composite index; soft-delete via `deleted_at` only where
listed. Sensitivity classes: **H** = health-adjacent (profile/allergen data),
**P** = personal (account, images, scans), **C** = content/reference (public),
**O** = operational. Retention per class in PRIVACY_MODEL.

## Identity & consent

| Entity | Purpose / key fields | Relations & constraints | Sens | Retention/deletion |
|---|---|---|---|---|
| `user` | account: email (citext unique), password_hash (argon2id), email_verified, role (user\|admin), locked_until | — | P | hard delete on account deletion |
| `session` | refresh-token families: token_hash unique, family_id, expires_at, revoked_at, device_label | user FK cascade | P | expired purged 30 d |
| `consent_record` | append-only: kind (decision_support_disclosure \| training_corrections \| training_images), version, granted bool, at | user FK; **no updates** — new row per change | P | kept while account exists; summary retained in audit on deletion |
| `deletion_request` | account deletion job tracking: state, requested_at, completed_at | user FK (nullable post-delete; keeps tombstone) | O | permanent tombstone (proof of deletion) |

## Profiles (H — heightened protection)

| Entity | Purpose / key fields | Relations & constraints | Sens |
|---|---|---|---|
| `dietary_profile` | label ("Me", "Son"), is_default; max 5/user | user FK cascade | H |
| `profile_allergen` | profile↔allergen link OR custom: allergen_id nullable, custom_term nullable (XOR check constraint), created_at | profile FK cascade; unique(profile, allergen_id/custom_term) | H |
| `profile_diet_rule` | rule enum (vegetarian\|vegan\|gluten_avoidance) | profile FK cascade; unique(profile, rule) | H |

## Scanning core (P)

| Entity | Purpose / key fields | Relations & constraints |
|---|---|---|
| `scan` | mode (photo\|label\|panel\|barcode), state (state-machine enum), active_profile_id, deleted_at (soft), failure_code? | user FK cascade; profile FK set-null; index(user, created_at desc) |
| `scan_image` | image ref: storage_key unique, mime, bytes, width, height, sha256, exif_stripped bool, thumb_key | scan FK cascade |
| `image_quality_result` | blur_score, brightness, resolution_ok, verdict | scan_image FK cascade |
| `classification_result` | model_version FK, latency_ms, temperature, raw entropy, ood_score | scan FK cascade; one per scan attempt (attempt_no) |
| `classification_candidate` | rank 1–5, food FK, calibrated_prob | result FK cascade; unique(result, rank) |
| `user_confirmation` | confirmed food FK, source (candidate\|search), at | scan FK cascade; unique(scan) |
| `user_correction` | target (classification\|ocr_field), field_ref, old_value, new_value, training_eligible bool (computed from consent at write time) | scan FK cascade |
| `ocr_result` | engine, engine_version, verbatim_text, completeness, section_map jsonb, pipeline_flags | scan FK cascade |
| `ocr_field` | section, field_name, value_text, value_num?, unit?, confidence, span (start,end), user_confirmed bool, flags[] | ocr_result FK cascade |
| `parsed_ingredient` | raw_text, span, order_idx, canonical ingredient FK?, parent FK (compound), alternative bool, qualifiers[], ocr_confidence | ocr_result FK cascade |
| `allergen_evidence` | profile_allergen ref (or allergen FK for non-profile "other declared"), **status_code (ALLERGEN_POLICY enum, NOT NULL)**, rule_id NOT NULL, source (ocr\|off\|class_hint), span?, source_record?, ontology_version NOT NULL | scan FK cascade — schema enforces "no status without evidence" |
| `serving_selection` | serving FK or custom grams, multiplier | scan FK cascade; unique(scan) |

## Food knowledge (C)

| Entity | Purpose / key fields | Relations & constraints |
|---|---|---|
| `food` | canonical_name, is_dish, fdc_id?, food101_class?, mapping_confidence?, default framing flags | unique(fdc_id), unique(food101_class) |
| `food_serving` | label, grams?, source (fdc_portion\|label\|curated) | food FK cascade |
| `nutrient` | canonical: fdc_nutrient_id, name, unit, display_rounding_rule, dv_value? | seed data |
| `nutrition_record` | basis (per_100g\|per_serving), source FK, source_ref (fdc id/barcode/ocr scan id), fetched_at, payload jsonb | food FK or product FK (XOR) |
| `nutrient_value` | value numeric, nutrient FK | record FK cascade; unique(record, nutrient) |
| `product` | barcode (GTIN-13 normalized, unique), name, brand FK?, off_last_modified, allergen_tags[], traces_tags[], ingredients_text, completeness flags | — |
| `brand` | name unique-ish (normalized) | — |
| `ingredient` | canonical_name unique, additive_code?, veg/vegan/gluten attrs (+rationale), notes | — |
| `ingredient_synonym` | form (unique per ingredient), type (exact\|abbrev\|misspell\|derived) | ingredient FK cascade |
| `allergen` | the 9 canonical + family members: code unique, family FK self-ref?, display_name | seed data |
| `allergen_term` | ontology rows: term, allergen FK, relation, confidence, provenance, version_tag | seed from ontology.yaml |
| `class_allergen_hint` | food101_class → allergen, prevalence_note, provenance | curated seed; drives S4 |
| `data_source` | fdc \| off \| user_ocr \| curated: name, attribution_text, license_note | seed |
| `external_cache` | (source, source_id) unique, payload jsonb, fetched_at, ttl | — |

## Assistant (P)

| Entity | Purpose / key fields | Relations |
|---|---|---|
| `assistant_thread` | one per scan | scan FK cascade (unique) |
| `assistant_message` | role, content, degraded bool, provider, model_name, prompt_version, token_counts | thread FK cascade |
| `message_citation` | message FK, kind (tool\|chunk), ref (tool name+call id \| chunk id) | cascade |
| `corpus_doc` | doc_id unique, title, category, source, license, reviewed_at, content_hash | C |
| `corpus_chunk` | doc FK, heading_path, content, embedding vector(384), embedding_model, content_hash | HNSW index (cosine); C |

## ML & ops (O)

| Entity | Purpose / key fields | Relations |
|---|---|---|
| `model_version` | name, version, wandb_artifact, onnx_sha256, thresholds (τ, τ_u), temperature, status (candidate\|staging\|production\|retired), promoted_at | registry mirror |
| `inference_event` | scan FK, model_version FK, latency_ms, top1_prob, ood_score — powers monitoring | index(model_version, created_at) |
| `experiment` | (optional mirror of W&B run metadata for admin UI) | — |
| `job` | queue table (ASYNC_JOB_DESIGN fields) | — |
| `audit_event` | actor (user/system/admin), action enum, target ref, metadata jsonb (redacted), at — **append-only** (no UPDATE/DELETE grants) | index(actor, at) |
| `feedback_event` | scan FK, kind (confirmation\|correction\|ui_feedback), payload, training_eligible | user FK |

## Tenant isolation & access rules

Single-tenant-per-user model: every P/H row reaches a `user_id` within one join;
repo layer applies user scoping universally; admin role has **no** endpoint that
returns H-class data (profiles/allergens) — admin sees aggregates only.

## Deletion semantics

- Scan delete: soft (`deleted_at`) → 7-day sweep hard-deletes scan graph + storage
  objects + thumbnails.
- Account delete: hard cascade across all P/H tables + storage + embeddings-free
  (no user embeddings exist by design) + `deletion_request` tombstone + audit
  summary. Verified by the deletion-sweep test (TEST_STRATEGY).

## Provenance invariants (schema-enforced)

`allergen_evidence.rule_id/ontology_version`, `nutrition_record.source/fetched_at`,
`classification_result.model_version`, `ocr_result.engine_version` are NOT NULL —
un-provenanced facts cannot be stored.
