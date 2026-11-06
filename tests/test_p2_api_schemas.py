"""Pruebas del contrato de entrada y salida de la API P2."""

import pytest
from pydantic import ValidationError

from mibici.api.schemas import P2PredictionRequest, P2PredictionResponse


@pytest.fixture
def entrada_valida():
    return {
        "departures_prev_30m": 2,
        "arrivals_prev_30m": 1,
        "departures_prev_2h": 8,
        "arrivals_prev_2h": 6,
        "hour": 10,
        "minute": 30,
        "day_of_week": 2,
        "capacity": 15,
    }


def test_acepta_entrada_valida(entrada_valida):
    request = P2PredictionRequest(**entrada_valida)
    assert request.capacity == 15
    assert request.minute == 30


@pytest.mark.parametrize(
    "cambio",
    [
        {"capacity": 0},
        {"hour": 24},
        {"minute": 15},
        {"departures_prev_30m": -1},
        {"day_of_week": 7},
        {"campo_desconocido": 1},
    ],
)
def test_rechaza_entrada_invalida(entrada_valida, cambio):
    with pytest.raises(ValidationError):
        P2PredictionRequest(**{**entrada_valida, **cambio})


def test_acepta_salida_con_clase_conocida():
    response = P2PredictionResponse(
        prediction="sin_presion_neta_elevada",
        model_name="MiBici_Equipo23_P2_Presion_Proxy_Academica",
        model_version="1",
    )
    assert response.prediction == "sin_presion_neta_elevada"


def test_rechaza_salida_con_clase_desconocida():
    with pytest.raises(ValidationError):
        P2PredictionResponse(
            prediction="sin_bicicletas_observadas",
            model_name="MiBici_Equipo23_P2_Presion_Proxy_Academica",
            model_version="1",
        )
