# RAG Architecture

## Role boundary (what RAG is NOT for)

Structured facts — nutrition numbers, allergen statuses, scan results, profiles —
are served by **deterministic tools over Postgres** (TOOL_ARCHITECTURE). Embedding
those and retrieving semantically would add fuzziness where SQL is exact.
RAG serves only **explanatory prose**: ingredient/additive definitions, allergen
education, dietary-guidance explainers, data-source documentation, app help.

## Knowledge sources (curated corpus)

All free/redistributable; each document registered with source, license, and
review date:
- Ingredient & additive explainers — written in-repo, informed by public references
  (curated by us; ~200–400 short docs over time).
- Allergen education — derived from FDA public-domain guidance (FALCPA/FASTER
  summaries, "may contain" meaning, cross-contact explanations).
- Nutrition education — FDA/USDA public-domain material (DV explanations, label
  reading guides, Dietary Guidelines excerpts).
- Data-source docs — how FDC/OFF work, what "typical values" means (our own docs).
- App help — our own product documentation.

Corpus lives in `data/corpus/**/*.md` with YAML frontmatter (id, title, category,
source, license, reviewed_at). PRs to corpus require source citation.

## Ingestion pipeline (async job)

parse frontmatter → chunk → embed → upsert to pgvector; idempotent by (doc_id,
content_hash); deletions tombstone chunks. Re-run on corpus change (CI-triggered).

- **Chunking:** heading-aware, target 300–500 tokens, 15% overlap; chunk keeps doc
  metadata + heading path (better citations).
- **Embedding model:** open sentence-transformers, served in-process —
  `BAAI/bge-small-en-v1.5` (384-d, MIT, strong MTEB for size, CPU-friendly).
  Alternative if quality insufficient on eval: `bge-base-en-v1.5` (768-d). Model
  name+version stored per chunk; re-embedding is a versioned migration.

## pgvector schema (summary; full DDL in DATA_MODEL)

`corpus_chunk(id, doc_id, heading_path, content, category, embedding vector(384),
embedding_model, content_hash, created_at)` — HNSW index (cosine). Scale is small
(thousands of chunks): free-tier Postgres handles it trivially.

## Retrieval

1. Query = user question (+ light scan-context expansion: confirmed food name,
   flagged allergens — from tools, not raw user text).
2. Filters: category allowlist by question type (help questions → help partition;
   ingredient questions → definitions) — metadata WHERE clause, then vector top-k
   (k=8) → **rerank** by cosine + keyword-overlap heuristic → top 3–4 passed to the
   LLM. (No cross-encoder reranker in MVP — measure first; slot exists.)
3. Similarity floor: below threshold → assistant says it has no good reference
   rather than stretching a weak chunk.

## Citation generation

Chunks passed with stable IDs; the model must attach `[n]` markers; the response
validator maps markers → chunk IDs → UI source chips (doc title + section). Uncited
retrieved-fact sentences fail validation (AI_EVALUATION citation tests).

## Freshness & access control

- Corpus versioned in git; `reviewed_at` surfaced in citations ("reviewed 2026-07").
- Corpus is public, non-personal content — no per-user ACLs needed; user/scan data
  never enters the corpus or the vector store (hard boundary; embeddings of user
  content would be a privacy leak vector).
- Scan-history semantic search (a possible future feature that WOULD embed user data)
  is explicitly out of scope; if ever built, it uses a separate, user-scoped
  vector namespace.

## Evaluation

Retrieval eval set: ~100 (question → expected doc/chunk) pairs built while curating
the corpus. Metrics: recall@4, MRR. Run on every embedding-model or chunking change.
End-to-end citation correctness covered by AI_EVALUATION.
