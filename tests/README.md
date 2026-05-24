# Unit and Integration Tests

This folder separates tests into two groups:

```text
tests/
├── conftest.py
├── unit/
│   ├── test_athena_sql_unit.py
   │   ├── test_importability.py
   │   ├── test_indicators.py
   │   └── test_lambda_handler_unit.py
└── integration/
    ├── test_athena_view_integration.py
    ├── test_binance_api_integration.py
    ├── test_lambda_binance_s3_integration.py
    └── test_s3_integration.py
```

## Install development dependencies

```bash
pip install -r requirements-dev.txt
```

Run only unit tests:

```bash
pytest -q -m unit
```

Run all tests except integration tests:

```bash
pytest -q -m "not integration"
```

## Unit tests

Unit tests do not use the internet or real AWS services.

They validate:

- Importing the Lambda script.
- SMA calculation.
- RSI calculation.
- Standard deviation calculation.
- EMA calculation.
- CSV generation.
- Mocked call to S3 `put_object`.
- Error handling.
- Main structure and rules of the Athena SQL.

## Integration tests

Integration tests are disabled by default because they use external services.

### Binance integration

```bash
RUN_BINANCE_INTEGRATION=1 pytest -q -m integration tests/integration/test_binance_api_integration.py
```

### S3 integration

```bash
RUN_AWS_INTEGRATION=1 \
TEST_S3_BUCKET=your-test-bucket \
pytest -q -m integration tests/integration/test_s3_integration.py
```

### Lambda + Binance + S3 integration

```bash
RUN_AWS_INTEGRATION=1 \
RUN_BINANCE_INTEGRATION=1 \
TEST_S3_BUCKET=your-test-bucket \
pytest -q -m integration tests/integration/test_lambda_binance_s3_integration.py
```

This test runs `lambda_handler`, queries the real Binance API and uploads the CSV to a real test bucket.
The test deletes the created object after it finishes.

### Athena integration

```bash
RUN_AWS_INTEGRATION=1 \
TEST_ATHENA_DATABASE=your_test_database \
TEST_ATHENA_OUTPUT_LOCATION=s3://your-athena-results-bucket/integration-tests/ \
pytest -q -m integration tests/integration/test_athena_view_integration.py
```

This test:

1. Reads `src/athena/athena_query.sql`.
2. Replaces the view name `gold_prediction` with a temporary view name.
3. Executes the `CREATE OR REPLACE VIEW`.
4. Executes `SELECT * FROM temporary_view LIMIT 1`.
5. Drops the temporary view with `DROP VIEW`.

## Important note

Integration tests require:

- configured AWS credentials;
- permissions for S3, Athena and the Glue Data Catalog;
- a test S3 bucket;
- the source table referenced by the SQL:
  `"glue-2silver"."silver_table"`.

If that table does not exist, the Athena test should fail — this indicates the integration environment is not ready.
