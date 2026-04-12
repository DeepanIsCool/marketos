DROP INDEX IF EXISTS idx_episodic_embedding;
DROP INDEX IF EXISTS idx_semantic_embedding;

CREATE INDEX idx_episodic_embedding
    ON agent_episodic_memory USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_semantic_embedding
    ON agent_semantic_memory USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
