# Technical Documentation: Medallion Data Pipeline on AWS
**Project:** MarketMatrix (Serverless Financial Data Pipeline)  
**Version:** 1.1 — May 2026

---

## 1. Environment Configuration
This section provides a detailed breakdown of the infrastructure blueprints, service topologies, and discrete configurations utilized to implement the end-to-end cloud processing architecture for the **MarketMatrix** platform.

---

## 2. Infrastructure Resource Inventory

To ensure complete scalability, elasticity, and minimal operational overhead, all resources are deployed in a fully managed, serverless model within the Amazon Web Services (AWS) perimeter:

| AWS Service | Resource Name / Identifier | Core Infrastructure Function |
| :--- | :--- | :--- |
| **Amazon S3** | `unam-2026-ingenieriadatos-equipo2-066338415813-mx-central-1-an` | Persistent multi-tier cloud storage hosting the structured data lakehouse layers (`/bronze`, `/silver`, `/gold`). |
| **AWS Lambda** | `script_binance` | Serverless microservice running automated Python runtime tasks to pull active daily candle closes from the exchange API. |
| **AWS EventBridge** | `CierreDiarioBTC` | Cloud native event orchestrator maintaining a dedicated cron daemon to trigger ingestion runs on exact schedules. |
| **AWS Glue** | `2silver_cleaning_data` | Managed serverless Spark job engine that automates data cataloging, indexing, and schema evolution. |
| **Amazon Athena** | `primary` (WorkGroup) / `glue-2silver` (Database) | Serverless distributed query processing engine used to evaluate mathematical indicator logic via direct ANSI SQL operations over S3. |

---

## 3. Pipeline Specifications (ETL Lifecycle)

### 3.1. Ingestion Layer (API -> Bronze)
* **Execution Dynamic:** Automating data intake without provisioning continuous compute loops. Every day at exactly **00:05 UTC** (18:05 CDMX), a target ruleset within **AWS EventBridge** dispatches an execution signal to the `script_binance` Lambda function.
* **Ingestion Logic:** The serverless function targets the Binance API endpoint, extracts the definitive daily closing price structure for Bitcoin (BTC), validates the network handshake, and saves the immutable result directly into `s3://unam-2026-ingenieriadatos-equipo2-066338415813-mx-central-1-an/bronze/` using a raw **CSV** format. Operational monitoring and execution tracing are captured live in **Amazon CloudWatch Logs**.

### 3.2. Transformation Layer (PySpark -> Silver)
* **Execution Dynamic:** A managed **AWS Glue Job** running an optimized **PySpark** script targets the newly ingested files to cleanse and reformat the data structure.
* **Core PySpark Tasks:**
    1. **Raw Extraction:** Reads the immutable text datasets directly from the `/bronze` root path.
    2. **Deduplication:** Runs window functions to discard redundant ticker sequences or transmission logs.
    3. **Schema Mapping & Casting:** Converts date expressions into unified cryptographic timestamps and casts prices into accurate numeric definitions.
    4. **Data Compaction:** Serializes the trusted datasets into **Apache Parquet** format partitioned systematically by execution date (`/year=/month=`), reducing overall footprint and data-scan overhead.

### 3.3. Refinement & Analytics Layer (Athena -> Gold)
* **Execution Dynamic:** Data entities are dynamically cataloged inside the **AWS Glue Data Catalog**. Instead of maintaining a costly, always-on relational database warehouse, analytical metrics are processed via **Amazon Athena**.
* **Indicator Mathematical Scoring:** Complex SQL queries run across the `/silver` Parquet tables to generate the `/gold` layer signals by assessing three strict trading boundaries simultaneously:
    * **RSI Evaluation:** Computing 14-period loss/gain ratios to map historical exhaustion levels ($\le 30$ or $\ge 70$).
    * **Bollinger Deviation:** Building localized volatility bands to track asset re-entries or extensions.
    * **MACD Crosses:** Performing exponential moving average crossovers against formal Signal lines.
* **Signal Persistence:** Validated outcomes (**STRONG BUY**, **PARTIAL/TOTAL SELL**, or **HOLD / LIQUIDITY**) are optimized as material views and exposed to the consumption layer for instantaneous querying.

---

## 4. Data Dictionary (Gold Layer: "gold_prediction" View)

The following schema accurately reflects the structural columns, datatypes, and constraints configured within the **AWS Glue Data Catalog** for user analytical queries:

| Column Name | Data Type | Constraint / Description |
| :--- | :--- | :--- |
| `fecha` | `STRING` | The definitive closing date or timestamp boundary inherited from the processed historical daily session. |
| `precio` | `DOUBLE` | The recorded settlement price of Bitcoin at the session closure. |
| `estado_rsi` | `VARCHAR(26)` | Derived indicator classification based on boundary limits: `SOBREVENDIDO (Oportunidad)`, `SOBRECOMPRADO (Riesgo)`, or `NEUTRAL`. |
| `posicion_bollinger` | `VARCHAR(25)` | Structural pricing location relative to volatility envelopes: `PRECIO BAJO (Soporte)`, `PRECIO ALTO (Resistencia)`, or `RANGO NORMAL`. |
| `recomendacion_algoritmica` | `VARCHAR(22)` | The final automated decision engine output: `COMPRA FUERTE`, `VENTA / TOMA GANANCIAS`, or `MANTENER / ESPERAR`. |

---

## 5. Execution & Monitoring Guide

### Manual Pipeline Trigger
To override the automated event rule or initiate an out-of-schedule pipeline run, engineers can force execution manually using the following **AWS CLI** instruction from an authenticated terminal workstation:

```bash
aws glue start-job-run --job-name 2silver_cleaning_data
```
