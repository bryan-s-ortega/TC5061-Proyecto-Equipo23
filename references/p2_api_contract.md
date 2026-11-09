# Contrato de la API P2 y Despliegue en Contenedor

## Propósito

`POST /predict` estima la clase de **presión neta de movimientos** de una
estación durante el siguiente intervalo de 30 minutos. No mide bicicletas
ni anclajes disponibles físicamente. Es un servicio de demostración académica.

## Esquema y Validación (Pydantic)

El esquema oficial está definido en `mibici/api/schemas.py`. Los nombres de las variables
coinciden exactamente con las utilizadas durante el entrenamiento del modelo.

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

Los conteos históricos deben calcularse únicamente con movimientos conocidos
**antes** del instante de predicción. La configuración `extra = "forbid"` rechaza cualquier campo no especificado con código HTTP `422 Unprocessable Entity`.

---

## Endpoints Disponibles

1. **`GET /`**: Información general de la API, enlaces a documentación interactiva Swagger (`/docs`) y ReDoc (`/redoc`).
2. **`GET /health`**: Chequeo de salud del servicio y verificación del estado del modelo (`healthy` / `unhealthy`).
3. **`GET /model/info`**: Metadatos descriptivos del modelo cargado (nombre oficial, versión/alias, tipo y lista de variables requeridas).
4. **`POST /predict`**: Predicción individual síncrona.
5. **`POST /predict/batch`**: Predicción por lote vectorizada para múltiples estaciones o intervalos simultáneos.

---

## Gobernanza y Trazabilidad con MLflow Model Registry

El modelo desplegado corresponde a la versión ganadora aprobada en la Entrega 2:
- **Nombre en Registry:** `MiBici_Equipo23_P2_Presion_Proxy_Academica`
- **Alias de Producción:** `@champion`
- **Registro Central:** DagsHub (`https://dagshub.com/bryan-s-ortega/TC5061-Proyecto-Equipo23.mlflow`)

Para extraer o actualizar el modelo champion directamente desde DagsHub hacia el repositorio local:

```bash
uv run python -m mibici.api.extract_model
```

---

## Contenedorización con `uv.lock`

El contenedor se gestiona mediante [Containerfile](../Containerfile) utilizando `uv` y `uv.lock` en lugar de archivos `requirements.txt` separados, garantizando builds deterministas y reproducibles.

### Construcción de la Imagen

```bash
task api:container:build
# o directamente:
docker build -t mibici-p2-api:latest -f Containerfile .
```

### Ejecución del Contenedor

```bash
task api:container:run
# o directamente:
docker run --rm -p 8000:8000 mibici-p2-api:latest
```

Una vez en ejecución, la documentación interactiva OpenAPI estará accesible en `http://localhost:8000/docs`.
