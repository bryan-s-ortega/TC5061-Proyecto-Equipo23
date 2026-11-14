# P2: análisis preliminar de los periodos

## Fuente y cortes

Archivo: `data/processed/p2_examples.parquet`. Se filtró por
`prediction_time` con inicio inclusivo y fin exclusivo:

- Referencia: `split=train`, 2025-07-01 a 2025-10-01.
- Periodo posterior: `split=test`, 2026-07-01 a 2026-10-01.

La clase «presión» agrupa `presion_sin_bicicletas` y
`presion_sin_anclajes`. Es una etiqueta proxy de movimientos netos,
no una medición de inventario físico.

## Resultados descriptivos

| Grupo | Filas | Estaciones | Casos de presión | Tasa |
| --- | ---: | ---: | ---: | ---: |
| Referencia, todas | 1,620,407 | 367 | 11,565 | 0.714 % |
| Periodo posterior, todas | 2,010,909 | 469 | 9,487 | 0.472 % |
| Periodo posterior, 367 estaciones compartidas | 1,614,080 | 367 | 9,250 | 0.573 % |
| Periodo posterior, 102 estaciones ausentes en referencia | 396,829 | 102 | 237 | 0.060 % |

En las estaciones compartidas, la tasa pasó de 0.714 % a 0.573 %:
una caída de 0.141 puntos porcentuales, cercana al 20 % relativo.
En el total pasó de 0.714 % a 0.472 %. Aproximadamente 58 % de la
diferencia total se observa al comparar las estaciones compartidas;
el 42 % restante se asocia, en esta descomposición descriptiva, con
la incorporación al conjunto de estaciones de muy baja tasa.

«Ausentes en referencia» no demuestra que sean estaciones recién
instaladas. La diferencia de tasas tampoco demuestra por sí sola
drift estadístico en las variables ni deterioro del modelo.

## Siguiente comprobación

Generar Evidently sobre las ocho variables predictoras para ambos
periodos. Además del reporte general, considerar una comparación
restringida a las 367 estaciones compartidas. Evaluar las versiones
A y B sobre las mismas filas posteriores antes de recomendar un cambio.
