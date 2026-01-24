#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
USER=${POSTGRES_USER}
DB_NAME=${POSTGRES_DB}

echo "Connection to database $DB_NAME sur $DB_HOST:$DB_PORT..."

echo "Preprocessing data..."
Rscript r/clean_data.R

# Python pipeline execution
python -m rnaseq.pipeline --config /app/config.yaml

#  Dashboard KPIs

echo -e "DASHBOARD (KPIs)"

export PGPASSWORD=$POSTGRES_PASSWORD


echo -e "${GREEN}\n\n1. Top 5 samples by library size:${NC}"
# 
psql -h "$DB_HOST" -U "$USER" -d "$DB_NAME" -c "
SELECT (SELECT COUNT(*) FROM runs) as total_runs, (SELECT COUNT(*) FROM samples) as total_samples;"


echo -e "${GREEN}\n\n 2. Average library size by condition: ${NC}"

psql -h "$DB_HOST" -U "$USER" -d "$DB_NAME" -c " 
SELECT condition, COUNT(*), ROUND(AVG(library_size)::numeric, 0) as avg_lib FROM samples s 
JOIN qc_metrics q ON s.sample_id = q.sample_id GROUP BY condition;"

echo -e "\n\n"

echo -e " Interactive psql shell (\q to exit):"
psql -h "$DB_HOST" -U "$USER" -d "$DB_NAME"