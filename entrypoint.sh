#!/bin/bash
set -e

DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
USER=${POSTGRES_USER}
DB_NAME=${POSTGRES_DB}

echo "Connexion a la base de donnees $DB_NAME sur $DB_HOST:$DB_PORT..."

# 1. Lancer le pipeline Python
python -m rnaseq.pipeline --config /app/config.yaml

# 2. Dashboard KPIs
echo -e "\n--------------------------------------------------------"
echo -e "DASHBOARD DES RESULTATS (KPIs)"
echo -e "--------------------------------------------------------"
export PGPASSWORD=$POSTGRES_PASSWORD

# On utilise explicitement les variables pour psql
psql -h "$DB_HOST" -U "$USER" -d "$DB_NAME" -c "
SELECT (SELECT COUNT(*) FROM runs) as total_runs, (SELECT COUNT(*) FROM samples) as total_samples;
SELECT condition, COUNT(*), ROUND(AVG(library_size)::numeric, 0) as avg_lib FROM samples s 
JOIN qc_metrics q ON s.sample_id = q.sample_id GROUP BY condition;"

# 3. Mode interactif
echo -e "\nOuverture de la console interactive SQL \q "
psql -h "$DB_HOST" -U "$USER" -d "$DB_NAME"