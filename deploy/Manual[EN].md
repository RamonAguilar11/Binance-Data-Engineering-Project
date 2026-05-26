# Deployment and Replicability Guide 🚀
**MarketMatrix — Serverless Data Engineering Pipeline**

This folder contains the step-by-step technical instructions to replicate and deploy the complete infrastructure of the **MarketMatrix** project within an AWS account, ensuring a seamless data lifecycle transition across the Bronze, Silver, and Gold layers of the architecture.

---

## 📋 Prerequisites

Before you begin, ensure you have the following:
- An active AWS Account with Administrator privileges or roles granting full permissions for S3, Lambda, EventBridge, Glue, and Athena.
- [Python 3.9+](https://www.python.org/) installed locally for baseline environment testing.
- A **Binance** account to retrieve API keys (public/private) or access to the Spot API public endpoints.
- The project repository cloned onto your local machine.

---

## 🛠️ Step 1: Storage Tier Configuration (Amazon S3)

The data pipeline implements a data lakehouse architecture pattern (**Medallion Architecture**). You must create a globally unique S3 bucket to host data across its distinct processing stages.

1. Navigate to the **Amazon S3** console and click **Create bucket**.
2. **Bucket name:** Choose a globally unique name conforming to your organization's naming standards.
   * *Security Note: Due to data privacy guidelines, do not include your AWS Account ID within the public resource name.*
3. **Region:** Select the closest geographical region (e.g., `us-east-1` or your assigned institutional region).
4. **Security Settings:** Ensure you check the box for **"Block Public Access" (Block all public access)** to protect underlying assets from unauthorized lookups.
5. Click **Create bucket**.
6. Inside the newly created bucket, generate the initial directory layout structure:
   - `1bronze/` *(For immutable, raw API data extraction payloads in CSV format)*
   - `2silver/` *(For clean, deduplicated, and cost-optimized data assets in Parquet format)*
   - `3gold/` *(For analytical business logic queries and Athena target output repositories)*

---

## ⚡ Step 2: Extraction Module Deployment (AWS Lambda)

The AWS Lambda function acts as the automated ingestion engine, orchestrating HTTP requests to the Binance API, parsing payloads, and storing objects inside the Bronze layer.

1. Open the **AWS Lambda** console and click **Create function**.
2. Select **Author from scratch**.
3. **Basic information:**
   * **Function name:** `marketmatrix-extractor-lambda`
   * **Runtime:** `Python 3.9` (or newer)
   * **Architecture:** `x86_64`
4. **Execution Role Permissions:**
   * Select *Create a new role with basic Lambda permissions*.
   * Once the Lambda function finishes initializing, go to the **Configuration** tab -> **Permissions**, and click the generated IAM Role link to launch the IAM Console.
   * Attach an Inline Policy granting explicit write permissions (`PutObject`) restricted exclusively to the S3 bucket created in Step 1.
5. **Code Upload:**
   * Copy the source code from your local ingestion script (`src/lambda/script_binance.py`) and paste it into the Lambda inline code editor.
   * *Ensure environmental variables are configured if utilizing API authorization signatures, or point directly to the public Spot API market data endpoint (`https://api.binance.com/api/v3/klines`).*
6. **Timeout Adjustments:**
   * Under **Configuration** -> **General configuration**, edit the default Timeout boundary from 3 seconds to **1 minute** to mitigate connection drops caused by external network API latency.

---

## ⏱️ Step 3: Pipeline Automation (AWS EventBridge)

To isolate and capture the official daily candlestick closure immediately after it occurs, a time-based event bridge trigger must be provisioned.

1. Open the **Amazon EventBridge** console and select **Rules** -> **Create rule**.
2. **Rule definition:**
   * **Name:** `marketmatrix-daily-trigger`
   * **Rule type:** `Schedule`
3. **Schedule Configuration:**
   * Select **A fine-grained schedule (cron expression)**.
   * **Cron Expression:** `cron(5 0 * * ? *)`
   * *Technical Explanation:* This expression fires the ingestion engine daily at 00:05 UTC (equivalent to 18:05 CDMX). This design ensures that the Binance trading engine has fully consolidated and finalized the previous daily block, removing intra-day price fluctuations from your dataset.
4. **Target Selection:**
   * Under **Target types**, select **AWS service**.
   * In the dropdown list, choose **Lambda function**.
   * Link your function: `marketmatrix-extractor-lambda`.
5. Review configurations and click **Create rule**.

---

## 🗄️ Step 4: Data Transformation (AWS Glue Job)

To completely mitigate infrastructure costs, **AWS Glue Crawlers are not utilized** in this project. Instead, schema definitions and table partitioning are managed directly via Spark processing and the Athena query engine.

1. Navigate to **AWS Glue** -> **ETL Jobs** -> **Script editor**.
2. Select **Spark script editor** to load your processing engine file (`src/glue/2silver_cleaning_data.py`).
3. Ensure the script maps out the following pipeline operations:
   * Read raw entries directly from the raw directory bucket path `s3://<YOUR-BUCKET-NAME>/1bronze/`.
   * Execute schema cleanup operations (deduplicate records, cast data types: `timestamp` to Date string formats, numerical metrics to `double`).
   * Output partitioned file structures matching Year/Month/Day keys into the destination path: `s3://<YOUR-BUCKET-NAME>/2silver/` using **Parquet** formatting.
4. **Save and Trigger:** Save the asset as `marketmatrix-silver-transformation-job`. 
   * *Architecture Note:* To optimize operational budgets, this job is intentionally executed manually or scheduled weekly to minimize runtime usage under the AWS Free Tier limitations.

---

## 🔍 Step 5: Analytical Engine and Manual Schema Mapping (Amazon Athena)

Amazon Athena acts as our serverless interactive query engine for the Gold Layer, evaluating SQL computations directly on top of partitioned columnar files at zero infrastructure maintenance costs.

1. Go to the **Amazon Athena** console.
2. **Initial Setup:** Before executing your baseline query payload, navigate to the **Settings** tab and configure a designated query output path directory in S3 (e.g., `s3://<YOUR-BUCKET-NAME>/3gold/query-results/`).
3. **Manual Table Schema Definition (Silver Layer):** * Execute the manual DDL DDL External Table script (`src/athena/athena_query.sql`) inside the Athena editor. This script explicitly creates the structural schema pointing to your S3 storage path: `s3://<YOUR-BUCKET-NAME>/2silver/`.
4. **Gold View Deployment:**
   * Copy and run the optimized SQL business rules script inside the query editor to build the analytical view that evaluates the core indicators: **RSI (14)**, **Bollinger Bands (20, 2)**, and **MACD (12, 26, 9)**.
   * The SQL conditional framework enforces the **Triple Confirmation Strategy** to yield automatic signals: `COMPRA FUERTE` (Strong Buy), `VENTA` (Sell), or `MANTENER` (Hold).

---

## 🧪 Step 6: End-to-End Pipeline Validation

To confirm that data moves securely through the entire data lakehouse architecture, perform the following validation protocol:

1. Open your AWS Lambda (`marketmatrix-extractor-lambda`) and trigger a manual execution invoke (**Test**).
2. Inspect the Amazon S3 console to ensure a new raw `.csv` file was stored within the path directory: `1bronze/year=2026/month=05/...`.
3. Run the AWS Glue Job to parse the new payload. Confirm that a compressed, optimized `.parquet` file appears inside the `2silver/` directory.
4. Open Amazon Athena, run a basic query: `SELECT * FROM marketmatrix_db.vista_capa_gold ORDER BY fecha DESC LIMIT 10;`, and verify that technical indicator evaluations map out instantaneously over your partition boundaries.

---
*Operational exceptions, throttling limits, or IAM access failures can be reviewed in real-time by inspecting the diagnostic logs generated automatically inside **Amazon CloudWatch**.*
