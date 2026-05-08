"""
lambda_function.py
------------------
AWS Lambda consumer — triggered by Kinesis Data Stream.
Reads batches of stock records, detects anomalies using Z-score,
and writes processed results to S3 as JSON (partitioned by date).

Environment Variables to set in Lambda console:
    S3_BUCKET   → your-pipeline-bucket-name  (e.g. stock-pipeline-yourname)
    ZSCORE_THRESHOLD → 2.0  (flag if price change exceeds 2 std deviations)
"""

import json
import boto3
import base64
import os
import statistics
from datetime import datetime, timezone

s3 = boto3.client("s3")

S3_BUCKET        = os.environ.get("S3_BUCKET", "stock-pipeline-bucket")
ZSCORE_THRESHOLD = float(os.environ.get("ZSCORE_THRESHOLD", "2.0"))

# Rolling window kept in memory within a Lambda container (warm cache)
# For production, use DynamoDB or ElastiCache instead
_price_window: list[float] = []
WINDOW_SIZE = 20


def compute_zscore(value: float, window: list[float]) -> float | None:
    """Return Z-score of value relative to window, or None if window too small."""
    if len(window) < 5:
        return None
    mean  = statistics.mean(window)
    stdev = statistics.stdev(window)
    if stdev == 0:
        return 0.0
    return round((value - mean) / stdev, 3)


def decode_record(kinesis_record: dict) -> dict:
    """Base64-decode and parse a Kinesis record payload."""
    raw  = base64.b64decode(kinesis_record["kinesis"]["data"]).decode("utf-8")
    return json.loads(raw)


def build_s3_key(record: dict, anomaly: bool) -> str:
    """Partition S3 output by date and type for easy Athena querying."""
    ts   = datetime.fromisoformat(record["timestamp"])
    date = ts.strftime("%Y/%m/%d")
    label = "anomaly" if anomaly else "normal"
    return f"processed/{label}/{date}/{record['symbol']}_{ts.strftime('%H%M%S%f')}.json"


def lambda_handler(event, context):
    global _price_window

    processed, anomalies = 0, 0

    for kinesis_record in event["Records"]:
        try:
            record = decode_record(kinesis_record)
        except (KeyError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to decode record: {e}")
            continue

        price  = record["price"]
        zscore = compute_zscore(price, _price_window)

        # Update rolling window
        _price_window.append(price)
        if len(_price_window) > WINDOW_SIZE:
            _price_window.pop(0)

        is_anomaly = zscore is not None and abs(zscore) > ZSCORE_THRESHOLD

        # Build enriched output record
        output = {
            **record,
            "zscore":        zscore,
            "is_anomaly":    is_anomaly,
            "window_mean":   round(statistics.mean(_price_window), 2) if len(_price_window) >= 2 else None,
            "processed_at":  datetime.now(timezone.utc).isoformat(),
        }

        # Write to S3
        s3_key = build_s3_key(record, is_anomaly)
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=json.dumps(output),
            ContentType="application/json",
        )

        if is_anomaly:
            anomalies += 1
            print(f"[ANOMALY] {record['symbol']}  Price: ${price}  Z-score: {zscore}")
        else:
            print(f"[OK]      {record['symbol']}  Price: ${price}  Z-score: {zscore}")

        processed += 1

    print(f"\n✅ Batch complete — processed: {processed}, anomalies flagged: {anomalies}")
    return {"statusCode": 200, "processed": processed, "anomalies": anomalies}
