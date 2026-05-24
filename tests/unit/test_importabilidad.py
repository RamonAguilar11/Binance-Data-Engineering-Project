import pytest


pytestmark = pytest.mark.unit


def test_script_lambda_se_puede_importar(lambda_module):
    assert hasattr(lambda_module, "lambda_handler")
    assert hasattr(lambda_module, "obtener_datos_binance")
    assert hasattr(lambda_module, "calcular_sma")
    assert hasattr(lambda_module, "calcular_rsi")
    assert hasattr(lambda_module, "calcular_desviacion_estandar")
    assert hasattr(lambda_module, "calcular_ema_lista")


def test_archivo_athena_sql_no_esta_vacio(athena_sql):
    assert athena_sql.strip() != ""
