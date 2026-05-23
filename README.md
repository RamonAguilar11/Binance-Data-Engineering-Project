# Binance-Data-Engineering-Project

# MarketMatrix 📊🚀
**Prediccion de Trading de Criptomonedas**

MarketMatrix es una solución de ingeniería de datos que automatiza la extracción, procesamiento y análisis de datos de criptomonedas (Bitcoin) para generar señales de trading precisas. El sistema utiliza una arquitectura *serverless* en AWS para garantizar escalabilidad y eficiencia de costos.

## 🎯 Objetivo del Proyecto
El objetivo principal es responder a la pregunta fundamental de negocio: 
> "¿Cuál es el momento estadísticamente óptimo para realizar una operación de trading con cualquier criptomoneda que maximice la probabilidad de ganancia y minimice el riesgo?"

## 🔍 Objetivos Específicos del Proyecto

- Ingerir datos de precio y volumen desde la API de Binance.
- Almacenar los datos crudos en Amazon S3.
- Depurar, validar y transformar los datos.
- Convertir los datos limpios para mejorar el rendimiento de consulta.
- Consultar los datos preparados con Amazon Athena.
- Aplicar reglas de decisión basadas en RSI, Bandas de Bollinger y MACD.
- Generar una recomendación final: compra fuerte, venta o mantener.
- Mantener trazabilidad del dato desde la ingesta hasta la capa analítica final.

## 🏗️ Arquitectura del Sistema
El sistema sigue el patrón de diseño de **Medallion Architecture** (Capa Bronze, Silver y Gold).

![Arquitectura de MarketMatrix](Images/Diagrama_reglas.png)
*Diagrama de flujo: EventBridge -> Lambda -> S3 -> Glue -> Athena*

### 🛠️ Stack de Desarrollo
- **Extracción:** Python (Boto3, Requests) & Binance API.
- **Orquestación:** AWS EventBridge (Cron jobs).
- **Cómputo:** AWS Lambda (Serverless).
- **Almacenamiento:** Amazon S3 (Data Lake).
- **Procesamiento/ETL:** AWS Glue & PySpark.
- **Consultas/Analítica:** Amazon Athena (SQL).

## 📊 El Pipeline de Datos

### 1. Capa Bronze (Raw Data)
- **Frecuencia:** Diaria (00:05 UTC / 18:05 CDMX).
- **Formato:** CSV.
- **Descripción:** Captura la vela diaria de Binance justo después del cierre oficial, asegurando datos inmutables y completos.

### 2. Capa Silver (Processed Data)
- **Proceso:** AWS Glue Job.
- **Formato:** Parquet (Optimizado para analítica).
- **Descripción:** Limpieza de datos, eliminación de duplicados y transformación de tipos de datos para reducir costos de escaneo en Athena.

### 3. Capa Gold (Business Rules)
- **Interfaz:** Vistas en Amazon Athena.
- **Lógica:** Implementación de la **Regla de Triple Confirmación**.
- **Indicadores:** RSI, Bandas de Bollinger y MACD.

## 🛡️ Reglas de Negocio (Trading Logic)
La "Capa Gold" emite recomendaciones basadas en criterios matemáticos estrictos:

| Estado | Condición Técnica |
| :--- | :--- |
| **COMPRA FUERTE** | RSI ≤ 30 + Precio < Banda Inf. Bollinger + Cruce Alcista MACD |
| **VENTA** | RSI ≥ 70 + Precio > Banda Sup. Bollinger + Cruce Bajista MACD |
| **MANTENER** | Cuando no se cumplen simultáneamente los criterios de entrada o salida. |

---
