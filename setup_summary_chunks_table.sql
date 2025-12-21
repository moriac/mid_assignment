-- SQL script to create the summary_chunks table in Supabase
-- Run this in your Supabase SQL Editor

-- Create the summary_chunks table
CREATE TABLE IF NOT EXISTS summary_chunks (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536)
);

-- Create an index for faster similarity searches
CREATE INDEX summary_chunks_embedding_idx 
ON summary_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION summary_chunks_search(
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
    FROM summary_chunks sc
    WHERE (filter = '{}' OR sc.metadata @> filter)
    ORDER BY sc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
