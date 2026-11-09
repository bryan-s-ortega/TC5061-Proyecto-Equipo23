# Evidencia de la API P2 en Docker

Prueba realizada el **8 de noviembre de 2026**, zona America/Mexico_City.

- Imagen: `mibici-p2-api:actividad8-olbap009`.
- Contenedor: `mibici-p2-api-actividad8-olbap009`.
- Publicación local: `127.0.0.1:18000` hacia el puerto `8000` del contenedor.
- Fuentes de la API y paquete del modelo: `a3384b4`, con la corrección de copia de
  `README.md` y `LICENSE` en el Containerfile. La documentación se completó después
  de ejecutar la imagen. No se afirma una construcción desde el commit final de
  esta evidencia, que todavía no existía al tomar las capturas.

## Resultados

| Comprobación | Resultado |
| --- | --- |
| Construcción de imagen | Finalizada sin errores |
| Salud y metadatos | HTTP 200 |
| Predicción con el ejemplo compartido | HTTP 200 |
| Capacidad inválida (`0`) | HTTP 422 |
| Predicción por lote | HTTP 200, dos resultados |
| Interfaz web | HTTP 200 y predicción visible |
| Pruebas de contrato y endpoints | 28 aprobadas, una advertencia |
| Modelo cargado | `DecisionTreeClassifier (MLflow Extracted Artifact)` |
| SHA-256 del modelo | Igual en el repositorio y en el contenedor |

La respuesta de la API muestra el alias `champion`. El manifiesto del paquete
identifica la versión numérica `1`. Se verificó la carga del paquete incluido en
la imagen; no se activó el fallback de demostración. No se modificó el Registry
remoto ni se reentrenó el modelo como parte de esta prueba. El manifiesto de
procedencia se consulta en `models/p2_champion/manifest.json`.

## Archivos

- [Captura de Docker y HTTP](docker_prediction.png).
- [Captura de la interfaz](api_ui.png).
- [Respuesta real](p2_response.json) y [salida de curl](curl_predict.txt).
- [Salud](health.json), [metadatos](model_info.json), [respuesta por lote](batch_response.json).
- [Entrada inválida](invalid_request.json) y [respuesta 422](invalid_response.json).
- [Salida de construcción](container_build.txt) y [pruebas de API](pytest_api.txt).
- [Identidad del contenedor](container.json), [versiones y hash](container_runtime.json).
- [Registro de verificación](http_verification.json), con imagen, códigos HTTP y hashes.
- [Visor utilizado para la captura](evidence_viewer.html) y [salida de docker ps](docker_ps.txt).

Los resultados JSON y de texto son salidas de ejecución reales. El visor solo
presenta esas salidas para poder capturarlas de manera legible; no genera una
respuesta de inferencia simulada. Las entradas utilizadas corresponden al ejemplo
público del contrato del equipo. Los archivos de las entregas anteriores se
conservan; no se incluyen credenciales ni datos de viajes individuales nuevos.
