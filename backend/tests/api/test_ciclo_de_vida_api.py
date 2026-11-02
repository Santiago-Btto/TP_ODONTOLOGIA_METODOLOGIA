"""Contrato HTTP de confirmación y cancelación (C-05) contra PostgreSQL real."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.modelos import HistorialModelo

URL = "/api/v1/turnos"


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


def crear(cliente: TestClient) -> str:
    respuesta = cliente.post(URL, json=cuerpo())
    assert respuesta.status_code == 201
    return str(respuesta.json()["id"])


def historiales(fabrica: sessionmaker[Session]) -> int:
    with fabrica() as sesion:
        return sesion.scalar(select(func.count()).select_from(HistorialModelo)) or 0


# Escenario: Confirmación por API
def test_confirmar_por_api_responde_200_con_estado_confirmado(cliente: TestClient) -> None:
    turno_id = crear(cliente)

    respuesta = cliente.post(f"{URL}/{turno_id}/confirmar")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "confirmado"
    assert respuesta.json()["inicio"] == "2030-01-10T12:00:00Z"


# Escenario: Cancelación por API y reutilización del horario
def test_cancelar_por_api_libera_el_horario_para_un_nuevo_alta(cliente: TestClient) -> None:
    turno_id = crear(cliente)

    cancelacion = cliente.post(f"{URL}/{turno_id}/cancelar")
    nuevo = cliente.post(URL, json=cuerpo())

    assert cancelacion.status_code == 200
    assert cancelacion.json()["estado"] == "cancelado"
    assert nuevo.status_code == 201


def test_confirmado_sigue_ocupando_el_horario_por_api(cliente: TestClient) -> None:
    turno_id = crear(cliente)
    assert cliente.post(f"{URL}/{turno_id}/confirmar").status_code == 200

    respuesta = cliente.post(URL, json=cuerpo(box_id="box-demo-002"))

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "conflicto_profesional"


# Escenario: Transición inválida por API
@pytest.mark.parametrize("previa,accion", [
    ("cancelar", "confirmar"), ("cancelar", "cancelar"), ("confirmar", "confirmar"),
])
def test_transicion_invalida_por_api_responde_409_sin_historial_nuevo(
    cliente: TestClient, fabrica: sessionmaker[Session], previa: str, accion: str
) -> None:
    turno_id = crear(cliente)
    assert cliente.post(f"{URL}/{turno_id}/{previa}").status_code == 200

    respuesta = cliente.post(f"{URL}/{turno_id}/{accion}")

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "transicion_invalida"
    assert historiales(fabrica) == 2


# Escenario: Turno inexistente por API
@pytest.mark.parametrize("accion", ["cancelar", "confirmar"])
def test_turno_inexistente_por_api_responde_404(cliente: TestClient, accion: str) -> None:
    respuesta = cliente.post(f"{URL}/turno-demo-inexistente/{accion}")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "recurso_inexistente"


def test_identificador_demasiado_largo_responde_422(cliente: TestClient) -> None:
    assert cliente.post(f"{URL}/{'x' * 65}/cancelar").status_code == 422


# Escenario: Turno cancelado identificado en la agenda
def test_agenda_informa_el_estado_de_cada_turno(cliente: TestClient) -> None:
    cancelado = crear(cliente)
    assert cliente.post(f"{URL}/{cancelado}/cancelar").status_code == 200
    confirmado = crear(cliente)
    assert cliente.post(f"{URL}/{confirmado}/confirmar").status_code == 200

    agenda = cliente.get("/api/v1/agenda", params={
        "inicio": "2030-01-10T08:00:00-03:00", "fin": "2030-01-10T12:00:00-03:00"}).json()

    assert {(t["id"], t["estado"]) for t in agenda} == {(cancelado, "cancelado"), (confirmado, "confirmado")}
