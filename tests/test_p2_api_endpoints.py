"""Pruebas de integración de los endpoints de la API FastAPI para P2."""

from fastapi.testclient import TestClient
import pytest

from mibici.api.main import app
from mibici.modeling.train_p2 import FEATURES, LABELS

client = TestClient(app)


@pytest.fixture
def valid_payload():
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


def test_root_endpoint():
    """El endpoint raíz debe devolver metadatos de la API y enlaces de documentación."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert data["documentation"] == "/docs"
    assert data["interactive_ui"] == "/ui"
    assert data["health"] == "/health"
    assert data["status"] == "online"


def test_ui_endpoint():
    """El endpoint /ui debe devolver la interfaz web interactiva en HTML."""
    response = client.get("/ui")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "MiBici — Inferencia de Presión en Estaciones" in response.text
    assert "predict-form" in response.text


def test_root_browser_negotiation():
    """Al solicitar text/html en raíz se entrega la interfaz web."""
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "MiBici — Inferencia de Presión en Estaciones" in response.text


def test_health_endpoint():
    """El health check debe confirmar que el servicio y el modelo están listos."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "model_name" in data
    assert "model_version" in data


def test_model_info_endpoint():
    """El endpoint /model/info debe describir las variables y clases del contrato."""
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["features"] == FEATURES
    assert data["labels"] == LABELS
    assert "model_type" in data


def test_predict_endpoint_valid_request(valid_payload):
    """POST /predict debe responder con una predicción válida del contrato."""
    response = client.post("/predict", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in LABELS
    assert "model_name" in data
    assert "model_version" in data


@pytest.mark.parametrize(
    "invalid_patch,field_error",
    [
        ({"capacity": 0}, "capacity"),
        ({"capacity": -5}, "capacity"),
        ({"hour": 24}, "hour"),
        ({"hour": -1}, "hour"),
        ({"minute": 15}, "minute"),
        ({"minute": 45}, "minute"),
        ({"day_of_week": 7}, "day_of_week"),
        ({"departures_prev_30m": -1}, "departures_prev_30m"),
        ({"arrivals_prev_2h": -2}, "arrivals_prev_2h"),
        ({"campo_extra": "no_permitido"}, "campo_extra"),
    ],
)
def test_predict_endpoint_rejects_invalid_inputs(valid_payload, invalid_patch, field_error):
    """POST /predict debe rechazar con HTTP 422 cualquier entrada que viole el esquema."""
    payload = {**valid_payload, **invalid_patch}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_predict_endpoint_rejects_missing_fields():
    """POST /predict debe rechazar peticiones incompletas."""
    incomplete_payload = {
        "departures_prev_30m": 1,
        "arrivals_prev_30m": 1,
    }
    response = client.post("/predict", json=incomplete_payload)
    assert response.status_code == 422


def test_predict_batch_endpoint_valid(valid_payload):
    """POST /predict/batch debe realizar inferencia para múltiples estaciones."""
    batch_payload = {
        "instances": [
            valid_payload,
            {**valid_payload, "hour": 18, "minute": 0, "capacity": 20},
        ]
    }
    response = client.post("/predict/batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 2
    for pred in data["predictions"]:
        assert pred["prediction"] in LABELS


def test_predict_batch_rejects_empty_instances():
    """POST /predict/batch debe rechazar listas vacías."""
    response = client.post("/predict/batch", json={"instances": []})
    assert response.status_code == 422
