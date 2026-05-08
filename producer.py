"""
producer.py
-----------
Simulates real-time stock price data and sends it to AWS Kinesis Data Stream.
Run this locally after setting up your AWS credentials.

Install dependencies:
    pip install boto3

Usage:
    python producer.py
"""

import boto3
import json
import random
import time
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
STREAM_NAME = "stock-price-stream"   # Must match the Kinesis stream you create
REGION      = "ap-south-1"            # Change if you use a different region
STOCK_SYMBOL = "AAPL"
BASE_PRICE   = 175.0                 # Starting price
SEND_INTERVAL = 1                    # Seconds between records
# ─────────────────────────────────────────────────────────────────────────────

kinesis = boto3.client("kinesis", region_name=REGION)


def generate_price(prev_price: float) -> float:
    """Random walk with occasional spikes (to trigger anomaly detection)."""
    spike = random.random() < 0.05                      # 5% chance of spike
    change = random.uniform(-2, 2) if not spike else random.uniform(15, 25)
    return round(max(1.0, prev_price + change), 2)


def send_record(price: float, prev_price: float) -> None:
    record = {
        "symbol":    STOCK_SYMBOL,
        "price":     price,
        "change":    round(price - prev_price, 2),
        "timestamp": datetime.utcnow().isoformat(),
        "volume":    random.randint(100, 10000),
    }
    kinesis.put_record(
    StreamARN="arn:aws:kinesis:ap-south-1:546820406326:stream/stock-price-stream",
        Data=json.dumps(record),
        PartitionKey=STOCK_SYMBOL,      # Routes all AAPL records to same shard
    )
    print(f"[SENT] {record['timestamp']}  Price: ${price:>8.2f}  "
          f"Change: {record['change']:+.2f}")


def main():
    print(f"Starting producer → stream: {STREAM_NAME}  (Ctrl+C to stop)\n")
    price = BASE_PRICE
    while True:
        new_price = generate_price(price)
        send_record(new_price, price)
        price = new_price
        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main()
