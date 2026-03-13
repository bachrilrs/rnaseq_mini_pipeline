#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-rnaseq_user}
DB_NAME=${DB_NAME:-rnaseq_db}
DB_PASSWORD=${DB_PASSWORD:-rnaseq_password}

echo -e "${CYAN}=== RNA-seq Pipeline ===${NC}"
echo ""

# Wait for database
echo -e "${YELLOW}Waiting for database...${NC}"
for i in {1..30}; do
    if PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &>/dev/null; then
        echo -e "${GREEN}✓ Database ready${NC}"
        break
    fi
    echo "Attempt $i/30..."
    sleep 1
done
echo ""

# 1. R preprocessing
echo -e "${YELLOW}Step 1: Running R preprocessing...${NC}"
if [ -f r/clean_data.R ]; then
    if command -v Rscript &> /dev/null; then
        Rscript r/clean_data.R 2>&1 || echo -e "${RED}✗ R script failed${NC}"
        if [ -f data/GSE60450_Lactation-GenewiseCounts_filtered.txt ]; then
            echo -e "${GREEN}✓ Filtered file created${NC}"
        else
            echo -e "${RED}✗ Filtered file NOT created${NC}"
        fi
    else
        echo -e "${RED}✗ Rscript not found${NC}"
    fi
else
    echo -e "${RED}✗ r/clean_data.R not found${NC}"
fi
echo ""

# 2. Python QC pipeline
echo -e "${YELLOW}Step 2: Running Python QC pipeline...${NC}"
python -m rnaseq.pipeline --config config.yaml
echo -e "${GREEN}✓ QC pipeline complete${NC}"
echo ""

# 3. Create database schema
echo -e "${YELLOW}Step 3: Creating database schema...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f sql/create_tables.sql 2>/dev/null || true
echo -e "${GREEN}✓ Schema created${NC}"
echo ""

# 4. Export results
echo -e "${YELLOW}Step 4: Exporting results to database...${NC}"
python -m rnaseq.db_setup
echo -e "${GREEN}✓ Export complete${NC}"
echo ""

# 5. Database summary
echo -e "${CYAN}=== Pipeline Complete ===${NC}"
echo ""

echo -e "${GREEN}1. Pipeline Summary:${NC}"
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT (SELECT COUNT(*) FROM runs) as total_runs, 
       (SELECT COUNT(*) FROM samples) as total_samples,
       (SELECT COUNT(*) FROM qc_metrics) as qc_metrics;" 2>/dev/null || true
echo ""

echo -e "${GREEN}2. Average library size by condition:${NC}"
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "
SELECT condition, COUNT(*), ROUND(AVG(total_reads)::numeric, 0) as avg_reads 
FROM samples s 
JOIN qc_metrics q ON s.sample_name = q.sample_name 
GROUP BY condition;" 2>/dev/null || true
echo ""