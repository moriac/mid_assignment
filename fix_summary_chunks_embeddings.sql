-- Fix embeddings in summary_chunks table
-- Run this in your Supabase SQL Editor

-- This SQL converts string-stored embeddings to proper VECTOR type
-- by re-casting them with the ::vector type

-- Step 1: Check current state
SELECT 
    id,
    pg_typeof(embedding) as current_type,
    length(embedding::text) as text_length
FROM summary_chunks
LIMIT 3;

-- Step 2: Fix the embeddings by updating with proper vector casting
-- This creates a temporary column, copies data with proper casting, then swaps

-- Add a temporary column
ALTER TABLE summary_chunks ADD COLUMN IF NOT EXISTS embedding_temp VECTOR(1536);

-- Copy embeddings with proper vector casting
UPDATE summary_chunks
SET embedding_temp = embedding::text::vector
WHERE embedding IS NOT NULL;

-- Drop the old column and rename temp column
ALTER TABLE summary_chunks DROP COLUMN embedding;
ALTER TABLE summary_chunks RENAME COLUMN embedding_temp TO embedding;

-- Recreate the index
DROP INDEX IF EXISTS summary_chunks_embedding_idx;
CREATE INDEX summary_chunks_embedding_idx 
ON summary_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Step 3: Verify the fix
SELECT 
    id,
    pg_typeof(embedding) as type_after_fix,
    embedding <-> '[0,0,0,0,0,0,0,0,0,0]'::vector as test_distance
FROM summary_chunks
WHERE embedding IS NOT NULL
LIMIT 3;

-- Step 4: Test the search function
SELECT 
    id,
    content,
    similarity
FROM summary_chunks_search(
    '[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'::vector(1536),
    3
)
LIMIT 3;
