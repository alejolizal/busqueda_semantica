-- Script SQL para recrear el schema de la base de datos en cualquier PostgreSQL con pgvector.
-- Uso:
--   psql -U semantic_user -d semantic_search -f scripts/db_schema.sql
-- O ejecutar manualmente las sentencias en tu cliente SQL favorito.

-- 1. Crear extensión pgvector (requiere que la extensión esté instalada en el servidor)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Crear tabla de documentos
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536)
);

-- 3. Crear índice IVFFlat para búsqueda por similitud coseno
CREATE INDEX IF NOT EXISTS idx_documents_embedding
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
