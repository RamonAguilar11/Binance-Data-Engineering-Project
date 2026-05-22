# Functional Documentation: MarketMatrix Trading Analytics Platform
**Project:** MarketMatrix (Serverless Financial Data Pipeline)  

---

## 1. Document Objective
This document outlines the functional features of the **MarketMatrix** system from a business, operational, and end-user perspective. It defines what the system can do, who interacts with it, and the financial and technical value it delivers to users, without diving into raw code implementations or infrastructure details.

---

## 2. User Roles & Profiles

To guarantee structural separation of operational tasks, systemic auditing, and risk management, the platform defines the following core profiles:

| Role | Core Responsibilities |
| :--- | :--- |
| **Quantitative Trader / Financial Analyst** | Consults refined technical indicator signals, monitors algorithmic trends, and executes trading entries or risk adjustments based on system recommendations. |
| **Data Engineer (Support / Platform)** | Monitors daily ingestion pipelines to ensure that loading and processing routines execute flawlessly every single day. |
| **Risk Manager / Stakeholder** | Visualizes strategic KPIs, reviews historical trading efficiency, and leverages analytical insights for critical operational decision-making. |

---

## 3. Supported Business Processes

### 3.1. Automated Market Data Centralization
The system automatically captures and consolidates daily Bitcoin or any other cryptocurrency market data (Binance daily closing candles) directly into a secure, centralized cloud repository (Silver/Gold layers). This eliminates the reliance on manual tracking, unstandardized Excel spreadsheets, or fragmented local files.

### 3.2. Programmatic Financial Data Cleansing
The analytical pipeline programmatically identifies and mitigates common data anomalies. It automatically drops duplicate exchange logs and standardizes inconsistencies, ensuring that quantitative analysis is executed against a mathematically sound, unified source of truth.

### 3.3. Algorithmic Technical Evaluation & Historical Reporting
The system automates the evaluation of market momentum and volatility through a rigid mathematical framework while enabling deep data accumulation. This allows the platform to support comprehensive historical comparisons and performance evaluations across extensive custom timeframes. Under the hood, it concurrently scores three distinct market parameters:
* **RSI (14):** Evaluates extreme exhaustion boundaries (Oversold $\le 30$ / Overbought $\ge 70$).
* **Bollinger Bands (20, 2):** Identifies price rejections, entries, or deviations along volatility envelopes.
* **MACD (12, 26, 9):** Validates precise momentum shifts via directional crossovers between the MACD Line and the Signal Line.

---

## 4. Operational Use Cases

* **Use Case 1: Trader checks for actionable market triggers at the daily close.**
    * *System Outcome:* The pipeline completes its daily extraction, transformation, and analytical indicator scoring within minutes of the daily candle close. Results are fully updated, cataloged, and queryable via Amazon Athena by 00:10 UTC (18:10 CDMX), ensuring data availability right after the market close.
* **Use Case 2: Historical API data discrepancy or exchange downtime detected.**
    * *System Outcome:* System support engineers can initiate an isolated historical backfill (reprocessing script) to cleanly extract, rewrite, and recalculate historical data partitions to restore overall data integrity without corrupting current production tables.
* **Use Case 3: Extreme market volatility or flash crash event occurs.**
    * *System Outcome:* The pipeline detects extreme oversold values but flags a lack of cross-indicator validation (e.g., MACD lagging or missing confirmation). The system automatically enforces a capital lock, defaulting to maximum liquidity and preventing the portfolio from catching "falling knives."

---

## 5. Strict Business & Trading Rules

1.  **Strict Convergence Requirement:** Actionable entry or exit signals are generated exclusively when all three technical indicators (RSI, Bollinger Bands, and MACD) align perfectly. If any condition fails to meet the exact mathematical threshold, the platform defaults to a **HOLD / LIQUIDITY** state.
2.  **Definitive Exchange Closure:** Ingestion triggers are explicitly calibrated to execute at 00:05 UTC (using a strict `cron(5 0 * * ? *)` schedule) to capture the absolute and immutable closing price of the daily Binance candle, eliminating timezone-skew errors.
3.  **Capital Protection Bounds:** Every buy recommendation must be coupled with an immediate technical Stop Loss floor and a corresponding Take Profit ceiling to enforce structural risk management and systematically protect trading equity.

---

## 6. Glossary of Terms for the User

* **Strong Buy / Strong Sell:** Definitive algorithmic recommendations triggered only when the system achieves full triple-confirmation compliance across all indicator sub-routines.
* **Hold / Liquidity:** The baseline default state of the pipeline when market data is inconclusive, focusing entirely on capital preservation and risk avoidance.
* **Daily Ingestion (Daily Charge):** The automated, serverless process running every evening that securely pulls market closing structures from global data sources into the data lakehouse.
* **Backfill:** The manual or automated operational capability to re-run data processing layers over a specified historical window to restore data integrity.
* **Availability:** The exact window of time and structural state in which the technical infrastructure is completely ready to be queried by users.

---
**Approved by:** Quantitative Engineering & Risk Operations — Team MarketMatrix
