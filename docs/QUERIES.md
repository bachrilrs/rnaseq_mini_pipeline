# Example SQL Queries

## Overview Queries

### Get all samples with their QC metrics

```sql
SELECT 
    s.sample_id,
    s.condition,
    s.replicate,
    qm.library_size,
    qm.mean_counts
FROM samples s
LEFT JOIN qc_metrics qm ON s.sample_id = qm.sample_id
ORDER BY s.condition, s.replicate;
```

### Summary statistics by condition

```sql
SELECT 
    s.condition,
    COUNT(DISTINCT s.sample_id) as sample_count,
    AVG(qm.library_size) as avg_library_size,
    STDDEV(qm.library_size) as stddev_library_size,
    MIN(qm.library_size) as min_library_size,
    MAX(qm.library_size) as max_library_size
FROM samples s
LEFT JOIN qc_metrics qm ON s.sample_id = qm.sample_id
GROUP BY s.condition
ORDER BY s.condition;
```

### Pipeline execution history

```sql
SELECT 
    id,
    version,
    dataset_source,
    timestamp,
    (SELECT COUNT(*) FROM qc_metrics WHERE run_id = runs.id) as metrics_count
FROM runs
ORDER BY timestamp DESC
LIMIT 10;
```

## Quality Metrics Queries

### High library size samples

```sql
SELECT 
    s.sample_id,
    s.condition,
    qm.library_size
FROM qc_metrics qm
JOIN samples s ON qm.sample_id = s.sample_id
WHERE qm.library_size > (
    SELECT AVG(library_size) + 2 * STDDEV(library_size)
    FROM qc_metrics
)
ORDER BY qm.library_size DESC;
```

### Outlier detection (IQR method)

```sql
WITH stats AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY library_size) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY library_size) as q3
    FROM qc_metrics
)
SELECT 
    s.sample_id,
    s.condition,
    qm.library_size,
    CASE 
        WHEN qm.library_size < stats.q1 - 1.5 * (stats.q3 - stats.q1) THEN 'Low'
        WHEN qm.library_size > stats.q3 + 1.5 * (stats.q3 - stats.q1) THEN 'High'
        ELSE 'Normal'
    END as outlier_status
FROM qc_metrics qm
JOIN samples s ON qm.sample_id = qm.sample_id
CROSS JOIN stats
WHERE qm.library_size < stats.q1 - 1.5 * (stats.q3 - stats.q1)
   OR qm.library_size > stats.q3 + 1.5 * (stats.q3 - stats.q1);
```

## Data Integrity Queries

### Check for duplicate samples

```sql
SELECT 
    sample_id,
    COUNT(*) as count
FROM samples
GROUP BY sample_id
HAVING COUNT(*) > 1;
```

### Samples without QC metrics

```sql
SELECT 
    s.sample_id,
    s.condition,
    s.replicate
FROM samples s
LEFT JOIN qc_metrics qm ON s.sample_id = qm.sample_id
WHERE qm.sample_id IS NULL;
```
