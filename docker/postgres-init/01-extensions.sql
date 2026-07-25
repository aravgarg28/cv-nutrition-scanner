-- Enable pgvector at database creation (used by the RAG corpus store; see
-- docs/architecture/DATA_MODEL.md). Idempotent.
CREATE EXTENSION IF NOT EXISTS vector;
