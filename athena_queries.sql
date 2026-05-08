-- ============================================================
-- athena_queries.sql
-- Run these in AWS Athena after your pipeline has written data
-- ============================================================

-- STEP 1: Create external table pointing at your S3 processed data
-- Replace 'your-pipeline-bucket-name' with your actual bucket

CREATE EXTERNAL TABLE IF NOT EXISTS stock_prices (
    symbol      STRING,
    price       DOUBLE,
    change      DOUBLE,
    timestamp   STRING,
    volume      INT,
    zscore      DOUBLE,
    is_anomaly  BOOLEAN,
    window_mean DOUBLE,
    processed_at STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://your-pipeline-bucket-name/processed/'
TBLPROPERTIES ('has_encrypted_data'='false');


-- ============================================================
-- STEP 2: Explore your data
-- ============================================================

-- All records
SELECT * FROM stock_prices
ORDER BY timestamp DESC
LIMIT 50;


-- All detected anomalies
SELECT symbol, price, zscore, timestamp
FROM stock_prices
WHERE is_anomaly = true
ORDER BY ABS(zscore) DESC;


-- Price statistics summary
SELECT
    symbol,
    COUNT(*)                        AS total_records,
    ROUND(AVG(price), 2)            AS avg_price,
    ROUND(MIN(price), 2)            AS min_price,
    ROUND(MAX(price), 2)            AS max_price,
    ROUND(STDDEV_SAMP(price), 2)    AS price_stddev,
    SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) AS anomaly_count
FROM stock_prices
GROUP BY symbol;


-- Anomaly rate over time (by minute)
SELECT
    DATE_TRUNC('minute', CAST(timestamp AS TIMESTAMP)) AS minute,
    COUNT(*) AS total,
    SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) AS anomalies,
    ROUND(
        100.0 * SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS anomaly_pct
FROM stock_prices
GROUP BY 1
ORDER BY 1;


-- Top 10 largest price spikes
SELECT symbol, price, change, zscore, timestamp
FROM stock_prices
WHERE is_anomaly = true
ORDER BY ABS(change) DESC
LIMIT 10;
