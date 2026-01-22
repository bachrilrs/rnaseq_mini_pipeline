CREATE TABLE IF NOT EXISTS samples (
    sample_id VARCHAR(100) PRIMARY KEY,
    condition VARCHAR(50),
    geo_accession VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS runs (
    run_id SERIAL PRIMARY KEY,
    run_name VARCHAR(50) NOT NULL,
    pipeline_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dataset_id VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS qc_metrics (
    run_id INTEGER REFERENCES runs(run_id),
    sample_id VARCHAR REFERENCES samples(sample_id),
    library_size BIGINT NOT NULL,
    zero_fraction NUMERIC(5,3) NOT NULL,
    expressed_genes INTEGER,
    PRIMARY KEY (run_id, sample_id),
    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
    FOREIGN KEY (sample_id) REFERENCES samples(sample_id) ON DELETE CASCADE
);