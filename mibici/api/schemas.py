"""Contrato de entrada y salida para la predicción P2."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PrediccionP2 = Literal[
    "sin_presion_neta_elevada",
    "presion_sin_bicicletas",
    "presion_sin_anclajes",
]


class P2PredictionRequest(BaseModel):
    """Variables disponibles al comenzar un intervalo de 30 minutos."""

    model_config = ConfigDict(extra="forbid")

    departures_prev_30m: int = Field(ge=0)
    arrivals_prev_30m: int = Field(ge=0)
    departures_prev_2h: int = Field(ge=0)
    arrivals_prev_2h: int = Field(ge=0)
    hour: int = Field(ge=0, le=23)
    minute: Literal[0, 30]
    day_of_week: int = Field(ge=0, le=6)
    capacity: int = Field(gt=0)


class P2PredictionResponse(BaseModel):
    """Clase predicha y modelo que produjo la respuesta."""

    prediction: PrediccionP2
    model_name: str
    model_version: str


class HealthResponse(BaseModel):
    """Estado de salud de la API y disponibilidad del modelo."""

    status: str = Field(description="Estado de la aplicación (e.g. 'healthy')")
    model_loaded: bool = Field(description="Indica si el modelo de ML está cargado")
    model_name: str = Field(description="Nombre del modelo configurado")
    model_version: str = Field(description="Versión o alias del modelo")


class ModelInfoResponse(BaseModel):
    """Metadatos del modelo cargado y contrato de inferencia."""

    model_name: str
    model_version: str
    model_type: str
    features: list[str]
    labels: list[str]
    academic_proxy_note: str = (
        "Estimación proxy de presión neta basada en flujos, no disponibilidad física real."
    )


class BatchP2PredictionRequest(BaseModel):
    """Lista de peticiones para inferencia por lotes."""

    instances: list[P2PredictionRequest] = Field(min_length=1)


class BatchP2PredictionResponse(BaseModel):
    """Lista de predicciones producidas."""

    predictions: list[P2PredictionResponse]
