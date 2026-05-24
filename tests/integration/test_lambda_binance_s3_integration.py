import os
import re

import pytest


pytestmark = pytest.mark.integration


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_AWS_INTEGRATION") != "1"
    or os.getenv("RUN_BINANCE_INTEGRATION") != "1"
    or not os.getenv("TEST_S3_BUCKET"),
    reason=(
        "Lambda + Binance + S3 integration test disabled. "
        "Set RUN_AWS_INTEGRATION=1, RUN_BINANCE_INTEGRATION=1 and TEST_S3_BUCKET=<bucket>."
    ),
)


def test_lambda_handler_real_binance_y_s3(lambda_module, monkeypatch):
    boto3 = pytest.importorskip("boto3")

    bucket = os.environ["TEST_S3_BUCKET"]
    s3 = boto3.client("s3")

    # Prevent writing to the script's hardcoded production bucket.
    monkeypatch.setattr(lambda_module, "nombre_bucket", bucket)

    respuesta = lambda_module.lambda_handler({}, None)

    assert respuesta["statusCode"] == 200
    assert "Éxito" in respuesta["body"]

    match = re.search(rf"s3://{re.escape(bucket)}/(.+)$", respuesta["body"])
    assert match, "Could not extract the S3 key from the response message"

    key = match.group(1)

    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        contenido = obj["Body"].read().decode("utf-8")

        assert "Fecha,Precio,Promedio_20d,RSI,Bollinger_Alta,Bollinger_Baja,MACD_Linea,MACD_Senal" in contenido
        assert "BTCUSDT" in respuesta["body"]
    finally:
        s3.delete_object(Bucket=bucket, Key=key)
