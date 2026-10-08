"""Escenarios de `Exponer el alta por API HTTP` contra PostgreSQL real."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.main import crear_app

URL = "/api/v1/turnos"


@pytest.fixture
def cliente(fabrica: sessionmaker[Session]) -> Iterator[TestClient]:
    with TestClient(crear_app(fabrica)) as cliente:
        yield cliente


def cuerpo(**cambios: str) -> dict[str, str]:
    base = {
        "paciente_id": "paciente-demo-001",
        "profesional_id": "profesional-demo-001",
        "box_id": "box-demo-001",
        "prestacion_id": "prestacion-demo-001",
        "inicio": "2030-01-10T09:00:00-03:00",
    }
    base.update(cambios)
    return base


# Escenario: Alta por API
def test_alta_por_api_responde_201_con_el_turno(cliente: TestClient) -> None:
    respuesta = cliente.post(URL, json=cuerpo())

    assert respuesta.status_code == 201
    turno = respuesta.json()
    assert turno["id"]
    assert turno["estado"] == "programado"
    assert turno["inicio"] == "2030-01-10T12:00:00Z"
    assert turno["fin"] == "2030-01-10T12:30:00Z"


# Escenario: Conflicto por API
def test_conflicto_de_profesional_por_api_responde_409(cliente: TestClient) -> None:
    assert cliente.post(URL, json=cuerpo(box_id="box-demo-002")).status_code == 201

    respuesta = cliente.post(URL, json=cuerpo(inicio="2030-01-10T09:15:00-03:00"))

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "conflicto_profesional"


def test_conflicto_de_box_por_api_responde_409(cliente: TestClient) -> None:
    assert cliente.post(URL, json=cuerpo(profesional_id="profesional-demo-002")).status_code == 201

    respuesta = cliente.post(URL, json=cuerpo(inicio="2030-01-10T09:15:00-03:00"))

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "conflicto_box"


def test_turno_contiguo_por_api_responde_201(cliente: TestClient) -> None:
    assert cliente.post(URL, json=cuerpo()).status_code == 201

    assert cliente.post(URL, json=cuerpo(inicio="2030-01-10T09:30:00-03:00")).status_code == 201


# Escenario: Intervalo inválido por API
def test_intervalo_invalido_por_api_responde_422(cliente: TestClient) -> None:
    respuesta = cliente.post(URL, json=cuerpo(fin="2030-01-10T09:00:00-03:00"))

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "intervalo_invalido"


def test_fecha_sin_zona_horaria_responde_422(cliente: TestClient) -> None:
    assert cliente.post(URL, json=cuerpo(inicio="2030-01-10T09:00:00")).status_code == 422


# Escenario: Recurso inexistente por API
def test_recurso_inexistente_por_api_responde_404(cliente: TestClient) -> None:
    respuesta = cliente.post(URL, json=cuerpo(box_id="box-que-no-existe"))

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "recurso_inexistente"


def test_health_informa_api_y_base_disponibles(cliente: TestClient) -> None:
    respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "base_de_datos": "ok"}
