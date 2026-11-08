# API REST de P2: guía de despliegue

**Estado: borrador para integración.** Esta guía se prepara sobre `main`, commit
`707f961`. Están integrados el contrato Pydantic y el Containerfile inicial; falta
la aplicación `mibici/api/main.py`. Los comandos siguientes se deben verificar
cuando esté integrada la API. No se han construido ni ejecutado contenedores como
parte de esta contribución y todavía no se publica una respuesta real de inferencia.

## Propósito y estrategia de despliegue

La API de MiBici atenderá una petición `POST /predict` con las variables de una
estación y devolverá su clase de presión neta de movimientos para el siguiente
intervalo de 30 minutos. Se propone **inferencia en tiempo real**, porque el
consumidor puede solicitar una predicción con las variables disponibles al
comenzar cada intervalo y recibir una respuesta inmediata, sin esperar un proceso
por lotes.

El resultado es un indicador proxy calculado a partir de movimientos: no demuestra
que una estación esté físicamente vacía o llena. La elección describe el modo de
consumo propuesto; aún no hay mediciones de latencia del servicio.

## Modelo y requisitos de integración

La referencia de P2 registrada por el proyecto es
`MiBici_Equipo23_P2_Presion_Proxy_Academica`. Para la integración se propone cargar
el modelo desde MLflow al iniciar el servicio, usando el alias `champion`:

```text
models:/MiBici_Equipo23_P2_Presion_Proxy_Academica@champion
```

La ubicación del servidor se configura mediante `MLFLOW_TRACKING_URI`. El servidor
y el almacenamiento de artefactos deben ser accesibles desde el contenedor y el
alias debe existir en esa instancia. La respuesta debe identificar la versión
efectivamente cargada; el nombre de alias por sí solo no identifica una versión
inmutable. Si la integración elige empaquetar un modelo descargado del Registry,
debe documentar esa opción y su versión antes de cerrar esta guía.

Antes de validar el servicio, confirmar:

- La aplicación FastAPI exporta `app` desde el módulo que utiliza el Containerfile.
- El endpoint conecta el esquema con el modelo y conserva el orden/nombres de las
  ocho variables de entrenamiento.
- El Containerfile y el entorno de inferencia usan las dependencias acordadas con
  el `uv.lock` del proyecto. El Containerfile inicial usa Python 3.11 y
  `requirements-api.txt`, mientras el proyecto declara Python 3.13; la integración
  de dependencias aún está pendiente.
- Se dispone de Podman y de acceso al servidor y los artefactos de MLflow. En
  macOS o Windows, la máquina virtual de Podman debe estar iniciada.

## Contrato de entrada y salida

El contrato de Miguel está en
[`mibici/api/schemas.py`](../mibici/api/schemas.py), con su explicación en
[`references/p2_api_contract.md`](../references/p2_api_contract.md).

| Campo de entrada | Restricción |
| --- | --- |
| `departures_prev_30m` | Entero mayor o igual a cero |
| `arrivals_prev_30m` | Entero mayor o igual a cero |
| `departures_prev_2h` | Entero mayor o igual a cero |
| `arrivals_prev_2h` | Entero mayor o igual a cero |
| `hour` | Entero de 0 a 23 |
| `minute` | 0 o 30 |
| `day_of_week` | Entero de 0 a 6; lunes = 0 |
| `capacity` | Entero mayor que cero |

No se aceptan campos adicionales. Los conteos históricos deben calcularse con
movimientos conocidos antes del instante de predicción.

La petición compartida para la prueba está en
[`examples/p2_prediction_request.json`](../examples/p2_prediction_request.json):

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
```

El esquema de salida exige:

| Campo | Contenido |
| --- | --- |
| `prediction` | `sin_presion_neta_elevada`, `presion_sin_bicicletas` o `presion_sin_anclajes` |
| `model_name` | Nombre del modelo utilizado |
| `model_version` | Versión del modelo cargado, como cadena |

**Respuesta de ejemplo pendiente:** se añadirá la respuesta obtenida del modelo
real al ejecutar la petición en el contenedor. La clase no se puede deducir del
contrato y no se sustituye por una predicción inventada.

## Construcción y ejecución previstas con Podman

Ejecutar desde la raíz del repositorio **después de integrar la API y resolver sus
dependencias**. Estos son los comandos propuestos para la prueba local:

```bash
podman build -f Containerfile -t mibici-p2-api:actividad8 .
```

En otra terminal, iniciar el contenedor. La siguiente URI es un ejemplo para un
servidor del anfitrión en el puerto 5001; ajustarla a la instancia real accesible:

```bash
export MLFLOW_TRACKING_URI_CONTENEDOR="http://host.containers.internal:5001"

podman run --rm --name mibici-p2-api \
  -p 127.0.0.1:8000:8000 \
  -e MLFLOW_TRACKING_URI="$MLFLOW_TRACKING_URI_CONTENEDOR" \
  mibici-p2-api:actividad8
```

`MLFLOW_TRACKING_URI_CONTENEDOR` es una variable auxiliar del shell; dentro del
contenedor se entrega como `MLFLOW_TRACKING_URI`. Podman proporciona normalmente
el nombre `host.containers.internal` para llegar al anfitrión. Su resolución y la
conectividad dependen de la red y, en macOS/Windows, de la máquina virtual. Un
servidor que solo escucha en una interfaz inaccesible desde esa red no podrá
utilizarse mediante esta URI. Confirmar el acceso antes de atribuir un fallo al
modelo.

El puerto de la API se publica únicamente en la interfaz local del anfitrión para
esta demostración. La estrategia final de acceso al Registry debe quedar alineada
con la implementación que integre el equipo.

## Petición de prueba y evidencia pendiente

Con el contenedor ejecutándose, comprobar que aparece activo y enviar el JSON:

```bash
podman ps --filter name=mibici-p2-api

curl --fail-with-body -i \
  -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  --data-binary @examples/p2_prediction_request.json
```

Comprobar un estado HTTP 200 y una respuesta que cumpla el esquema de salida,
con el nombre y la versión reales. Una respuesta de error o un contenedor que
termina inmediatamente no acreditan el funcionamiento del servicio.

Para completar la entrega, guardar en `reports/evidence/api/`:

1. La respuesta JSON real y el commit de código utilizado.
2. Una captura legible que muestre el contenedor activo y la petición HTTP con su
   respuesta. La captura debe corresponder a Podman, no a una API ejecutada solo
   fuera del contenedor.
3. El nombre de imagen, versiones de Python y dependencias de inferencia, modelo
   y versión resuelta, y los comandos que efectivamente funcionaron.

Después, añadir la respuesta y la captura a esta guía y verificar nuevamente los
comandos contra el Containerfile final. Hasta entonces, esta sección permanece
pendiente de validación.

Para finalizar la demostración local:

```bash
podman stop mibici-p2-api
```

## Contribución y continuidad

Esta documentación y el JSON reutilizable son la aportación inicial de
Juan Pablo Islas Guzmán (A01797727 / `Olbap009`), preparados con apoyo de Codex.
Se basan en el contrato aportado por Miguel, el contenedor inicial de Kevin y la
integración de API anunciada por Bryan. La respuesta y las capturas se completarán
cuando pueda verificarse el servicio integrado.

## Referencias técnicas

- [Model Registry de MLflow: carga de modelos y aliases](https://mlflow.org/docs/latest/model-registry).
- [Podman: ejecución y configuración de red del contenedor](https://docs.podman.io/en/latest/markdown/podman-run.1.html).
