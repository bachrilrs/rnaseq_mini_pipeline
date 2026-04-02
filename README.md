# RNA-seq Automated QC Pipeline

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

## Project Overview

This project is an industrialized **ETL (Extract, Transform, Load) pipeline** dedicated to quality control (QC) of RNA-seq sequencing data. Using the public dataset **GSE60450**, the pipeline automates the ingestion of raw data, validates it, and stores it in a relational database.

The objective is to demonstrate mastery of service orchestration (Docker Compose), Python development for data processing, and automation of complex workflows (DevOps/Data Engineering).

---

## Architecture & Features

* **Multi-Service Orchestration** : Docker Compose isolates the Python application from the PostgreSQL server.
* **Zero-Friction Automation** : An intelligent launch script (`run_project.sh`) manages environment variables and deployment.
* **Robust Synchronization** : The entrypoint uses network sockets to ensure PostgreSQL is ready before data insertion.
* **ETL Pipeline** :
  * **Extract** : Ingest TSV files via Pandas.
  * **Transform** : Clean GEO metadata, validate data types, and compute quality metrics.
  * **Load** : Secure insertion via `psycopg2` with atomic transaction handling.
* **Observability** : Automatic **KPI Dashboard** displayed in SQL format at the end of processing.

---

## Data Model (SQL)

The database is structured to ensure complete traceability of analyses:

* **`runs`** : Pipeline execution history (code version, source dataset, timestamp).
* **`samples`** : Sample registry (Biological conditions, GEO Accession).
* **`qc_metrics`** : Technical metrics (Library Size, Mean Counts) linked to a sample and pipeline run.

---

## Installation & Launch (One-Click)

The project is designed to be tested with a single command. Only Docker is required.

### Clone the Repository

```bash
git clone https://github.com/bachrilrs/rnaseq_mini_pipeline.git
cd rnaseq_mini_pipeline
```

### Launch the Pipeline

```bash
chmod +x run_project.sh
./run_project.sh
```

**Note** : On Linux/macOS, ensure Docker Desktop is running before executing the script.

This will:

* Build Docker images

* Start services

* Run the ETL pipeline

* Display a SQL dashboard with KPIs

* Open an interactive PostgreSQL console

---

## KPI Dashboard

At the end of execution, a statistical summary automatically displays in your terminal:

* Total number of runs and samples processed

* Average library size per biological condition (Virgin vs Lactation)


Example output:

```
=== Pipeline Complete ===

1. Pipeline Summary:
 total_runs | total_samples | qc_metrics
------------+---------------+----------
     1      |      12       |    12

2. Average library size by condition:
   condition  | count | avg_reads
--------------+-------+----------
  lactation   |   6   | 2500000
  virgin      |   6   | 2300000
```

---

## Interactive Console

The `run_project.sh` script leaves you at an interactive PostgreSQL console at the end of the process. You can test your own queries immediately:

```sql
-- Example: Check the first 5 samples
SELECT * FROM samples LIMIT 5;

-- Check all conditions
SELECT DISTINCT condition FROM samples;

-- Exit the console
\q
```

### Database Connection Details

If you want to connect manually after the pipeline finishes:

```bash
# From the interactive bash shell:
psql -h db -U rnaseq_user -d rnaseq_db

# Password: rnaseq_password
```

---

## SQL Injection Prevention

When inserting data into PostgreSQL, the pipeline uses parameterized queries with `psycopg2` to prevent SQL injection risks.

Instead of concatenating strings, the code uses placeholders `%s`:

```python
insert_query = """INSERT INTO samples (sample_name, condition, replicate)
VALUES (%s, %s, %s)"""
cursor.execute(insert_query, (sample_name, condition, replicate))
```

This ensures data is safely escaped and prevents malicious SQL execution.

---

## Tech Stack

* **Language** : Python 3.11 (Pandas, SQLAlchemy, PyYAML)

* **Database** : PostgreSQL 16

* **Infrastructure** : Docker, Docker Compose

* **R Preprocessing** : R 4.5.0 (edgeR, ggplot2)




---

## Troubleshooting

### Docker not running

Ensure Docker Desktop is launched before executing `run_project.sh`.

### Database connection timeout

Wait 10-15 seconds for PostgreSQL to initialize. The script includes automatic retry logic.

### Permission denied on `run_project.sh`

Run: `chmod +x run_project.sh`

---

## Contact

* **LinkedIn** : [Laroussi Bachri](https://www.linkedin.com/in/laroussi*bachri)

* **GitHub** : [bachrilrs](https://github.com/bachrilrs)
