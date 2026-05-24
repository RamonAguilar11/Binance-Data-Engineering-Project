import csv
import io
import re

import pytest


pytestmark = pytest.mark.unit


class FakeS3Client:
    def __init__(self):
        self.put_object_calls = []

    def put_object(self, **kwargs):
        self.put_object_calls.append(kwargs)
        return {"ETag": "fake-etag"}


def test_lambda_handler_genera_csv_y_llama_put_object(lambda_module, fake_klines, monkeypatch):
    fake_s3 = FakeS3Client()

    monkeypatch.setattr(
        lambda_module,
        "obtener_datos_binance",
        lambda: fake_klines(cantidad=40, precio_inicial=100.0),
    )

    monkeypatch.setattr(
        lambda_module.boto3,
        "client",
        lambda service_name: fake_s3,
    )

    respuesta = lambda_module.lambda_handler({}, None)

    assert respuesta["statusCode"] == 200
    assert "Éxito" in respuesta["body"]

    assert len(fake_s3.put_object_calls) == 1

    llamada_s3 = fake_s3.put_object_calls[0]

    assert llamada_s3["Bucket"] == lambda_module.nombre_bucket
    assert llamada_s3["Key"].startswith("1bronze/")
    assert llamada_s3["Key"].endswith("/analisis_BTCUSDT.csv")
    assert re.match(
        r"1bronze/\d{2}-\d{2}-\d{4}-\d{2}-\d{2}/analisis_BTCUSDT\.csv",
        llamada_s3["Key"],
    )

    csv_generado = llamada_s3["Body"]
    filas = list(csv.DictReader(io.StringIO(csv_generado)))

    assert len(filas) == 40

    assert list(filas[0].keys()) == [
        "Fecha",
        "Precio",
        "Promedio_20d",
        "RSI",
        "Bollinger_Alta",
        "Bollinger_Baja",
        "MACD_Linea",
        "MACD_Senal",
    ]

    assert filas[0]["Fecha"] == "2026-01-01"
    assert float(filas[0]["Precio"]) == pytest.approx(100.0)

    # Before 20 records there is no 20-day SMA yet.
    assert filas[0]["Promedio_20d"] == ""

    # On the 20th record the SMA for prices 100 to 119 exists.
    assert float(filas[19]["Promedio_20d"]) == pytest.approx(109.5)

    # MACD appears only after EMA 12 and EMA 26 are available.
    assert filas[24]["MACD_Linea"] == ""
    assert filas[25]["MACD_Linea"] != ""

    # The MACD signal requires 9 valid MACD values.
    assert filas[32]["MACD_Senal"] == ""
    assert filas[33]["MACD_Senal"] != ""


def test_lambda_handler_devuelve_500_si_falla_binance(lambda_module, monkeypatch):
    def obtener_datos_con_error():
        raise RuntimeError("Error simulado de Binance")

    monkeypatch.setattr(lambda_module, "obtener_datos_binance", obtener_datos_con_error)

    respuesta = lambda_module.lambda_handler({}, None)

    assert respuesta["statusCode"] == 500
    assert "Error crítico" in respuesta["body"]
    assert "Error simulado de Binance" in respuesta["body"]


def test_lambda_handler_devuelve_500_si_falla_s3(lambda_module, fake_klines, monkeypatch):
    class FakeS3ConError:
        def put_object(self, **kwargs):
            raise RuntimeError("Error simulado de S3")

    monkeypatch.setattr(
        lambda_module,
        "obtener_datos_binance",
        lambda: fake_klines(cantidad=40, precio_inicial=100.0),
    )

    monkeypatch.setattr(
        lambda_module.boto3,
        "client",
        lambda service_name: FakeS3ConError(),
    )

    respuesta = lambda_module.lambda_handler({}, None)

    assert respuesta["statusCode"] == 500
    assert "Error crítico" in respuesta["body"]
    assert "Error simulado de S3" in respuesta["body"]
