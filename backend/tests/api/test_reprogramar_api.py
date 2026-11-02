"""Contrato HTTP de `PATCH /api/v1/turnos/{id}` (C-04) contra PostgreSQL real."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.modelos import HistorialModelo, TurnoModelo

URL = "/api/v1/turnos"


def crear(cliente: TestClient, **cambios: str) -> str:
    datos = {
        "paciente_id": "paciente-demo-001", "profesional_id": "profesional-demo-001",
        "box_id": "box-demo-001", "prestacion_id": "prestacion-demo-001",
        "inicio": "2030-01-10T09:00:00-03:00",
    }
    datos.update(cambios)
    respuesta = cliente.post(URL, json=datos)
    assert respuesta.status_code == 201
    return str(respuesta.json()["id"])


def intervalo_y_eventos(fabrica: sessionmaker[Session], turno_id: str) -> tuple[str, str, int]:
    with fabrica() as sesion:
        fila = sesion.get(TurnoModelo, turno_id)
        assert fila is not None
        eventos = sesion.scalar(select(func.count()).select_from(HistorialModelo)
                                .where(HistorialModelo.turno_id == turno_id)) or 0
        return fila.inicio.isoformat(), fila.box_id, eventos


# Escenario: Reprogramación por API
def test_reprogramar_por_api_responde_200_con_el_nuevo_intervalo(cliente: TestClient) -> None:
    turno_id = crear(cliente)

    respuesta = cliente.patch(f"{URL}/{turno_id}", json={"inicio": "2030-01-10T11:00:00-03:00"})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert (cuerpo["id"], cuerpo["inicio"], cuerpo["fin"], cuerpo["estado"]) == (
        turno_id, "2030-01-10T14:00:00Z", "2030-01-10T14:30:00Z", "programado")


def test_reprogramar_recursos_y_reutilizar_el_horario_anterior(cliente: TestClient) -> None:
    turno_id = crear(cliente)

    respuesta = cliente.patch(f"{URL}/{turno_id}",
                              json={"profesional_id": "profesional-demo-002", "box_id": "box-demo-002"})

    assert respuesta.status_code == 200
    assert (respuesta.json()["profesional_id"], respuesta.json()["box_id"]) == (
        "profesional-demo-002", "box-demo-002")
    crear(cliente)  # el profesional y box originales quedaron libres


# Escenario: Conflicto por API
@pytest.mark.parametrize("otro,codigo", [
    ({"box_id": "box-demo-002"}, "conflicto_profesional"),
    ({"profesional_id": "profesional-demo-002"}, "conflicto_box"),
])
def test_conflicto_por_api_responde_409_sin_modificar(
    cliente: TestClient, fabrica: sessionmaker[Session], otro: dict[str, str], codigo: str
) -> None:
    turno_id = crear(cliente)
    crear(cliente, inicio="2030-01-10T11:00:00-03:00", **otro)
    antes = intervalo_y_eventos(fabrica, turno_id)

    respuesta = cliente.patch(f"{URL}/{turno_id}", json={"inicio": "2030-01-10T11:00:00-03:00"})

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == codigo
    assert intervalo_y_eventos(fabrica, turno_id) == antes


def test_conflicto_con_bloqueo_por_api_responde_409(cliente: TestClient) -> None:
    turno_id = crear(cliente)
    assert cliente.post("/api/v1/bloqueos", json={
        "box_id": "box-demo-002", "inicio": "2030-01-10T09:00:00-03:00",
        "fin": "2030-01-10T10:00:00-03:00"}).status_code == 201

    respuesta = cliente.patch(f"{URL}/{turno_id}", json={"box_id": "box-demo-002"})

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "conflicto_bloqueo_box"


def test_reprogramar_cancelado_responde_409_transicion_invalida(cliente: TestClient) -> None:
    turno_id = crear(cliente)
    assert cliente.post(f"{URL}/{turno_id}/cancelar").status_code == 200

    respuesta = cliente.patch(f"{URL}/{turno_id}", json={"inicio": "2030-01-10T11:00:00-03:00"})

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "transicion_invalida"


@pytest.mark.parametrize("ruta,cuerpo", [
    ("turno-demo-inexistente", {"inicio": "2030-01-10T11:00:00-03:00"}),
    (None, {"box_id": "box-demo-inexistente"}),
])
def test_recurso_inexistente_responde_404(cliente: TestClient, ruta: str | None, cuerpo: dict[str, str]) -> None:
    turno_id = ruta or crear(cliente)

    respuesta = cliente.patch(f"{URL}/{turno_id}", json=cuerpo)

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "recurso_inexistente"


@pytest.mark.parametrize("cuerpo,codigo", [
    ({"fin": "2030-01-10T09:00:00-03:00"}, "intervalo_invalido"),
    ({"inicio": "2030-01-10T09:00:00-03:00"}, "reprogramacion_sin_cambios"),
])
def test_reglas_de_dominio_invalidas_responden_422_con_codigo(
    cliente: TestClient, fabrica: sessionmaker[Session], cuerpo: dict[str, str], codigo: str
) -> None:
    turno_id = crear(cliente)
    antes = intervalo_y_eventos(fabrica, turno_id)

    respuesta = cliente.patch(f"{URL}/{turno_id}", json=cuerpo)

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == codigo
    assert intervalo_y_eventos(fabrica, turno_id) == antes


# Escenario: Cuerpo vacío por API (y otras entradas mal formadas)
@pytest.mark.parametrize("cuerpo", [
    {},
    {"inicio": None},
    {"paciente_id": "paciente-demo-002"},
    {"inicio": "2030-01-10T11:00:00"},
    {"box_id": ""},
])
def test_entrada_mal_formada_responde_422(cliente: TestClient, cuerpo: dict[str, object]) -> None:
    turno_id = crear(cliente)

    assert cliente.patch(f"{URL}/{turno_id}", json=cuerpo).status_code == 422
