import pytest


pytestmark = pytest.mark.unit


def normalizar_sql(sql):
    return " ".join(sql.lower().split())


def test_athena_sql_crea_view_gold_prediction(athena_sql):
    sql = normalizar_sql(athena_sql)

    assert sql.startswith('create or replace view "gold_prediction" as select')


def test_athena_sql_lee_desde_tabla_silver(athena_sql):
    sql = normalizar_sql(athena_sql)

    assert 'from "glue-2silver"."silver_table"' in sql


def test_athena_sql_filtra_macd_no_nulo(athena_sql):
    sql = normalizar_sql(athena_sql)

    assert "where macd_linea is not null" in sql


def test_athena_sql_contiene_columnas_de_salida_esperadas(athena_sql):
    sql = normalizar_sql(athena_sql)

    columnas_esperadas = [
        "fecha",
        "precio",
        "estado_rsi",
        "posicion_bollinger",
        "recomendacion_algoritmica",
    ]

    for columna in columnas_esperadas:
        assert columna in sql


def test_athena_sql_contiene_reglas_de_rsi(athena_sql):
    sql = normalizar_sql(athena_sql)

    assert "rsi <= 30" in sql
    assert "rsi >= 70" in sql
    assert "sobrevendido" in sql
    assert "sobrecomprado" in sql


def test_athena_sql_contiene_reglas_de_bollinger(athena_sql):
    sql = normalizar_sql(athena_sql)

    assert "precio <= bollinger_baja" in sql
    assert "precio >= bollinger_alta" in sql
    assert "soporte" in sql
    assert "resistencia" in sql


def test_athena_sql_contiene_reglas_de_recomendacion_algoritmica(athena_sql):
    sql = normalizar_sql(athena_sql)

    assert "compra fuerte" in sql
    assert "venta / toma ganancias" in sql
    assert "mantener / esperar" in sql
    assert "macd_linea > macd_senal" in sql
    assert "macd_linea < macd_senal" in sql
