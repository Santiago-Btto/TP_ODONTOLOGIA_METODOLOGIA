"""Contrato HTTP de bloqueos y alta de turnos, probado con PostgreSQL real."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.main import crear_app
from app.infrastructure.modelos import BloqueoModelo, HistorialModelo, TurnoModelo

URL = "/api/v1/bloqueos"


@pytest.fixture
def cliente(fabrica: sessionmaker[Session]) -> Iterator[TestClient]:
    with TestClient(crear_app(fabrica)) as cliente:
        yield cliente


def cuerpo(**cambios: object) -> dict[str, object]:
    datos: dict[str, object] = {
        "profesional_id": "profesional-demo-001",
        "inicio": "2030-01-10T09:00:00-03:00",
        "fin": "2030-01-10T10:00:00-03:00",
        "motivo": "Reunión Demo",
    }
    datos.update(cambios)
    return datos


def turno(**cambios: str) -> dict[str, str]:
    datos = {
        "paciente_id": "paciente-demo-001", "profesional_id": "profesional-demo-001",
        "box_id": "box-demo-001", "prestacion_id": "prestacion-demo-001",
        "inicio": "2030-01-10T09:30:00-03:00",
    }
    datos.update(cambios)
    return datos


def cantidad(fabrica: sessionmaker[Session], modelo: type[BloqueoModelo] | type[TurnoModelo] | type[HistorialModelo]) -> int:
    with fabrica() as sesion:
        return sesion.scalar(select(func.count()).select_from(modelo)) or 0


@pytest.mark.parametrize("recurso", [
    {"profesional_id": "profesional-demo-001"},
    {"profesional_id": None, "box_id": "box-demo-001"},
])
def test_post_bloqueos_devuelve_201_y_datos_normalizados(cliente: TestClient, recurso: dict[str, str | None]) -> None:
    respuesta = cliente.post(URL, json=cuerpo(**recurso))
    assert respuesta.status_code == 201
    dato = respuesta.json()
    assert dato["id"]
    assert (dato["profesional_id"], dato["box_id"]) == (recurso.get("profesional_id"), recurso.get("box_id"))
    assert (dato["inicio"], dato["fin"], dato["motivo"]) == (
        "2030-01-10T12:00:00Z", "2030-01-10T13:00:00Z", "Reunión Demo")


def test_post_bloqueos_acepta_superposicion_con_otro_bloqueo(cliente: TestClient, fabrica: sessionmaker[Session]) -> None:
    assert cliente.post(URL, json=cuerpo()).status_code == 201
    respuesta = cliente.post(URL, json=cuerpo(inicio="2030-01-10T09:30:00-03:00", motivo=None))
    assert respuesta.status_code == 201
    assert cantidad(fabrica, BloqueoModelo) == 2


def test_post_bloqueos_no_impone_limite_de_motivo_ajeno_a_la_kb(cliente: TestClient) -> None:
    motivo_demo = "Motivo Demo " * 55
    respuesta = cliente.post(URL, json=cuerpo(motivo=motivo_demo))
    assert respuesta.status_code == 201
    assert respuesta.json()["motivo"] == motivo_demo


@pytest.mark.parametrize("recurso", [
    {"profesional_id": "profesional-inexistente"},
    {"profesional_id": None, "box_id": "box-inexistente"},
])
def test_post_bloqueos_recurso_inexistente_devuelve_404(
    cliente: TestClient, fabrica: sessionmaker[Session], recurso: dict[str, str | None]
) -> None:
    respuesta = cliente.post(URL, json=cuerpo(**recurso))
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "recurso_inexistente"
    assert cantidad(fabrica, BloqueoModelo) == 0


@pytest.mark.parametrize("recurso,turno_anterior", [
    ({"profesional_id": "profesional-demo-001"}, {"box_id": "box-demo-002"}),
    ({"profesional_id": None, "box_id": "box-demo-001"}, {"profesional_id": "profesional-demo-002"}),
])
def test_post_bloqueos_cruza_turno_y_devuelve_409_sin_mutar(
    cliente: TestClient, fabrica: sessionmaker[Session], recurso: dict[str, str | None], turno_anterior: dict[str, str]
) -> None:
    assert cliente.post("/api/v1/turnos", json=turno(**turno_anterior)).status_code == 201
    respuesta = cliente.post(URL, json=cuerpo(**recurso))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "conflicto_turno_existente"
    assert (cantidad(fabrica, BloqueoModelo), cantidad(fabrica, TurnoModelo), cantidad(fabrica, HistorialModelo)) == (0, 1, 1)


@pytest.mark.parametrize("cambios", [
    {"profesional_id": None},
    {"box_id": "box-demo-001"},
    {"fin": "2030-01-10T09:00:00-03:00"},
    {"fin": "2030-01-10T08:00:00-03:00"},
    {"inicio": "2030-01-10T09:00:00"},
    {"fin": "sin-fecha"},
])
def test_post_bloqueos_invalido_devuelve_422_sin_persistir(
    cliente: TestClient, fabrica: sessionmaker[Session], cambios: dict[str, object]
) -> None:
    respuesta = cliente.post(URL, json=cuerpo(**cambios))
    assert respuesta.status_code == 422
    assert cantidad(fabrica, BloqueoModelo) == 0


@pytest.mark.parametrize("campo", ["inicio", "fin"])
def test_post_bloqueos_requiere_ambas_fechas(cliente: TestClient, campo: str) -> None:
    datos = cuerpo()
    del datos[campo]
    assert cliente.post(URL, json=datos).status_code == 422


@pytest.mark.parametrize("recurso,turno_nuevo,codigo", [
    ({"profesional_id": "profesional-demo-001"}, {"box_id": "box-demo-002"}, "conflicto_bloqueo_profesional"),
    ({"profesional_id": None, "box_id": "box-demo-001"}, {"profesional_id": "profesional-demo-002"}, "conflicto_bloqueo_box"),
])
def test_post_turnos_rechaza_bloqueo_y_no_crea_historial(
    cliente: TestClient, fabrica: sessionmaker[Session], recurso: dict[str, str | None],
    turno_nuevo: dict[str, str], codigo: str
) -> None:
    assert cliente.post(URL, json=cuerpo(**recurso)).status_code == 201
    respuesta = cliente.post("/api/v1/turnos", json=turno(**turno_nuevo))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == codigo
    assert (cantidad(fabrica, TurnoModelo), cantidad(fabrica, HistorialModelo)) == (0, 0)


@pytest.mark.parametrize("inicio,fin", [
    ("2030-01-10T08:30:00-03:00", "2030-01-10T09:30:00-03:00"),
    ("2030-01-10T10:00:00-03:00", "2030-01-10T11:00:00-03:00"),
])
def test_post_turnos_acepta_contiguedad_con_bloqueo(
    cliente: TestClient, inicio: str, fin: str
) -> None:
    assert cliente.post(URL, json=cuerpo(inicio=inicio, fin=fin)).status_code == 201
    assert cliente.post("/api/v1/turnos", json=turno()).status_code == 201


def test_openapi_publica_la_ruta_y_esquema_del_ejemplo(cliente: TestClient) -> None:
    documento = cliente.get("/openapi.json").json()
    operacion = documento["paths"][URL]["post"]
    esquema = documento["components"]["schemas"]["BloqueoEntrada"]
    assert "201" in operacion["responses"]
    assert set(esquema["required"]) == {"inicio", "fin"}
    assert {"profesional_id", "box_id", "motivo"}.issubset(esquema["properties"])
    assert "detail" in operacion["responses"]["422"]["description"]
    assert "validación" in operacion["responses"]["422"]["description"]


def test_errores_422_de_intervalo_y_sintaxis_tienen_detalle_de_validacion(cliente: TestClient) -> None:
    intervalo = cliente.post(URL, json=cuerpo(fin="2030-01-10T09:00:00-03:00"))
    sintaxis = cliente.post(URL, json=cuerpo(inicio="sin-fecha"))
    assert intervalo.status_code == sintaxis.status_code == 422
    assert isinstance(intervalo.json()["detail"], list)
    assert isinstance(sintaxis.json()["detail"], list)
