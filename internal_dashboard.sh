#!/bin/bash


echo -e "\n--- DASHBOARD AUTOMATIQUE (KPIs) ---"

# Exécution des KPIs via psql
docker exec -t rnaseq_db psql -U rnaseq_user -d rnaseq_db -c "
echo '--- RÉSUMÉ GLOBAL ---'
SELECT 
    (SELECT COUNT(*) FROM runs) as total_runs,
    (SELECT COUNT(*) FROM samples) as total_samples,
    (SELECT COUNT(*) FROM qc_metrics) as total_qc_records;

echo '--- ANALYSE PAR CONDITION BIOLOGIQUE ---'
SELECT 
    condition, 
    COUNT(*) as n_samples,
    ROUND(AVG(qc.library_size)::numeric, 2) as avg_lib_size
FROM samples s
JOIN qc_metrics qc ON s.sample_id = qc.sample_id
GROUP BY condition;

echo '--- DERNIER RUN EXÉCUTÉ ---'
SELECT 
    run_id, 
    run_name, 
    pipeline_version, 
    created_at 
FROM runs 
ORDER BY created_at DESC 
LIMIT 1;
"

echo -e "${GREEN}Dashboard généré avec succès à $(date)${NC}"