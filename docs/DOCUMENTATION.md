# API Documentation

## Overview

This document describes the public API of the RNA-seq Mini Pipeline.

## Modules

### `src.rnaseq.db_setup`

Database connection and operations management.

### `src.rnaseq.io_setup`

Input/output and file operations.

### `src.rnaseq.validation`

Data validation and quality checks.

### `src.rnaseq.qc`

Quality control metrics calculation.

### `src.rnaseq.pipeline`

Main ETL pipeline orchestration.

### `src.rnaseq.pca`

Principal Component Analysis for dimensionality reduction.

## Configuration

Use `config.yaml` to configure:

- Database connection (host, user, password, database, port)
- Pipeline settings (dataset_id, data_dir, output_dir, batch_size)
- Logging configuration

Environment variables can override config.yaml:

- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`
- `DATASET_ID`, `DATA_DIR`, `OUTPUT_DIR`, `BATCH_SIZE`

## Usage Examples

### Running the pipeline

```bash
python -m src.rnaseq.pipeline
```

### Using Docker

```bash
docker-compose up
```

### Running tests

```bash
pytest tests/ -v --cov=src
```

### Launching dashboard

```bash
streamlit run dashboard.py
```
