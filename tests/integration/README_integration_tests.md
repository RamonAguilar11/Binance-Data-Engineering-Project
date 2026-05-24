# Integration Tests

This folder contains integration tests for validating the project against real external services.

Unlike unit tests, integration tests may connect to:

- Binance API
- AWS S3
- AWS Athena
- AWS Glue Data Catalog

For safety reasons, integration tests are disabled by default. They only run when the required environment variables are explicitly set.

---

## 1. Prerequisites

Install the development dependencies first:
V
```bash
pip install -r requirements-dev.txt
```

Run all commands from the root of the project:

```bash
cd Binance-Data-Engineering-Project
```

Before running AWS integration tests, make sure you have valid AWS credentials configured.

You can configure them with:

```bash
aws configure
```

Or use an existing AWS CLI profile:

```bash
export AWS_PROFILE=default
export AWS_DEFAULT_REGION=mx-central-1
```

---

## 2. Run Unit Tests First

Before running integration tests, it is recommended to verify that all unit tests pass:

```bash
pytest -q -m unit
```

You can also run every test except integration tests:

```bash
pytest -q -m "not integration"
```

---

## 3. Binance API Integration Test

This test validates that the project can connect to the real Binance API and retrieve market data for the configured symbol, such as `BTCUSDT`.

This test does not require AWS credentials.

Run:

```bash
RUN_BINANCE_INTEGRATION=1 \
pytest -q tests/integration/test_binance_api_integration.py
```

This test validates that:

- the Binance API returns a valid response;
- the response is a list of candlestick records;
- each record contains a valid timestamp and closing price.

---

## 4. S3 Integration Test

This test validates that the project can write, read, and delete an object in a real S3 bucket.

It requires AWS credentials and a test bucket.

Set the required variables:

```bash
export AWS_PROFILE=default
export AWS_DEFAULT_REGION=mx-central-1
export TEST_S3_BUCKET=your-test-bucket-name
```

Run:

```bash
RUN_AWS_INTEGRATION=1 \
TEST_S3_BUCKET=$TEST_S3_BUCKET \
pytest -q tests/integration/test_s3_integration.py
```

This test performs the following flow:

```text
put_object -> get_object -> delete_object
```

In other words, it uploads a temporary file, reads it back, and then deletes it.

Do not use a production bucket unless you are completely sure it is safe.

---

## 5. Lambda + Binance + S3 Integration Test

This test validates the main data ingestion flow:

```text
Binance API -> Python processing -> CSV generation -> S3 upload
```

It requires:

- internet access;
- AWS credentials;
- a test S3 bucket.

Set the required variables:

```bash
export AWS_PROFILE=default
export AWS_DEFAULT_REGION=mx-central-1
export TEST_S3_BUCKET=your-test-bucket-name
```

Run:

```bash
RUN_AWS_INTEGRATION=1 \
RUN_BINANCE_INTEGRATION=1 \
TEST_S3_BUCKET=$TEST_S3_BUCKET \
pytest -q tests/integration/test_lambda_binance_s3_integration.py
```

This test temporarily overrides the bucket name used by the script so it does not write to the hardcoded production bucket.

After the test finishes, it deletes the generated S3 object.

---

## 6. Athena View Integration Test

This test validates that the Athena SQL query can create a real view.

The test reads the SQL file from:

```text
src/athena/athena_query.sql
```

Then it creates a temporary Athena view, executes:

```sql
SELECT * FROM temporary_view LIMIT 1;
```

Finally, it deletes the temporary view.

This test requires:

- valid AWS credentials;
- permissions to use Athena;
- permissions to read the Glue Data Catalog;
- permissions to write Athena query results to S3;
- an existing Athena or Glue database;
- the source table referenced by the SQL query.

Set the required variables:

```bash
export AWS_PROFILE=default
export AWS_DEFAULT_REGION=mx-central-1
export TEST_ATHENA_DATABASE=glue-2silver
export TEST_ATHENA_OUTPUT_LOCATION=s3://your-athena-results-bucket/integration-tests/
```

Run:

```bash
RUN_AWS_INTEGRATION=1 \
TEST_ATHENA_DATABASE=$TEST_ATHENA_DATABASE \
TEST_ATHENA_OUTPUT_LOCATION=$TEST_ATHENA_OUTPUT_LOCATION \
pytest -q tests/integration/test_athena_view_integration.py
```

The Athena test may fail if:

- the source table does not exist;
- Athena cannot write query results to S3;
- the SQL query has syntax errors;
- the Glue Data Catalog is not available;
- the AWS credentials are invalid or expired;
- the IAM user or role does not have the required permissions.

---

## 7. Run All Integration Tests

Only run all integration tests when the full external environment is ready.

Set the required variables:

```bash
export AWS_PROFILE=default
export AWS_DEFAULT_REGION=mx-central-1
export TEST_S3_BUCKET=your-test-bucket-name
export TEST_ATHENA_DATABASE=glue-2silver
export TEST_ATHENA_OUTPUT_LOCATION=s3://your-athena-results-bucket/integration-tests/
```

Then run:

```bash
RUN_AWS_INTEGRATION=1 \
RUN_BINANCE_INTEGRATION=1 \
pytest -q -m integration
```

---

## 8. Environment Variables

| Variable | Description | Required for |
|---|---|---|
| `RUN_BINANCE_INTEGRATION` | Enables tests that call the real Binance API | Binance, Lambda + Binance + S3 |
| `RUN_AWS_INTEGRATION` | Enables tests that use real AWS services | S3, Athena, Lambda + S3 |
| `TEST_S3_BUCKET` | Test bucket used for temporary S3 objects | S3, Lambda + S3 |
| `TEST_ATHENA_DATABASE` | Athena or Glue database used by the Athena integration test | Athena |
| `TEST_ATHENA_OUTPUT_LOCATION` | S3 location where Athena writes query results | Athena |
| `AWS_PROFILE` | Local AWS CLI profile used by boto3 | AWS |
| `AWS_DEFAULT_REGION` | AWS region used by boto3 | AWS |

---

## 9. Recommended Execution Order

Run the integration tests in this order:

### 1. Binance only

```bash
RUN_BINANCE_INTEGRATION=1 \
pytest -q tests/integration/test_binance_api_integration.py
```

### 2. S3 only

```bash
RUN_AWS_INTEGRATION=1 \
TEST_S3_BUCKET=your-test-bucket-name \
pytest -q tests/integration/test_s3_integration.py
```

### 3. Lambda + Binance + S3

```bash
RUN_AWS_INTEGRATION=1 \
RUN_BINANCE_INTEGRATION=1 \
TEST_S3_BUCKET=your-test-bucket-name \
pytest -q tests/integration/test_lambda_binance_s3_integration.py
```

### 4. Athena

```bash
RUN_AWS_INTEGRATION=1 \
TEST_ATHENA_DATABASE=glue-2silver \
TEST_ATHENA_OUTPUT_LOCATION=s3://your-athena-results-bucket/integration-tests/ \
pytest -q tests/integration/test_athena_view_integration.py
```

Athena is recommended last because it depends on more components:

- S3
- Athena
- Glue Data Catalog
- IAM permissions
- the existence of the Silver source table

---

## 10. Important Notes

Integration tests may fail even when the application code is correct.

Common external causes include:

- Binance API temporary errors;
- invalid or expired AWS credentials;
- missing IAM permissions;
- missing S3 bucket;
- missing Athena output location;
- missing Glue table;
- unavailable AWS services;
- SQL schema mismatches.

For that reason, integration tests are not intended to run automatically by default.

Unit tests should be the default test suite for local development and basic CI validation.
