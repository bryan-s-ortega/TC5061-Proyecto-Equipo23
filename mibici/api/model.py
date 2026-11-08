"""Servicio de carga e inferencia para el modelo P2 (Presión en Estaciones)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from loguru import logger
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from mibici.api.schemas import (
    ModelInfoResponse,
    P2PredictionRequest,
    P2PredictionResponse,
    PrediccionP2,
)
from mibici.config import MODELS_DIR
from mibici.modeling.train_p2 import FEATURES, LABELS

DEFAULT_MODEL_NAME = "MiBici_Equipo23_P2_Presion_Proxy_Academica"
DEFAULT_MODEL_VERSION = "champion"
DEFAULT_MODEL_URI = f"models:/{DEFAULT_MODEL_NAME}@{DEFAULT_MODEL_VERSION}"


class ModelService:
    """Administra la carga, almacenamiento en caché e inferencia del modelo P2."""

    def __init__(
        self,
        model_name: str | None = None,
        model_version: str | None = None,
        model_uri: str | None = None,
    ) -> None:
        self.model_name = model_name or os.getenv("MODEL_NAME", DEFAULT_MODEL_NAME)
        self.model_version = model_version or os.getenv("MODEL_VERSION", DEFAULT_MODEL_VERSION)
        self.model_uri = model_uri or os.getenv("MODEL_URI", DEFAULT_MODEL_URI)
        self.model: Any = None
        self.model_type: str = "Uninitialized"
        self._is_fallback: bool = False

    def load_model(self) -> None:
        """Intenta cargar el modelo desde MLflow, archivo local o genera fallback."""
        # 1. Intentar cargar desde ruta local especificada en MODEL_PATH
        local_path = os.getenv("MODEL_PATH")
        if local_path and Path(local_path).is_file():
            try:
                import joblib

                self.model = joblib.load(local_path)
                self.model_type = type(self.model).__name__
                self._is_fallback = False
                logger.info("Modelo P2 cargado exitosamente desde archivo local: {}", local_path)
                return
            except (OSError, ValueError, TypeError) as e:
                logger.warning("Fallo al cargar modelo local {}: {}", local_path, e)

        # 2. Intentar cargar desde archivo estándar en directorio models/
        default_local = MODELS_DIR / "p2_decision_tree.joblib"
        if default_local.is_file():
            try:
                import joblib

                self.model = joblib.load(default_local)
                self.model_type = type(self.model).__name__
                self._is_fallback = False
                logger.info("Modelo P2 cargado desde {}", default_local)
                return
            except (OSError, ValueError, TypeError) as e:
                logger.warning("Fallo al cargar modelo de {}: {}", default_local, e)

        # 3. Intentar cargar desde MLflow Model Registry
        try:
            import mlflow.sklearn

            logger.info("Intentando cargar modelo P2 desde MLflow URI: {}", self.model_uri)
            self.model = mlflow.sklearn.load_model(self.model_uri)
            self.model_type = type(self.model).__name__
            self._is_fallback = False
            logger.success("Modelo P2 cargado exitosamente desde MLflow: {}", self.model_uri)
            return
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "No fue posible cargar el modelo desde MLflow ({}). "
                "Causas comunes: servidor no iniciado o entorno sin conexión.",
                e,
            )

        # 4. Fallback determinista en memoria para entornos aislados / pruebas
        logger.info("Inicializando modelo P2 fallback de demostración académica...")
        self.model = self._create_fallback_model()
        self.model_type = f"{type(self.model).__name__} (In-Memory Fallback)"
        self._is_fallback = True
        logger.success("Modelo fallback listo para inferencia en modo demostración.")

    def _create_fallback_model(self) -> DecisionTreeClassifier:
        """Crea un clasificador entrenado con datos sintéticos representativos de P2."""
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

    @property
    def is_loaded(self) -> bool:
        """Verifica si el modelo está instanciado y listo para inferencia."""
        return self.model is not None

    def predict(self, request: P2PredictionRequest) -> P2PredictionResponse:
        """Realiza inferencia sobre una instancia de predicción."""
        if not self.is_loaded:
            self.load_model()

        input_data = pd.DataFrame([request.model_dump()])[FEATURES]
        raw_prediction = self.model.predict(input_data)[0]

        prediction_label: PrediccionP2
        if raw_prediction in LABELS:
            prediction_label = raw_prediction
        else:
            prediction_label = "sin_presion_neta_elevada"

        return P2PredictionResponse(
            prediction=prediction_label,
            model_name=self.model_name,
            model_version=self.model_version,
        )

    def predict_batch(self, requests: list[P2PredictionRequest]) -> list[P2PredictionResponse]:
        """Realiza inferencia vectorizada sobre un lote de peticiones."""
        if not self.is_loaded:
            self.load_model()

        input_data = pd.DataFrame([r.model_dump() for r in requests])[FEATURES]
        raw_predictions = self.model.predict(input_data)

        responses = []
        for pred in raw_predictions:
            label: PrediccionP2 = pred if pred in LABELS else "sin_presion_neta_elevada"
            responses.append(
                P2PredictionResponse(
                    prediction=label,
                    model_name=self.model_name,
                    model_version=self.model_version,
                )
            )
        return responses

    def get_info(self) -> ModelInfoResponse:
        """Retorna información descriptiva del modelo cargado."""
        if not self.is_loaded:
            self.load_model()

        return ModelInfoResponse(
            model_name=self.model_name,
            model_version=self.model_version,
            model_type=self.model_type,
            features=FEATURES,
            labels=LABELS,
        )


# Singleton del servicio de inferencia
model_service = ModelService()


def get_model_service() -> ModelService:
    """Dependency provider para inyección en FastAPI."""
    if not model_service.is_loaded:
        model_service.load_model()
    return model_service
