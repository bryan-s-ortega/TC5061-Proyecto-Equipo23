# MiBici P2: estimación del costo por inferencia

## Alcance

Se estima el costo de operar en una sola instancia la API de P2,
PostgreSQL, Grafana y Nginx, según el Docker Compose del proyecto.
La unidad de costo es una predicción válida de P2. En `POST /predict`,
cada respuesta válida cuenta como una inferencia. Si se evalúa
`/predict/batch`, se cuentan predicciones válidas, no peticiones HTTP.

## Evidencia necesaria

- Locust: duración de cada tramo estable, inferencias válidas, tasa
  de errores y latencia p95 (el tiempo dentro del cual termina el 95 %
  de las peticiones). Excluir el calentamiento del cálculo.
- Docker stats: CPU y memoria de cada servicio durante ese mismo tramo.
  Registrar también el hardware de prueba y dónde se ejecutó Locust,
  porque si comparte máquina con los servicios consume recursos.
- Precio de referencia: proveedor, región, tipo de instancia, vCPU,
  RAM, tarifa, moneda, fecha de consulta y enlace oficial. Usar CPU y
  memoria medidas para justificar el tamaño estimado de la instancia.
  Si la carga se ejecutó en otro hardware, identificar el costo como
  proyección y no asumir que el rendimiento en nube será idéntico.

## Cálculo 1: costo bajo carga sostenida

1. Inferencias válidas por segundo = inferencias válidas del tramo /
   segundos del tramo.
2. Costo por millón de inferencias = tarifa por hora /
   (3,600 × inferencias válidas por segundo) × 1,000,000.

Usar el tramo de mayor carga que cumpla los límites de p95 y error
acordados antes de interpretar la prueba. Registrar esos límites y
los valores realmente observados.

## Cálculo 2: costo mensual al volumen esperado

1. Costo mensual = tarifa por hora × horas encendidas al mes +
   almacenamiento y otros cargos incluidos en el escenario.
2. Costo por millón de inferencias = costo mensual /
   inferencias válidas mensuales × 1,000,000.

Para operación 24/7, usar 730 horas como supuesto mensual. Mostrar
un escenario de demanda baja y otro de demanda alta. Si no existe
tráfico real, declarar ambos volúmenes como supuestos. Indicar qué
cargos quedaron fuera y evitar sumar un recurso ya incluido en la tarifa.

## Cómo justificar una optimización

- Si sobra CPU y memoria, probar una instancia menor y repetir la carga
  antes de recomendar el cambio.
- Si las solicitudes se pueden agrupar, comparar `/predict` con
  `/predict/batch` en inferencias válidas por segundo y p95.
- Si el servicio queda ocioso muchas horas y no requiere operar 24/7,
  estimar el ahorro de un horario de operación más corto.

Resultados pendientes: incorporar las mediciones de Locust y Docker stats
y el precio oficial antes de presentar una cifra de costo.
