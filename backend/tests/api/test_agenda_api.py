"""Escenarios de `Exponer la consulta por HTTP` (`GET /api/v1/agenda`) contra PostgreSQL real."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.main import crear_app
from app.infrastructure.modelos import HistorialModelo, TurnoModelo

URL_TURNOS = "/api/v1/turnos"
URL_AGENDA = "/api/v1/agenda"


@pytest.fixture
def cliente(fabrica: sessionmaker[Session]) -> Iterator[TestClient]:
    with TestClient(crear_app(fabrica)) as cliente:
        yield cliente


def cuerpo_turno(**cambios: str) -> dict[str, str]:
    base = {
        "paciente_id": "paciente-demo-001",
        "profesional_id": "profesional-demo-001",
        "box_id": "box-demo-001",
        "prestacion_id": "prestacion-demo-001",
        "inicio": "2030-01-10T09:00:00-03:00",
    }
    base.update(cambios)
    return base


def cantidad(fabrica: sessionmaker[Session], modelo: type[TurnoModelo] | type[HistorialModelo]) -> int:
    with fabrica() as sesion:
        return sesion.scalar(select(func.count()).select_from(modelo)) or 0


# Escenario: Consulta diaria exitosa por API
def test_consulta_diaria_exitosa_por_api_responde_200_con_turnos_y_recursos(
    cliente: TestClient,
) -> None:
    creado_1 = cliente.post(
        URL_TURNOS,
        json=cuerpo_turno(
            profesional_id="profesional-demo-002",
            box_id="box-demo-002",
            inicio="2030-01-10T11:00:00-03:00",
        ),
    ).json()
    creado_2 = cliente.post(
        URL_TURNOS,
        json=cuerpo_turno(
            profesional_id="profesional-demo-001",
            box_id="box-demo-001",
            inicio="2030-01-10T09:00:00-03:00",
        ),
    ).json()

    respuesta = cliente.get(
        URL_AGENDA,
        params={
            "inicio": "2030-01-10T08:00:00-03:00",
            "fin": "2030-01-10T12:00:00-03:00",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {
            "id": creado_2["id"],
            "profesional_id": "profesional-demo-001",
            "box_id": "box-demo-001",
            "inicio": "2030-01-10T12:00:00Z",
            "fin": "2030-01-10T12:30:00Z",
        },
        {
            "id": creado_1["id"],
            "profesional_id": "profesional-demo-002",
            "box_id": "box-demo-002",
            "inicio": "2030-01-10T14:00:00Z",
            "fin": "2030-01-10T14:30:00Z",
        },
    ]


# Escenario: Consulta semanal con filtros y respuesta vacía sin coincidencias
def test_consulta_semanal_por_api_filtra_recursos_y_responde_lista_vacia_sin_coincidencias(
    cliente: TestClient,
) -> None:
    creado = cliente.post(
        URL_TURNOS,
        json=cuerpo_turno(
            profesional_id="profesional-demo-001",
            box_id="box-demo-001",
            inicio="2030-01-08T09:00:00-03:00",
        ),
    ).json()
    cliente.post(
        URL_TURNOS,
        json=cuerpo_turno(
            profesional_id="profesional-demo-002",
            box_id="box-demo-002",
            inicio="2030-01-10T10:00:00-03:00",
        ),
    )

    filtrada = cliente.get(
        URL_AGENDA,
        params={
            "inicio": "2030-01-07T00:00:00-03:00",
            "fin": "2030-01-14T00:00:00-03:00",
            "profesional_id": "profesional-demo-001",
            "box_id": "box-demo-001",
        },
    )
    vacia = cliente.get(
        URL_AGENDA,
        params={
            "inicio": "2030-01-07T00:00:00-03:00",
            "fin": "2030-01-14T00:00:00-03:00",
            "profesional_id": "profesional-inexistente-demo",
        },
    )

    assert filtrada.status_code == 200
    assert [item["id"] for item in filtrada.json()] == [creado["id"]]
    assert vacia.status_code == 200
    assert vacia.json() == []


# Escenario: Desplazamientos horarios equivalentes por API
def test_consulta_por_api_con_desplazamientos_horarios_equivalentes_devuelve_turno_una_vez(
    cliente: TestClient,
) -> None:
    creado = cliente.post(
        URL_TURNOS,
        json=cuerpo_turno(inicio="2030-01-10T12:00:00Z"),
    ).json()

    respuesta = cliente.get(
        URL_AGENDA,
        params={
            "inicio": "2030-01-10T08:00:00-03:00",
            "fin": "2030-01-10T10:00:00-03:00",
        },
    )

    assert respuesta.status_code == 200
    assert [item["id"] for item in respuesta.json()] == [creado["id"]]


# Escenario: Error de regla de consulta por rango inválido (fin <= inicio)
@pytest.mark.parametrize(
    "fin",
    [
        "2030-01-10T09:00:00-03:00",
        "2030-01-10T08:00:00-03:00",
    ],
)
def test_rango_invalido_por_api_responde_422_y_no_modifica_datos(
    cliente: TestClient, fabrica: sessionmaker[Session], fin: str
) -> None:
    creado = cliente.post(URL_TURNOS, json=cuerpo_turno()).json()

    respuesta = cliente.get(
        URL_AGENDA,
        params={"inicio": "2030-01-10T09:00:00-03:00", "fin": fin},
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "intervalo_invalido"
    assert cantidad(fabrica, TurnoModelo) == 1
    assert cantidad(fabrica, HistorialModelo) == 1
    vigentes = cliente.get(
        URL_AGENDA,
        params={"inicio": "2030-01-10T08:00:00-03:00", "fin": "2030-01-10T10:00:00-03:00"},
    ).json()
    assert [item["id"] for item in vigentes] == [creado["id"]]


# Escenario: Fecha sin zona horaria por API
@pytest.mark.parametrize(
    ("inicio", "fin"),
    [
        ("2030-01-10T09:00:00", "2030-01-10T10:00:00-03:00"),
        ("2030-01-10T09:00:00-03:00", "2030-01-10T10:00:00"),
    ],
)
def test_fecha_sin_zona_horaria_en_agenda_responde_422_y_no_modifica_datos(
    cliente: TestClient, fabrica: sessionmaker[Session], inicio: str, fin: str
) -> None:
    cliente.post(URL_TURNOS, json=cuerpo_turno())

    respuesta = cliente.get(URL_AGENDA, params={"inicio": inicio, "fin": fin})

    assert respuesta.status_code == 422
    assert cantidad(fabrica, TurnoModelo) == 1
    assert cantidad(fabrica, HistorialModelo) == 1


# Escenario: Fecha obligatoria ausente por API
@pytest.mark.parametrize(
    "params",
    [
        {"inicio": "2030-01-10T09:00:00-03:00"},
        {"fin": "2030-01-10T10:00:00-03:00"},
        {},
    ],
)
def test_fecha_obligatoria_ausente_en_agenda_responde_422(
    cliente: TestClient, params: dict[str, str]
) -> None:
    respuesta = cliente.get(URL_AGENDA, params=params)

    assert respuesta.status_code == 422


# Escenario: Fecha mal formada por API
@pytest.mark.parametrize(
    ("inicio", "fin"),
    [
        ("no-es-una-fecha", "2030-01-10T10:00:00-03:00"),
        ("2030-01-10T09:00:00-03:00", "fecha-invalida"),
    ],
)
def test_fecha_mal_formada_en_agenda_responde_422(
    cliente: TestClient, inicio: str, fin: str
) -> None:
    respuesta = cliente.get(URL_AGENDA, params={"inicio": inicio, "fin": fin})

    assert respuesta.status_code == 422


def test_contrato_openapi_de_agenda_documenta_parametros_y_esquema_de_salida(
    cliente: TestClient,
) -> None:
    openapi = cliente.get("/openapi.json").json()
    operacion = openapi["paths"][URL_AGENDA]["get"]
    parametros = {p["name"]: p for p in operacion["parameters"]}

    assert set(parametros) == {"inicio", "fin", "profesional_id", "box_id"}
    assert parametros["inicio"]["required"] is True
    assert parametros["fin"]["required"] is True
    assert parametros["profesional_id"]["required"] is False
    assert parametros["box_id"]["required"] is False
    esquema_item = openapi["components"]["schemas"]["TurnoAgendaSalida"]
    assert set(esquema_item["properties"]) == {"id", "profesional_id", "box_id", "inicio", "fin"}
