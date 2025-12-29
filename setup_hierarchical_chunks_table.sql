-- SQL script to create the hierarchical_chunks table for LlamaIndex AutoMergingRetriever
-- Run this in your Supabase SQL Editor before using the hierarchical retriever

-- Enable the pgvector extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop the table if it exists (to recreate with correct schema)
DROP TABLE IF EXISTS hierarchical_chunks;

-- Create the hierarchical_chunks table
-- This table stores the leaf nodes from the HierarchicalNodeParser
CREATE TABLE hierarchical_chunks (
    id BIGSERIAL PRIMARY KEY,
    node_id TEXT UNIQUE NOT NULL,  -- LlamaIndex node ID
    text TEXT NOT NULL,             -- Node content
    metadata JSONB,                 -- Node metadata
    embedding VECTOR(1536)          -- OpenAI text-embedding-3-small produces 1536-dimensional vectors
);

-- Create an index for faster similarity searches using cosine distance
CREATE INDEX hierarchical_chunks_embedding_idx 
ON hierarchical_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create an index on node_id for faster lookups
CREATE INDEX hierarchical_chunks_node_id_idx 
ON hierarchical_chunks (node_id);

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION hierarchical_chunks_search(
    query_embedding VECTOR(1536),
    match_count INT DEFAULT 6,
    filter JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id BIGINT,
    node_id TEXT,
    text TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        hc.id,
        hc.node_id,
        hc.text,
        hc.metadata,
        1 - (hc.embedding <=> query_embedding) AS similarity
    FROM hierarchical_chunks hc
    WHERE (filter = '{}' OR hc.metadata @> filter)
    ORDER BY hc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Optional: Create a function to get statistics about the stored chunks
CREATE OR REPLACE FUNCTION get_hierarchical_chunks_stats()
RETURNS TABLE (
    total_chunks BIGINT,
    avg_text_length FLOAT,
    total_size_mb FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_chunks,
        AVG(LENGTH(text))::FLOAT AS avg_text_length,
        (pg_total_relation_size('hierarchical_chunks') / 1024.0 / 1024.0)::FLOAT AS total_size_mb
    FROM hierarchical_chunks;
END;
$$;

-- Grant necessary permissions (adjust as needed for your security requirements)
-- Uncomment the following lines if you want to enable Row Level Security
-- ALTER TABLE hierarchical_chunks ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow authenticated users to read
-- CREATE POLICY "Allow authenticated read access" ON hierarchical_chunks
--     FOR SELECT
--     TO authenticated
--     USING (true);

-- Create a policy to allow service role to do everything
-- CREATE POLICY "Allow service role full access" ON hierarchical_chunks
--     FOR ALL
--     TO service_role
--     USING (true);

COMMENT ON TABLE hierarchical_chunks IS 'Stores leaf nodes from LlamaIndex HierarchicalNodeParser for AutoMergingRetriever';
COMMENT ON COLUMN hierarchical_chunks.node_id IS 'Unique identifier from LlamaIndex node';
COMMENT ON COLUMN hierarchical_chunks.text IS 'Text content of the leaf node';
COMMENT ON COLUMN hierarchical_chunks.metadata IS 'Additional metadata in JSON format';
COMMENT ON COLUMN hierarchical_chunks.embedding IS 'Vector embedding for semantic search';
