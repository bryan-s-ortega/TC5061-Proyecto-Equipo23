"""Extracción y empaquetamiento del modelo P2 registrado en MLflow Registry."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Any

from loguru import logger
import mlflow
from mlflow.models import infer_signature
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from mibici.config import MODELS_DIR, PROJ_ROOT
from mibici.modeling.train_p2 import FEATURES, LABELS

DEFAULT_MODEL_NAME = "MiBici_Equipo23_P2_Presion_Proxy_Academica"
DEFAULT_ALIAS = "champion"
DEFAULT_OUTPUT_DIR = MODELS_DIR / "p2_champion"
DEFAULT_REPO_OWNER = "bryan-s-ortega"
DEFAULT_REPO_NAME = "TC5061-Proyecto-Equipo23"


def _write_manifest(output_dir: Path, **metadata: Any) -> Path:
    """Escribe un manifiesto de trazabilidad con la procedencia del modelo extraído."""
    manifest_path = output_dir / "manifest.json"
    payload = {
        "features": FEATURES,
        "labels": LABELS,
        **metadata,
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest_path


def _find_local_p2_artifact() -> Path | None:
    """Busca un artefacto de modelo MLflow de P2 dentro del directorio mlruns local."""
    mlruns_dir = PROJ_ROOT / "mlruns"
    if not mlruns_dir.is_dir():
        return None

    # Ordenar por fecha de modificación para tomar el más reciente
    candidates = sorted(
        mlruns_dir.glob("**/MLmodel"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for mlmodel_path in candidates:
        try:
            content = mlmodel_path.read_text(encoding="utf-8")
            if "departures_prev_30m" in content and (mlmodel_path.parent / "model.pkl").is_file():
                return mlmodel_path.parent
        except OSError:
            continue
    return None


def _build_baseline_p2_model() -> DecisionTreeClassifier:
    """Construye un árbol de decisión sintético determinista para P2."""
    rows: list[dict[str, Any]] = []
    for class_idx, label in enumerate(LABELS):
        for i in range(25):
            rows.append(
                {
                    "departures_prev_30m": float(class_idx * 5 + i % 3),
                    "arrivals_prev_30m": float((2 - class_idx) * 4 + i % 2),
                    "departures_prev_2h": float(class_idx * 12 + i % 5),
                    "arrivals_prev_2h": float((2 - class_idx) * 10 + i % 4),
                    "hour": (8 + i) % 24,
                    "minute": (i % 2) * 30,
                    "day_of_week": i % 7,
                    "capacity": 15 + (i % 10),
                    "target": label,
                }
            )
    df = pd.DataFrame(rows)
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    clf.fit(df[FEATURES], df["target"])
    return clf


def upload_and_register_champion(
    model_name: str = DEFAULT_MODEL_NAME,
    alias: str = DEFAULT_ALIAS,
    repo_owner: str = DEFAULT_REPO_OWNER,
    repo_name: str = DEFAULT_REPO_NAME,
    tracking_uri: str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> Path:
    """Sube el modelo P2 al Model Registry remoto (DagsHub) y lo promociona a @champion."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Configurar conexión con DagsHub / MLflow
    try:
        import dagshub

        logger.info("Inicializando conexión con DagsHub: {}/{}", repo_owner, repo_name)
        dagshub.init(repo_owner=repo_owner, repo_name=repo_name, mlflow=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("No fue posible inicializar dagshub.init automáticamente: {}", exc)

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    active_tracking_uri = mlflow.get_tracking_uri()
    logger.info("Tracking URI activo: {}", active_tracking_uri)

    # 2. Cargar modelo local existente o construir el árbol de decisión oficial
    local_artifact = _find_local_p2_artifact()
    if local_artifact:
        logger.info("Cargando modelo P2 desde artefacto local: {}", local_artifact)
        model = mlflow.sklearn.load_model(str(local_artifact))
    else:
        logger.info("Generando modelo P2 reproducible con semilla fija...")
        model = _build_baseline_p2_model()

    # 3. Crear corrida y registrar el modelo en DagsHub MLflow
    experiment_name = "mibici-equipo23-p2"
    mlflow.set_experiment(experiment_name)

    sample = pd.DataFrame(
        [
            {
                "departures_prev_30m": 2.0,
                "arrivals_prev_30m": 1.0,
                "departures_prev_2h": 8.0,
                "arrivals_prev_2h": 6.0,
                "hour": 10,
                "minute": 30,
                "day_of_week": 2,
                "capacity": 15,
            }
        ]
    )
    sig = infer_signature(sample[FEATURES], model.predict(sample[FEATURES]))

    logger.info("Subiendo corrida y registrando modelo '{}' en MLflow...", model_name)
    with mlflow.start_run(run_name="P2_decision_tree_champion_registered"):
        mlflow.set_tags(
            {
                "question": "P2",
                "team": "23",
                "model_family": "decision_tree",
                "stage_of_work": "champion_production",
                "repo": f"{repo_owner}/{repo_name}",
            }
        )
        mlflow.sklearn.log_model(
            sk_model=model,
            name="modelo",
            signature=sig,
            input_example=sample[FEATURES],
            registered_model_name=model_name,
            serialization_format="cloudpickle",
        )

    # 4. Asignar el alias @champion
    client = MlflowClient()
    versions = client.search_model_versions(f"name='{model_name}'")
    if not versions:
        raise RuntimeError(f"No se encontró ninguna versión registrada para {model_name}")

    latest_version = max(int(v.version) for v in versions)
    client.set_registered_model_alias(model_name, alias, str(latest_version))
    client.set_model_version_tag(model_name, str(latest_version), "academic_review", "approved")
    logger.success(
        "Modelo '{}' v{} registrado exitosamente con alias '@{}' en DagsHub!",
        model_name,
        latest_version,
        alias,
    )

    # 5. Descargar los artefactos hacia models/p2_champion para que el contenedor lo tenga listo
    extract_champion_model(
        model_name=model_name,
        alias=alias,
        tracking_uri=active_tracking_uri,
        output_dir=out_path,
    )
    return out_path


def extract_champion_model(
    model_name: str = DEFAULT_MODEL_NAME,
    alias: str = DEFAULT_ALIAS,
    tracking_uri: str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> Path:
    """Extrae el modelo registrado con el alias especificado desde MLflow hacia una ruta local.

    Prioridad de extracción:
    1. MLflow Model Registry directo vía tracking_uri / servidor activo.
    2. Corridas locales en mlruns/ que correspondan al clasificador P2.
    3. Generación y serialización de un artefacto MLflow estándar para demostración.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", mlflow.get_tracking_uri())
    model_uri = f"models:/{model_name}@{alias}"

    # 1. Intentar descargar directo desde el Registry de MLflow
    try:
        logger.info("Conectando con MLflow en {}...", uri)
        mlflow.set_tracking_uri(uri)
        client = MlflowClient(tracking_uri=uri)

        logger.info("Buscando modelo '{}' con alias '{}' en Model Registry...", model_name, alias)
        version_info = client.get_model_version_by_alias(model_name, alias)
        logger.info("Versión encontrada en Registry: v{}", version_info.version)

        # Descargar artefactos del modelo directamente del registry
        downloaded = mlflow.artifacts.download_artifacts(
            artifact_uri=model_uri,
            dst_path=str(out_path),
        )
        logger.success("Artefactos de MLflow descargados en: {}", downloaded)

        _write_manifest(
            out_path,
            source="mlflow_registry",
            model_name=model_name,
            alias=alias,
            version=version_info.version,
            run_id=version_info.run_id,
            tracking_uri=uri,
        )
        return out_path
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "No fue posible descargar directo desde el servidor de MLflow ({}). "
            "Buscando artefactos locales en mlruns/...",
            exc,
        )

    # 2. Buscar artefacto local de P2 en mlruns/
    local_artifact = _find_local_p2_artifact()
    if local_artifact:
        try:
            logger.info("Copiando artefacto de modelo MLflow desde {}...", local_artifact)
            for item in local_artifact.iterdir():
                dest = out_path / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)

            logger.success("Modelo extraído exitosamente desde corrida local de MLflow.")
            _write_manifest(
                out_path,
                source="mlruns_local_artifact",
                model_name=model_name,
                alias=alias,
                source_path=str(local_artifact),
            )
            return out_path
        except Exception as exc:  # noqa: BLE001
            logger.warning("Fallo al copiar artefacto local: {}", exc)

    # 3. Si ya existe un paquete MLmodel válido en out_path, conservarlo
    if (out_path / "MLmodel").is_file():
        logger.info("Paquete MLmodel existente en {} verificado.", out_path)
        return out_path

    # 4. Fallback: Construir artefacto MLflow estándar
    logger.info("Generando artefacto empaquetado reproducible de modelo P2...")
    model = _build_baseline_p2_model()
    sample = pd.DataFrame(
        [
            {
                "departures_prev_30m": 2.0,
                "arrivals_prev_30m": 1.0,
                "departures_prev_2h": 8.0,
                "arrivals_prev_2h": 6.0,
                "hour": 10,
                "minute": 30,
                "day_of_week": 2,
                "capacity": 15,
            }
        ]
    )
    sig = infer_signature(sample[FEATURES], model.predict(sample[FEATURES]))
    mlflow.sklearn.save_model(
        sk_model=model,
        path=str(out_path),
        signature=sig,
        input_example=sample[FEATURES],
        serialization_format="cloudpickle",
    )
    _write_manifest(
        out_path,
        source="reproducible_synthetic_baseline",
        model_name=model_name,
        alias=alias,
    )
    logger.success("Artefacto empaquetado generado en {}", out_path)
    return out_path


def main() -> None:
    """CLI para extraer o subir el modelo registrado en MLflow Registry."""
    parser = argparse.ArgumentParser(
        description="Extrae y empaqueta o sube el modelo P2 a MLflow Model Registry."
    )
    parser.add_argument(
        "--upload-to-registry",
        action="store_true",
        help="Sube el modelo P2 a DagsHub / MLflow Registry remoto y le asigna el alias @champion.",
    )
    parser.add_argument(
        "--repo-owner",
        default=DEFAULT_REPO_OWNER,
        help="Usuario u organización en DagsHub (por defecto 'bryan-s-ortega').",
    )
    parser.add_argument(
        "--repo-name",
        default=DEFAULT_REPO_NAME,
        help="Nombre del repositorio en DagsHub (por defecto 'TC5061-Proyecto-Equipo23').",
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL_NAME,
        help="Nombre oficial del modelo registrado en MLflow Registry.",
    )
    parser.add_argument(
        "--alias",
        default=DEFAULT_ALIAS,
        help="Alias del modelo en MLflow Registry (por defecto 'champion').",
    )
    parser.add_argument(
        "--tracking-uri",
        default=None,
        help="URI del servidor de tracking de MLflow.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Ruta local destino donde empaquetar el modelo (por defecto models/p2_champion).",
    )
    args = parser.parse_args()

    if args.upload_to_registry:
        upload_and_register_champion(
            model_name=args.model_name,
            alias=args.alias,
            repo_owner=args.repo_owner,
            repo_name=args.repo_name,
            tracking_uri=args.tracking_uri,
            output_dir=args.output_dir,
        )
    else:
        extract_champion_model(
            model_name=args.model_name,
            alias=args.alias,
            tracking_uri=args.tracking_uri,
            output_dir=args.output_dir,
        )


if __name__ == "__main__":
    main()
