import csv
import io
import json
import math
import urllib.request
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime, timezone

# --- CONFIGURACIÓN GLOBAL ---
symbol = "BTCUSDT"
intervalo = "1d"
nombre_bucket = "unam-2026-ingenieriadatos-equipo2-066338415813-mx-central-1-an"

# ACTUALIZADO: Fecha de inicio a 1 de Enero de 2026
fecha_inicio_ms = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)

# --- FUNCIONES MATEMÁTICAS (NATIVAS) ---
def calcular_sma(precios, periodos):
    if len(precios) < periodos:
        return None
    return sum(precios[-periodos:]) / periodos

def calcular_rsi(precios, periodos=14):
    if len(precios) <= periodos:
        return None
    ganancias, perdidas = [], []
    for i in range(1, len(precios)):
        diferencia = precios[i] - precios[i-1]
        if diferencia > 0:
            ganancias.append(diferencia)
            perdidas.append(0)
        else:
            ganancias.append(0)
            perdidas.append(abs(diferencia))

    avg_gain = sum(ganancias[-periodos:]) / periodos
    avg_loss = sum(perdidas[-periodos:]) / periodos
    
    if avg_loss == 0: return 100
    return 100 - (100 / (1 + (avg_gain / avg_loss)))

def calcular_desviacion_estandar(precios, periodos):
    """Calcula la Desviación Estándar para las Bandas de Bollinger"""
    if len(precios) < periodos:
        return None
    ultimos_precios = precios[-periodos:]
    media = sum(ultimos_precios) / periodos
    varianza = sum((x - media) ** 2 for x in ultimos_precios) / periodos
    return math.sqrt(varianza)

def calcular_ema_lista(precios, periodos):
    """Calcula una lista completa de Medias Móviles Exponenciales (EMA) para el MACD"""
    ema = [None] * len(precios)
    if len(precios) < periodos:
        return ema
    # El primer valor EMA es simplemente el SMA de los primeros N días
    ema[periodos-1] = sum(precios[:periodos]) / periodos
    k = 2 / (periodos + 1)
    for i in range(periodos, len(precios)):
        ema[i] = (precios[i] * k) + (ema[i-1] * (1 - k))
    return ema

# --- OBTENER DATOS NATIVAMENTE ---
def obtener_datos_binance():
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={intervalo}&startTime={fecha_inicio_ms}&limit=1000"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

# --- LA FUNCIÓN PRINCIPAL DE LAMBDA ---
def lambda_handler(event, context):
    try:
        print(f"Obteniendo datos de {symbol} desde Enero 2026...")
        klines = obtener_datos_binance()

        fechas = []
        precios_cierre = []

        # 1. Extraer todos los precios primero
        for k in klines:
            fechas.append(datetime.fromtimestamp(k[0] / 1000).strftime('%Y-%m-%d'))
            precios_cierre.append(float(k[4]))

        # 2. Calcular los componentes del MACD en bloque (requiere historial completo)
        ema_12 = calcular_ema_lista(precios_cierre, 12)
        ema_26 = calcular_ema_lista(precios_cierre, 26)
        
        macd_line = []
        for i in range(len(precios_cierre)):
            if ema_12[i] is not None and ema_26[i] is not None:
                macd_line.append(ema_12[i] - ema_26[i])
            else:
                macd_line.append(None)

        # La línea de señal es un EMA de 9 periodos aplicado sobre la línea MACD
        macd_validos = [x for x in macd_line if x is not None]
        signal_line_corta = calcular_ema_lista(macd_validos, 9)
        # Alineamos la lista de señal con el tamaño original de nuestros datos
        signal_line = [None] * (len(precios_cierre) - len(signal_line_corta)) + signal_line_corta

        # 3. Procesar datos día por día y ensamblar CSV
        datos_procesados = []
        for i in range(len(precios_cierre)):
            precio = precios_cierre[i]
            precios_hist = precios_cierre[:i+1] # Historial hasta el día actual
            
            # Indicadores Clásicos
            sma_20 = calcular_sma(precios_hist, 20)
            rsi_14 = calcular_rsi(precios_hist, 14)
            
            # Bandas de Bollinger
            sd_20 = calcular_desviacion_estandar(precios_hist, 20)
            bollinger_alta = (sma_20 + (sd_20 * 2)) if sma_20 and sd_20 else None
            bollinger_baja = (sma_20 - (sd_20 * 2)) if sma_20 and sd_20 else None

            datos_procesados.append({
                'Fecha': fechas[i],
                'Precio': precio,
                'Promedio_20d': round(sma_20, 2) if sma_20 else "",
                'RSI': round(rsi_14, 2) if rsi_14 else "",
                'Bollinger_Alta': round(bollinger_alta, 2) if bollinger_alta else "",
                'Bollinger_Baja': round(bollinger_baja, 2) if bollinger_baja else "",
                'MACD_Linea': round(macd_line[i], 2) if macd_line[i] is not None else "",
                'MACD_Senal': round(signal_line[i], 2) if signal_line[i] is not None else ""
            })

        # 4. Crear el CSV EN MEMORIA
        print("Generando CSV en memoria con nuevos indicadores...")
        csv_buffer = io.StringIO()
        columnas = ['Fecha', 'Precio', 'Promedio_20d', 'RSI', 'Bollinger_Alta', 'Bollinger_Baja', 'MACD_Linea', 'MACD_Senal']
        writer = csv.DictWriter(csv_buffer, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(datos_procesados)

        # 5. Enviar a S3
        print("Enviando datos a S3...")
        s3_client = boto3.client('s3')
        carpeta_fecha = datetime.now().strftime('%d-%m-%Y-%H-%M') 
        ruta_completa_s3 = f"1bronze/{carpeta_fecha}/analisis_{symbol}.csv"

        s3_client.put_object(
            Bucket=nombre_bucket, 
            Key=ruta_completa_s3, 
            Body=csv_buffer.getvalue()
        )
        
        mensaje = f"¡Éxito! CSV guardado con indicadores avanzados en: s3://{nombre_bucket}/{ruta_completa_s3}"
        print(mensaje)
        return {'statusCode': 200, 'body': mensaje}

    except Exception as e:
        error_msg = f"Error crítico: {str(e)}"
        print(error_msg)
        return {'statusCode': 500, 'body': error_msg}