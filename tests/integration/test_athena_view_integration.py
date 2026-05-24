import os
import time
import uuid

import pytest


pytestmark = pytest.mark.integration


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_AWS_INTEGRATION") != "1"
    or not os.getenv("TEST_ATHENA_DATABASE")
    or not os.getenv("TEST_ATHENA_OUTPUT_LOCATION"),
    reason=(
        "Athena integration test disabled. "
        "Set RUN_AWS_INTEGRATION=1, TEST_ATHENA_DATABASE=<db> "
        "and TEST_ATHENA_OUTPUT_LOCATION=s3://bucket/prefix/."
    ),
)


def _ejecutar_athena(athena, sql, database, output_location):
    respuesta = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": output_location},
    )
    return respuesta["QueryExecutionId"]


def _esperar_query(athena, query_execution_id, timeout_segundos=90):
    inicio = time.time()

    while True:
        estado = athena.get_query_execution(
            QueryExecutionId=query_execution_id
        )["QueryExecution"]["Status"]

        state = estado["State"]

        if state == "SUCCEEDED":
            return

        if state in {"FAILED", "CANCELLED"}:
            razon = estado.get("StateChangeReason", "No details")
            raise AssertionError(f"Athena query ended in {state}: {razon}")

        if time.time() - inicio > timeout_segundos:
            raise TimeoutError(f"Athena took more than {timeout_segundos}s")

        time.sleep(2)


def test_athena_crea_y_consulta_view_temporal(athena_sql):
    boto3 = pytest.importorskip("boto3")

    database = os.environ["TEST_ATHENA_DATABASE"]
    output_location = os.environ["TEST_ATHENA_OUTPUT_LOCATION"]

    athena = boto3.client("athena")

    view_temporal = f"gold_prediction_pytest_{uuid.uuid4().hex[:8]}"

    sql_create = athena_sql.replace('"gold_prediction"', f'"{view_temporal}"')
    sql_select = f'SELECT * FROM "{view_temporal}" LIMIT 1'
    sql_drop = f'DROP VIEW IF EXISTS "{view_temporal}"'

    try:
        qid_create = _ejecutar_athena(athena, sql_create, database, output_location)
        _esperar_query(athena, qid_create)

        qid_select = _ejecutar_athena(athena, sql_select, database, output_location)
        _esperar_query(athena, qid_select)
    finally:
        qid_drop = _ejecutar_athena(athena, sql_drop, database, output_location)
        _esperar_query(athena, qid_drop)
