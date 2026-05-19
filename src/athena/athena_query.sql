CREATE OR REPLACE VIEW "gold_prediction" AS 
SELECT 
    fecha,
    precio,
    CASE 
        WHEN rsi <= 30 THEN 'SOBREVENDIDO (Oportunidad)'
        WHEN rsi >= 70 THEN 'SOBRECOMPRADO (Riesgo)'
        ELSE 'NEUTRAL'
    END AS estado_rsi,
    CASE 
        WHEN precio <= bollinger_baja THEN 'PRECIO BAJO (Soporte)'
        WHEN precio >= bollinger_alta THEN 'PRECIO ALTO (Resistencia)'
        ELSE 'RANGO NORMAL'
    END AS posicion_bollinger,
    CASE 
        WHEN rsi <= 35 AND precio <= (bollinger_baja * 1.02) AND macd_linea > macd_senal 
             THEN 'COMPRA FUERTE'
        WHEN rsi >= 65 AND precio >= (bollinger_alta * 0.98) AND macd_linea < macd_senal 
             THEN 'VENTA / TOMA GANANCIAS'
        ELSE 'MANTENER / ESPERAR'
    END AS recomendacion_algoritmica
FROM "glue-2silver"."silver_table"
WHERE macd_linea IS NOT NULL

