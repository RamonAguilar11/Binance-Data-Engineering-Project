import os

import pytest


pytestmark = pytest.mark.integration


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_BINANCE_INTEGRATION") != "1",
    reason="Binance integration test disabled. Set RUN_BINANCE_INTEGRATION=1 to enable.",
)


def test_obtener_datos_binance_real(lambda_module):
    datos = lambda_module.obtener_datos_binance()

    assert isinstance(datos, list)
    assert len(datos) > 0

    primera_vela = datos[0]

    assert len(primera_vela) >= 5
    assert int(primera_vela[0]) > 0
    assert float(primera_vela[4]) > 0
