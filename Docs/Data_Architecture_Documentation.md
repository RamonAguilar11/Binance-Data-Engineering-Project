# Data Architecture Documentation: Data Lakehouse Implementation
**Project:** MarketMatrix (Serverless Financial Data Pipeline)

---

## 1. Executive Summary
This document outlines the technical architecture of the data system designed and implemented for the **MarketMatrix** project. The primary objective of this system is to automate a fully serverless data pipeline for daily Bitcoin (BTC) market data. This encompasses the automated ingestion of definitive daily closing prices from global exchanges, multi-stage transformation, and high-performance technical analysis. The end-to-end system evaluates technical indicators under a strict triple-confirmation logic to generate algorithmic trading signals and optimize data-driven financial decision-making.

---

## 2. Technical Architecture (Conceptual Overview)
The solution is built upon a **Medallion Architecture (Bronze, Silver, Gold)** leveraging fully managed, serverless cloud services provided by **Amazon Web Services (AWS)**. This design decouples storage from compute layers, drastically minimizes operational overhead, and ensures high availability, automatic scaling, and optimal cost-efficiency without requiring infrastructure provisioning.

---

## 3. Technology Stack
* **Data Source:** Binance API (Daily Klines / Candlestick data).
* **Ingestion & Orchestration:** AWS EventBridge and AWS Lambda.
* **Data Lake Storage:** Amazon S3 (Simple Storage Service).
* **Big Data Processing:** AWS Glue Jobs (Serverless managed PySpark environment).
* **Data Cataloging:** AWS Glue Data Catalog.
* **Analytics & Consumption Layer:** Amazon Athena (Serverless interactive SQL query engine).

---

## 4. Layer Descriptions (Medallion Architecture)

| Layer | Process Description | Technology Stack |
| :--- | :--- | :--- |
| **Bronze (Raw)** | Stores immutable, raw Bitcoin daily closing price data exactly as extracted from the source API. Retained in plaintext format for auditability and recovery. | Amazon S3, AWS Lambda, AWS EventBridge |
| **Silver (Trusted)** | Cleaned, deduplicated, and schema-validated data. Converted into an efficient columnar format to minimize storage costs and optimize query execution speed. | Amazon S3, AWS Glue Job (PySpark) |
| **Gold (Refined)** | Aggregated and enriched financial datasets. Implements complex mathematical formulations for technical indicators (RSI, MACD, and Bollinger Bands) ready for consumption. | Amazon S3, Amazon Athena, AWS Glue Data Catalog |

---

## 5. Data Flow & Pipeline Mechanics

1. **Trigger & Ingestion (Bronze Layer):** Daily at 00:05 UTC (18:05 Mexico City Time / CDMX), a time-based cron schedule in **AWS EventBridge** triggers an **AWS Lambda** function. The Lambda function establishes a secure connection with the Binance API, retrieves the definitive closing price for the preceding daily candle, and persists the data as a **CSV** file within the designated **S3 Bronze** bucket.
2. **Transformation & Cost Optimization (Silver Layer):** An **AWS Glue Job** executing a **PySpark** script is orchestrated to ingest raw files from the Bronze layer. The script performs key data-cleansing operations: it eliminates duplicate records, standardizes cryptographic timestamps, enforces strict schemas, and writes the output into the **S3 Silver** bucket using **Apache Parquet**. This columnar migration significantly reduces analytical scanning fees.
3. **Analytics & Algorithmic Evaluation (Gold Layer):** The structured Parquet files are schema-mapped inside the **AWS Glue Data Catalog**. **Amazon Athena** executes optimized SQL queries directly over the Parquet files to calculate the core **Triple-Confirmation Trading Strategy**:
    * **Relative Strength Index - RSI (14):** Identifies critical price extremes, locating oversold ($\le 30$) or overbought ($\ge 70$) boundaries.
    * **Bollinger Bands (20, 2):** Computes price volatility using standard deviations to monitor price action bouncing off the Lower Band or testing the Upper Band.
    * **Moving Average Convergence Divergence - MACD (12, 26, 9):** Validates precise momentum shifts via directional crossovers between the MACD Line and the Signal Line.
4. **Signal Generation Logic:** The Athena processing engine evaluates all three mathematical conditions concurrently. A trading signal is dispatched only if all three distinct criteria are met in unison (**STRONG BUY** or **PARTIAL/TOTAL SELL**). If any condition fails to align, the pipeline defaults to a **HOLD / LIQUIDITY** state, protecting the portfolio from premature breakouts or "falling knives."

---

## 6. Security Framework & Operations Log

### Infrastructure Security & Identity Management
* **Principle of Least Privilege:** All cross-service interactions within the AWS perimeter are strictly governed by granular **AWS IAM (Identity and Access Management)** roles. The ingestion Lambda function is heavily restricted to write-only operations inside S3 Bronze, while the Glue PySpark environment and Athena queries utilize minimal, read/write permissions scoped strictly to their relevant data lakes and catalogs.

### Stabilization & Operational Log (May 2026)
As a core component of the software development lifecycle (SDLC) and continuous validation of the engineering pipeline, the following operational events were recorded:
* **May 5:** Production Bug Fix. Resolved a timezone misalignment within the scheduling trigger by calibrating the EventBridge expression to `cron(5 0 * * ? *)`. This modification successfully captured the exact closing figures from Binance.
* **May 11 – May 17:** Closed-Loop Trade Cycle. The pipeline generated a validated *Strong Buy* trigger at ~\$63,890. On May 16, as price extended to ~\$67,280, testing the upper Bollinger Band alongside an RSI > 70, the system executed a mandatory 50% profit take and trailed the Stop Loss upward to \$66,100. On May 17, the market retracted, striking the updated Stop Loss, safely liquidating the remainder of the position into 100% stable liquidity.
* **May 18 – May 20:** Risk Mitigation & Capital Protection. During an intense market drawdown, the algorithm systematically blocked buy entries despite massive oversold readings, citing a lack of bullish MACD convergence. This effectively protected capital from a severe downside trend.
* **May 21:** Systematic Trade Reactivation. Following an absorption bounce starting at \$61,600 and a subsequent bullish MACD crossover, the pipeline triggered a brand new *Strong Buy* signal at ~\$62,980. Automated technical exit boundaries were established with a technical Stop Loss at \$61,400 and an initial Take Profit placed near the Bollinger middle moving average at ~\$64,950.

---
**Prepared by:** Data Engineering Team – MarketMatrix Project
