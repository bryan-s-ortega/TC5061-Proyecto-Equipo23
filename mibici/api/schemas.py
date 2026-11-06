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