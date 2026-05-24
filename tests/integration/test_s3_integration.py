import os
import uuid

import pytest


pytestmark = pytest.mark.integration


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_AWS_INTEGRATION") != "1" or not os.getenv("TEST_S3_BUCKET"),
    reason=(
        "S3 integration test disabled. "
        "Set RUN_AWS_INTEGRATION=1 and TEST_S3_BUCKET=<bucket>."
    ),
)


def test_s3_put_get_delete_real():
    boto3 = pytest.importorskip("boto3")

    bucket = os.environ["TEST_S3_BUCKET"]
    key = f"integration-tests/pytest-{uuid.uuid4()}.txt"
    body = "test file for S3 integration"

    s3 = boto3.client("s3")

    try:
        s3.put_object(Bucket=bucket, Key=key, Body=body)

        respuesta = s3.get_object(Bucket=bucket, Key=key)
        contenido = respuesta["Body"].read().decode("utf-8")

        assert contenido == body
    finally:
        s3.delete_object(Bucket=bucket, Key=key)
