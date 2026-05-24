from datetime import datetime, timezone, timedelta
from pathlib import Path
import importlib.util
import sys
import types

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]

LAMBDA_SCRIPT = REPO_ROOT / "src" / "lambda" / "script_bincance.py"
ATHENA_SQL = REPO_ROOT / "src" / "athena" / "athena_query.sql"


def _install_fake_aws_modules_if_needed():
    """Allow running unit tests even if boto3/botocore are not installed.

    In unit tests, boto3.client is replaced via monkeypatch. If the real
    boto3 package is already installed, this function does not replace it.
    """
    try:
        import boto3  # noqa: F401
        import botocore.exceptions  # noqa: F401
        return
    except Exception:
        pass

    if "boto3" not in sys.modules:
        fake_boto3 = types.ModuleType("boto3")

        def fake_client(*args, **kwargs):
            raise RuntimeError("boto3.client fue llamado sin mockearse en el test")

        fake_boto3.client = fake_client
        sys.modules["boto3"] = fake_boto3

    if "botocore" not in sys.modules:
        sys.modules["botocore"] = types.ModuleType("botocore")

    if "botocore.exceptions" not in sys.modules:
        fake_exceptions = types.ModuleType("botocore.exceptions")

        class NoCredentialsError(Exception):
            pass

        fake_exceptions.NoCredentialsError = NoCredentialsError
        sys.modules["botocore.exceptions"] = fake_exceptions


@pytest.fixture(scope="session")
def lambda_module():

    """Import src/lambda/script_bincance.py using an absolute path.

    importlib is used because `lambda` is a reserved word in Python and
    cannot be used as a module name in regular import statements.
    """
    assert LAMBDA_SCRIPT.exists(), f"No se encontró el archivo: {LAMBDA_SCRIPT}"

    _install_fake_aws_modules_if_needed()

    spec = importlib.util.spec_from_file_location("script_bincance", LAMBDA_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["script_bincance"] = module

    try:
        spec.loader.exec_module(module)
    except SyntaxError as exc:
        pytest.fail(
            "No se pudo importar src/lambda/script_bincance.py por error de sintaxis. "
            "Revisa que el archivo tenga saltos de línea e indentación válidos. "
            f"Detalle: {exc}"
        )

    return module


@pytest.fixture(scope="session")
def athena_sql():
    assert ATHENA_SQL.exists(), f"No se encontró el archivo: {ATHENA_SQL}"
    return ATHENA_SQL.read_text(encoding="utf-8")


@pytest.fixture
def fake_klines():
    """
    Generate fake data similar to Binance /api/v3/klines.

    The script only uses:
    - k[0]: timestamp in milliseconds
    - k[4]: closing price
    """
    def _factory(cantidad=40, precio_inicial=100.0):
        base = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        klines = []

        for i in range(cantidad):
            fecha_ms = int((base + timedelta(days=i)).timestamp() * 1000)
            precio_cierre = precio_inicial + i

            klines.append([
                fecha_ms,
                "0", "0", "0",
                str(precio_cierre),
                "0", "0", "0", "0", "0", "0", "0",
            ])

        return klines

    return _factory
