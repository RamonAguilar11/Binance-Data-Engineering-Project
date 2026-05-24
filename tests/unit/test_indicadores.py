import pytest


pytestmark = pytest.mark.unit


def test_calcular_sma_usa_los_ultimos_n_precios(lambda_module):
    precios = [10, 20, 30, 40, 50]

    resultado = lambda_module.calcular_sma(precios, 3)

    assert resultado == pytest.approx(40.0)


def test_calcular_sma_devuelve_none_si_no_hay_suficientes_datos(lambda_module):
    precios = [10, 20]

    resultado = lambda_module.calcular_sma(precios, 3)

    assert resultado is None


def test_calcular_rsi_devuelve_none_si_no_hay_suficientes_datos(lambda_module):
    precios = [1, 2, 3, 4, 5]

    resultado = lambda_module.calcular_rsi(precios, periodos=14)

    assert resultado is None


def test_calcular_rsi_sin_perdidas_devuelve_100(lambda_module):
    precios = list(range(1, 17))

    resultado = lambda_module.calcular_rsi(precios, periodos=14)

    assert resultado == 100


def test_calcular_rsi_con_ganancias_y_perdidas(lambda_module):
    # Differences: +1, -1, +2
    # Average gains = (1 + 0 + 2) / 3 = 1
    # Average losses = (0 + 1 + 0) / 3 = 0.3333
    # RS = 3
    # RSI = 100 - (100 / (1 + 3)) = 75
    precios = [1, 2, 1, 3]

    resultado = lambda_module.calcular_rsi(precios, periodos=3)

    assert resultado == pytest.approx(75.0)


def test_calcular_desviacion_estandar(lambda_module):
    precios = [2, 4, 4, 4, 5, 5, 7, 9]

    resultado = lambda_module.calcular_desviacion_estandar(precios, 8)

    assert resultado == pytest.approx(2.0)


def test_calcular_desviacion_estandar_devuelve_none_si_no_hay_suficientes_datos(lambda_module):
    precios = [10, 20]

    resultado = lambda_module.calcular_desviacion_estandar(precios, 5)

    assert resultado is None


def test_calcular_ema_lista_devuelve_lista_none_si_no_hay_suficientes_datos(lambda_module):
    precios = [10, 20]

    resultado = lambda_module.calcular_ema_lista(precios, 5)

    assert resultado == [None, None]


def test_calcular_ema_lista(lambda_module):
    precios = [10, 20, 30, 40]

    resultado = lambda_module.calcular_ema_lista(precios, 3)

    assert resultado[0] is None
    assert resultado[1] is None

    # EMA inicial = SMA de los primeros 3 precios = 20
    assert resultado[2] == pytest.approx(20.0)

    # k = 2 / (3 + 1) = 0.5
    # EMA siguiente = 40 * 0.5 + 20 * 0.5 = 30
    assert resultado[3] == pytest.approx(30.0)
