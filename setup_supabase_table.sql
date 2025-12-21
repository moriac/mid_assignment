-- SQL script to create the small_chunks table in Supabase
-- Run this in your Supabase SQL Editor before running the Python script

-- Enable the pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop the table if it exists (to recreate with correct schema)
DROP TABLE IF EXISTS small_chunks;

-- Create the small_chunks table
CREATE TABLE small_chunks (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536)  -- OpenAI text-embedding-3-small produces 1536-dimensional vectors
);

-- Create an index for faster similarity searches
CREATE INDEX small_chunks_embedding_idx 
ON small_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION small_chunks_search(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sc.id,
        sc.content,
        sc.metadata,
        1 - (sc.embedding <=> query_embedding) AS similarity
    FROM small_chunks sc
    WHERE (filter = '{}' OR sc.metadata @> filter)
    ORDER BY sc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant necessary permissions (adjust as needed for your security requirements)
-- ALTER TABLE small_chunks ENABLE ROW LEVEL SECURITY;
