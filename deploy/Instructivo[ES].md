# Guía de Despliegue y Replicabilidad 🚀
**MarketMatrix — Pipeline Serverless de Ingeniería de Datos**

Esta carpeta contiene el instructivo técnico paso a paso para replicar e implementar la infraestructura completa del proyecto **MarketMatrix** en una cuenta de AWS, garantizando la correcta transición entre las capas Bronze, Silver y Gold de la arquitectura.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de contar con lo siguiente:
- Una cuenta activa de AWS con permisos de Administrador o roles con permisos para S3, Lambda, EventBridge, Glue y Athena.
- [Python 3.9+](https://www.python.org/) instalado localmente para pruebas.
- Una cuenta en **Binance** para obtener las llaves de la API (públicas/privadas) o acceso a los endpoints públicos de la API de Spot.
- El repositorio del proyecto clonado localmente.

---

## 🛠️ Paso 1: Configuración del Almacenamiento (Amazon S3)

El pipeline implementa una arquitectura de medallas (*Medallion Architecture*). Debes crear un bucket de S3 único que alojará los datos en sus diferentes etapas.

1. Ve a la consola de **Amazon S3** y haz clic en **Create bucket**.
2. **Nombre del bucket:** Elige un nombre único global (siguiendo las políticas de nomenclatura de tu organización). 
   * *Nota de Seguridad: Por motivos de cumplimiento y privacidad, no incluyas tu ID de cuenta de AWS en el nombre público del bucket.*
3. **Región:** Selecciona la región más cercana (ej. `us-east-1` o la asignada a tu cuenta).
4. **Configuración de Seguridad:** Asegúrate de marcar la casilla **"Block Public Access" (Bloquear todo el acceso público)** para proteger los datos de accesos no autorizados.
5. Haz clic en **Create bucket**.
6. Dentro del bucket creado, genera la estructura de carpetas inicial:
   - `1bronze/` *(Para los archivos de extracción crudos en formato CSV)*
   - `2silver/` *(Para los datos limpios y optimizados en formato Parquet)*
   - `3gold/` *(Para almacenar resultados de consultas y reportes analíticos de Athena)*

---

## ⚡ Paso 2: Despliegue del Módulo de Extracción (AWS Lambda)

La AWS Lambda se encarga de realizar la petición HTTP a la API de Binance, procesar la respuesta e instanciar el archivo inmutable en la capa Bronze.

1. Ve a la consola de **AWS Lambda** y haz clic en **Create function**.
2. Selecciona **Author from scratch**.
3. **Configuración básica:**
   * **Function name:** `marketmatrix-extractor-lambda`
   * **Runtime:** `Python 3.9` (o superior)
   * **Architecture:** `x86_64`
4. **Permisos de Ejecución (Execution Role):**
   * Elige *Create a new role with basic Lambda permissions*.
   * Una vez creada la Lambda, ve a la pestaña de **Configuration** -> **Permissions** y haz clic en el rol generado para ir a la consola de IAM.
   * Adjunta una política en línea (Inline Policy) que otorgue permisos específicos de escritura (`PutObject`) únicamente en el bucket de S3 creado en el Paso 1.
5. **Carga de Código:**
   * Copia el código fuente de tu script de extracción (`src/extractor.py`) y pégalo en el editor de código de la Lambda.
   * *Asegúrate de configurar las variables de entorno necesarias si estás usando firmas de API, o de apuntar directamente al endpoint público de Binance (`https://api.binance.com/api/v3/klines`).*
6. **Configuración de Tiempo de Espera (Timeout):**
   * En **Configuration** -> **General configuration**, cambia el Timeout por defecto (3 segundos) a **1 minuto** para prevenir caídas por latencia de red durante la llamada a la API externa.

---

## ⏱️ Paso 3: Automatización del Pipeline (AWS EventBridge)

Para capturar la vela diaria oficial inmediatamente después de su cierre, configuraremos un disparador basado en tiempo.

1. Ve a la consola de **Amazon EventBridge** y selecciona **Rules** -> **Create rule**.
2. **Definición de regla:**
   * **Name:** `marketmatrix-daily-trigger`
   * **Rule type:** `Schedule`
3. **Configuración del Horario:**
   * Selecciona **A fine-grained schedule (cron expression)**.
   * **Expresión Cron:** `cron(5 0 * * ? *)`
   * *Explicación:* Esta expresión dispara el evento todos los días a las 00:05 UTC (equivalente a las 18:05 CDMX). Esto garantiza que Binance ya haya consolidado y cerrado formalmente la vela del día anterior, evitando fluctuaciones intradía.
4. **Selección del Target:**
   * En **Target types**, selecciona **AWS service**.
   * En el menú desplegable, elige **Lambda function**.
   * Selecciona tu función: `marketmatrix-extractor-lambda`.
5. Revisa las configuraciones y haz clic en **Create rule**.

---

## 🗄️ Paso 4: Catálogo de Datos y Transformación (AWS Glue)

AWS Glue se encargará de estructurar el esquema de datos y ejecutar el proceso ETL para transformar los CSV de la capa Bronze a archivos optimizados Parquet en la capa Silver.

### 4.1. Configuración del Crawler para la Capa Bronze
1. Ve a **AWS Glue** -> **Crawlers** -> **Create crawler**.
2. **Name:** `marketmatrix-bronze-crawler`.
3. **Data store:** Elige `S3` y añade la ruta completa a tu carpeta Bronze: `s3://<TU-BUCKET-NAME>/1bronze/`.
4. **IAM Role:** Crea o selecciona un rol de IAM con la política administrada `AWSGlueServiceRole` y que posea permisos de lectura en tu bucket de S3.
5. **Output Database:** Crea una base de datos en el catálogo de datos llamada `marketmatrix_db`.
6. **Schedule:** Configúralo bajo demanda o programado para ejecutarse después de la Lambda. Haz clic en **Create y Run crawler** para mapear los primeros datos y crear la tabla externa inicial.

### 4.2. Despliegue del Glue Job (PySpark)
1. Ve a **AWS Glue** -> **ETL Jobs** -> **Script editor**.
2. Selecciona **Spark script editor** para cargar tu script de PySpark (`src/transform_silver.py`).
3. El script debe realizar las siguientes acciones lógicas:
   * Leer los datos crudos desde la tabla de catálogo de `1bronze/`.
   * Realizar la limpieza de datos (eliminar registros duplicados, castear tipos de datos: `timestamp` a fecha, precios a tipo `double`).
   * Escribir los datos optimizados particionados por año/mes/día en la ruta de S3: `s3://<TU-BUCKET-NAME>/2silver/` utilizando el formato **Parquet**.
4. **Guardar y Ejecutar:** Guarda el Job como `marketmatrix-silver-transformation-job`. *Nota de Arquitectura: Conforme a nuestras decisiones de diseño para optimizar costos, este Job se ejecuta de manera manual o espaciada (fines de semana) para reducir un 1,000% el consumo del presupuesto dentro del AWS Free Tier.*

---

## 🔍 Paso 5: Consultas Analíticas y Reglas de Negocio (Amazon Athena)

Amazon Athena actuará como nuestro motor de analítica para la Capa Gold, procesando las consultas SQL de manera serverless sobre los archivos Parquet de la Capa Silver.

1. Ve a la consola de **Amazon Athena**.
2. **Configuración Inicial:** Antes de ejecutar tu primer query, ve a la pestaña **Settings** y configura un directorio en S3 para almacenar los resultados de las consultas (ej. `s3://<TU-BUCKET-NAME>/3gold/query-results/`).
3. **Creación de la Tabla de la Capa Silver:** Ejecuta un nuevo Crawler sobre la carpeta `2silver/` o define la tabla particionada directamente en Athena.
4. **Despliegue de la Vista de la Capa Gold:**
   * Copia y ejecuta el script SQL desarrollado en tu editor de Athena para generar la vista analítica que calcula los indicadores técnicos correlacionados: **RSI (14)**, **Bandas de Bollinger (20, 2)** y el **MACD (12, 26, 9)**.
   * La consulta implementará la **Regla de Triple Confirmación** para arrojar los estados automáticos de `COMPRA FUERTE`, `VENTA` o `MANTENER`.

---

## 🧪 Paso 6: Validación del Despliegue

Para comprobar que el pipeline de datos está completamente operativo de extremo a extremo, realiza la siguiente prueba integral:

1. Ve a tu AWS Lambda (`marketmatrix-extractor-lambda`) y realiza una ejecución de prueba manual (**Test**).
2. Verifica en la consola de S3 que se haya generado un nuevo archivo `.csv` dentro de la ruta `1bronze/year=2026/month=05/...`.
3. Ejecuta el Job de Glue para procesar dicho archivo. Confirma la aparición del archivo `.parquet` optimizado y comprimido en la carpeta `2silver/`.
4. Ve a Amazon Athena, realiza un `SELECT * FROM marketmatrix_db.vista_capa_gold ORDER BY fecha DESC LIMIT 10;` y confirma que los indicadores técnicos se calculen de manera inmediata y exacta sobre las particiones existentes.

---
*Cualquier anomalía o falla en las políticas de accesos o en la red externa puede ser monitoreada en tiempo real inspeccionando los flujos de logs generados automáticamente en **Amazon CloudWatch**.*