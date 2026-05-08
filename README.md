# 📊 Real-Time Stock Data Pipeline with Anomaly Detection
> AWS | Kinesis · Lambda · S3 · Athena | Python

A serverless, real-time data pipeline that ingests simulated stock prices,
detects anomalies using Z-score statistics, and stores results in a queryable
data lake on S3.

---

## 🏗️ Architecture

```
producer.py  →  Kinesis Data Stream  →  Lambda Function  →  S3 Bucket
(local Python)    (real-time buffer)     (anomaly detect)    (data lake)
                                                                  ↓
                                                              Athena SQL
```

---

## 🛠️ AWS Services Used

| Service | Purpose |
|---|---|
| **Kinesis Data Streams** | Real-time data ingestion |
| **AWS Lambda** | Serverless stream processing |
| **S3** | Scalable data lake storage |
| **Athena** | Serverless SQL queries on S3 |
| **IAM** | Secure access management |

---

## 🚀 Setup Guide (Step-by-Step)

### Prerequisites
- AWS account (Free Tier is enough)
- AWS CLI installed and configured (`aws configure`)
- Python 3.9+

```bash
pip install boto3
```

---

### Step 1 — Create an S3 Bucket

1. Go to **AWS Console → S3 → Create Bucket**
2. Name it something unique: `stock-pipeline-yourname`
3. Region: `us-east-1`
4. Leave all other settings as default → **Create bucket**

---

### Step 2 — Create a Kinesis Data Stream

1. Go to **AWS Console → Kinesis → Create data stream**
2. Stream name: `stock-price-stream`
3. Capacity: **On-demand** (free tier friendly)
4. Click **Create data stream**

---

### Step 3 — Create the Lambda Function

1. Go to **AWS Console → Lambda → Create function**
2. Choose **Author from scratch**
   - Name: `StockAnomalyDetector`
   - Runtime: `Python 3.12`
3. Click **Create function**
4. In the **Code** tab, paste the contents of `lambda_function.py`
5. Click **Deploy**

#### Add Environment Variables (Lambda → Configuration → Environment variables)
| Key | Value |
|---|---|
| `S3_BUCKET` | `stock-pipeline-yourname` |
| `ZSCORE_THRESHOLD` | `2.0` |

#### Add IAM Permissions (Lambda → Configuration → Permissions → Role)
Click the execution role → Add these policies:
- `AmazonS3FullAccess`
- `AmazonKinesisReadOnlyAccess`

---

### Step 4 — Connect Lambda to Kinesis

1. In your Lambda function → **Add trigger**
2. Select **Kinesis**
3. Choose stream: `stock-price-stream`
4. Batch size: `10`
5. Starting position: **Trim horizon**
6. Click **Add**

---

### Step 5 — Run the Producer

```bash
python producer.py
```

You should see output like:
```
[SENT] 2024-01-15T10:23:01  Price: $  175.32  Change: +0.32
[SENT] 2024-01-15T10:23:02  Price: $  173.81  Change: -1.51
[SENT] 2024-01-15T10:23:03  Price: $  191.44  Change: +17.63  ← will trigger anomaly
```

Let it run for **5–10 minutes** to accumulate data.

---

### Step 6 — Verify in S3

Go to your S3 bucket. You should see:
```
processed/
  normal/2024/01/15/AAPL_102301000000.json
  anomaly/2024/01/15/AAPL_102303000000.json
```

---

### Step 7 — Query with Athena

1. Go to **AWS Console → Athena → Query editor**
2. Set up a query result location (S3 bucket subfolder: `s3://stock-pipeline-yourname/athena-results/`)
3. Run the queries in `athena_queries.sql` in order

---

## 📈 Sample Results

```sql
SELECT symbol, COUNT(*) as total, 
       SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomalies
FROM stock_prices GROUP BY symbol;
```

```
symbol | total | anomalies
-------+-------+----------
AAPL   |  312  |    18
```

---

## 🧠 How Anomaly Detection Works

The Lambda function maintains a **rolling window** of the last 20 price values.
For each new record it computes the **Z-score**:

```
Z = (price - mean) / std_deviation
```

If `|Z| > 2.0` → flagged as an anomaly (price is 2+ standard deviations from recent average).

---

## 💰 Cost Estimate

| Service | Free Tier | This Project Usage |
|---|---|---|
| Kinesis | 1M records/month | ~10K records |
| Lambda | 1M requests/month | ~1K invocations |
| S3 | 5 GB storage | < 10 MB |
| Athena | $5/TB scanned | ~$0.00 |
| **Total** | | **~$0** |

---

## 🔮 Extensions (for a stronger resume)

- Add **SNS alerts** when anomalies are detected (email notification)
- Replace Z-score with **Isolation Forest** (scikit-learn in Lambda Layer)
- Add a **QuickSight dashboard** for live visualization
- Stream multiple stock symbols using multiple Kinesis shards
- Use **AWS Glue Crawler** to auto-discover S3 schema for Athena

---

## 📁 Project Structure

```
├── producer.py          # Local script: generates & streams stock data
├── lambda_function.py   # AWS Lambda: processes stream, detects anomalies
├── athena_queries.sql   # SQL queries to analyze results in Athena
└── README.md
```

---

## 🏷️ Resume Bullet

> *Built a serverless real-time data pipeline on AWS (Kinesis, Lambda, S3, Athena) to ingest and process streaming time-series data with statistical anomaly detection; identified price spikes using Z-score on a rolling window with ~5% anomaly rate.*
