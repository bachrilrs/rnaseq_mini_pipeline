# Architecture Overview

## System Design

Input Data Files (TSV/CSV)
          ↓
    Extract Phase
    (io_setup.py)
          ↓
  Transform Phase
  (validation.py)
          ↓
   QC Metrics
    (qc.py)
          ↓
    Load Phase
   (db_setup.py)
          ↓
   PostgreSQL DB
    ├── runs
    ├── samples
    └── qc_metrics
          ↓
    Reporting
    ├���─ JSON Report
    ├── HTML Report
    └── Dashboard

## Module Dependencies

pipeline.py (Orchestrator)
    ├── db_setup.py (Database)
    ├── io_setup.py (I/O)
    ├── validation.py (Validation)
    └── qc.py (QC Metrics)

## Key Features

1. **Modular Design**: Each component handles a specific concern
2. **Comprehensive Testing**: Unit tests for all modules
3. **Configuration Management**: YAML-based with env overrides
4. **Error Handling**: Try-catch with logging at each stage
5. **Database Transactions**: Safe atomic operations
6. **Logging**: Detailed logging at INFO and DEBUG levels
7. **Docker Support**: Full Docker and Docker Compose setup
8. **Dashboard**: Interactive Streamlit visualization

## Data Flow

1. Extract → Read raw TSV files
2. Transform → Clean and validate data
3. QC → Calculate quality metrics
4. Load → Insert into PostgreSQL
5. Report → Generate reports and visualizations