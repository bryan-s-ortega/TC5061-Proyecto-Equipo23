# Contrato propuesto de la API P2

## Propósito

`POST /predict` estima la clase de **presión neta de movimientos** de una
estación durante el siguiente intervalo de 30 minutos. No mide bicicletas
ni anclajes disponibles físicamente. Es un servicio de demostración académica.

## Entrada JSON

El esquema está definido en `mibici/api/schemas.py`. Los nombres deben
coincidir exactamente con las variables usadas al entrenar el modelo.

| Campo | Significado | Validación |
| --- | --- | --- |
| `departures_prev_30m` | Salidas en los 30 minutos anteriores | Entero ≥ 0 |
| `arrivals_prev_30m` | Llegadas en los 30 minutos anteriores | Entero ≥ 0 |
| `departures_prev_2h` | Salidas en las dos horas anteriores | Entero ≥ 0 |
| `arrivals_prev_2h` | Llegadas en las dos horas anteriores | Entero ≥ 0 |
| `hour` | Hora local del inicio del intervalo | 0 a 23 |
| `minute` | Minuto del inicio del intervalo | 0 o 30 |
| `day_of_week` | Día de la semana; lunes = 0 | 0 a 6 |
| `capacity` | Capacidad de anclajes de la estación | Entero > 0 |

Los conteos históricos deben calcularse sólo con movimientos conocidos
**antes** del instante de predicción. No se aceptan campos adicionales.

### Petición de ejemplo

```json
{
  "departures_prev_30m": 2,
  "arrivals_prev_30m": 1,
  "departures_prev_2h": 8,
  "arrivals_prev_2h": 6,
  "hour": 10,
  "minute": 30,
  "day_of_week": 2,
  "capacity": 15
}