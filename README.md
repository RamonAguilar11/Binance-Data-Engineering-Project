# Binance-Data-Engineering-Project

# MarketMatrix 📊🚀
**Pipeline de Ingeniería de Datos para Recomendaciones de Trading de Bitcoin**

MarketMatrix es una solución de ingeniería de datos de extremo a extremo que automatiza la extracción, procesamiento y análisis técnico de datos de criptomonedas (Bitcoin) para generar señales de trading precisas. El sistema utiliza una arquitectura *serverless* en AWS para garantizar escalabilidad y eficiencia de costos.

## 🎯 Propósito del Proyecto
El objetivo principal es responder a la pregunta fundamental de negocio: 
> "¿Cuál es el momento estadísticamente óptimo para realizar una operación de trading con Bitcoin que maximice la probabilidad de ganancia y minimice el riesgo?"

## 🏗️ Arquitectura del Sistema
El sistema sigue el patrón de diseño de **Medallion Architecture** (Capa Bronze, Silver y Gold).

![Arquitectura de MarketMatrix](AQUÍ_VA_EL_LINK_A_TU_IMAGEN)
*Diagrama de flujo: EventBridge -> Lambda -> S3 -> Glue -> Athena*

### 🛠️ Tech Stack
- **Extracción:** Python (Boto3, Requests) & Binance API.
- **Orquestación:** AWS EventBridge (Cron jobs).
- **Cómputo:** AWS Lambda (Serverless).
- **Almacenamiento:** Amazon S3 (Data Lake).
- **Procesamiento/ETL:** AWS Glue & PySpark.
- **Consultas/Analítica:** Amazon Athena (Presto/SQL).

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
- **Indicadores:** RSI (14), Bandas de Bollinger (20, 2) y MACD (12, 26, 9).

## 🛡️ Reglas de Negocio (Trading Logic)
La "Capa Gold" emite recomendaciones basadas en criterios matemáticos estrictos:

| Estado | Condición Técnica |
| :--- | :--- |
| **COMPRA FUERTE** | RSI ≤ 30 + Precio < Banda Inf. Bollinger + Cruce Alcista MACD |
| **VENTA** | RSI ≥ 70 + Precio > Banda Sup. Bollinger + Cruce Bajista MACD |
| **MANTENER** | Cuando no se cumplen simultáneamente los criterios de entrada o salida. |

## 💰 Análisis de Costos (AWS Serverless)
El sistema ha sido optimizado para operar bajo el **Free Tier** de AWS:
- **Lambda & S3:** ~$0.00 USD (dentro de límites gratuitos).
- **Athena:** ~$0.01 USD por cada 2GB escaneados.
- **Opción de Automatización:** Se evaluó la automatización total de Glue, lo que incrementaría los costos en un 1,000% (de $0.05 a $0.50 USD mensuales), manteniendo la viabilidad económica del proyecto.

---
Desarrollado por Equipo 2 - MarketMatrix como parte del proyecto de Ingeniería de Datos.
