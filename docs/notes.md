# QC PCA produced using sklearn; a pedagogical PCA implementation is included for transparency

Schéma minimal (suffisant et très pro)

samples

- sample_id (PK)
- condition
- replicate
- geo_accession (optionnel)

runs

- run_id (PK)
- run_name
- pipeline_version
- timestamp
- config_hash (optionnel mais stylé)
- dataset_id / series (optionnel)

qc_metrics

- run_id (FK -> runs)
- sample_id (FK -> samples)
- library_size
- zero_fraction
- expressed_gene
- (PK composite : run_id + sample_id)


Why use %s? You should never put your data directly into a SQL string (e.g., INSERT INTO table VALUES (102, 'Sample_A')). This is a security risk called SQL Injection. By using %s, you are sending a "template" to the database, and psycopg2 safely plugs the real data in for you.
