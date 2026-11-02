"""Pruebas de integración HTTP para el alta y búsqueda de pacientes (C-17)."""

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from app.api.esquemas import PacienteEntrada, PacienteSalida
from app.domain.autorizacion import Rol


def test_esquemas_paciente_entrada_y_salida_definidos() -> None:
    entrada = PacienteEntrada(nombre_mostrado="Paciente Demo Ficticio 010", contacto="+54 9 11 0000-0010")
    salida = PacienteSalida(id="paciente-demo-010", nombre_mostrado=entrada.nombre_mostrado, contacto=entrada.contacto)

    assert salida.id == "paciente-demo-010"


def test_alta_valida_con_contacto_permite_crear_turno(cliente: TestClient) -> None:
    respuesta_alta = cliente.post(
        "/api/v1/pacientes",
        json={
            "nombre_mostrado": "  Paciente Demo Ficticio 010  ",
            "contacto": "  +54 9 11 0000-0010  ",
        },
    )

    assert respuesta_alta.status_code == 201
    cuerpo = respuesta_alta.json()
    assert cuerpo["id"].startswith("paciente-")
    assert cuerpo["nombre_mostrado"] == "Paciente Demo Ficticio 010"
    assert cuerpo["contacto"] == "+54 9 11 0000-0010"

    respuesta_turno = cliente.post(
        "/api/v1/turnos",
        json={
            "paciente_id": cuerpo["id"],
            "profesional_id": "profesional-demo-001",
            "box_id": "box-demo-001",
            "prestacion_id": "prestacion-demo-001",
            "inicio": "2030-05-10T09:00:00-03:00",
        },
    )

    assert respuesta_turno.status_code == 201
    assert respuesta_turno.json()["paciente_id"] == cuerpo["id"]


def test_alta_valida_con_id_explicito_y_sin_contacto_devuelve_null(cliente: TestClient) -> None:
    respuesta = cliente.post(
        "/api/v1/pacientes",
        json={
            "id": "paciente-demo-011",
            "nombre_mostrado": "Paciente Demo Ficticia 011",
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "id": "paciente-demo-011",
        "nombre_mostrado": "Paciente Demo Ficticia 011",
        "contacto": None,
    }


def test_rechaza_alta_con_id_duplicado_con_409(cliente: TestClient) -> None:
    respuesta = cliente.post(
        "/api/v1/pacientes",
        json={
            "id": "paciente-demo-001",
            "nombre_mostrado": "Paciente Demo Duplicado",
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "paciente_duplicado"


def test_rechaza_alta_con_contacto_duplicado_insensible_a_mayusculas_con_409(
    cliente: TestClient,
) -> None:
    respuesta = cliente.post(
        "/api/v1/pacientes",
        json={
            "nombre_mostrado": "Paciente Demo Otro Nombre",
            "contacto": "PACIENTE.DEMO.002@EXAMPLE.INVALID",
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "paciente_duplicado"


def test_busqueda_y_listado_de_pacientes_con_y_sin_filtro_q(cliente: TestClient) -> None:
    cliente.post(
        "/api/v1/pacientes",
        json={
            "id": "paciente-demo-ana",
            "nombre_mostrado": "Paciente Demo Ana",
            "contacto": "+54 9 11 0000-0101",
        },
    )

    todos = cliente.get("/api/v1/pacientes")
    assert todos.status_code == 200
    assert [p["id"] for p in todos.json()] == [
        "paciente-demo-ana",
        "paciente-demo-001",
        "paciente-demo-002",
    ]

    por_nombre = cliente.get("/api/v1/pacientes", params={"q": "ana"})
    assert por_nombre.status_code == 200
    assert [p["id"] for p in por_nombre.json()] == ["paciente-demo-ana"]

    por_contacto = cliente.get("/api/v1/pacientes", params={"q": "0101"})
    assert por_contacto.status_code == 200
    assert [p["id"] for p in por_contacto.json()] == ["paciente-demo-ana"]

    sin_coincidencias = cliente.get("/api/v1/pacientes", params={"q": "inexistente-xyz"})
    assert sin_coincidencias.status_code == 200
    assert sin_coincidencias.json() == []


@pytest.mark.parametrize(
    "campo_prohibido,valor",
    [
        ("historia_clinica", "Antecedentes ficticios"),
        ("odontograma", {"pieza_18": "sana"}),
        ("dni", "00000000"),
        ("obra_social", "Obra Social Demo"),
        ("diagnostico", "Caries ficticia"),
    ],
)
def test_rechaza_campos_clinicos_o_no_permitidos_con_422(
    cliente: TestClient, campo_prohibido: str, valor: object
) -> None:
    respuesta = cliente.post(
        "/api/v1/pacientes",
        json={
            "nombre_mostrado": "Paciente Demo Ficticio 020",
            campo_prohibido: valor,
        },
    )

    assert respuesta.status_code == 422


@pytest.mark.parametrize(
    "carga_invalida",
    [
        {"nombre_mostrado": ""},
        {"nombre_mostrado": "   "},
        {"id": "", "nombre_mostrado": "Paciente Demo Ficticio"},
        {"id": "   ", "nombre_mostrado": "Paciente Demo Ficticio"},
    ],
)
def test_rechaza_nombre_mostrado_o_id_vacios_o_en_blanco_con_422(
    cliente: TestClient, carga_invalida: dict[str, str]
) -> None:
    respuesta = cliente.post("/api/v1/pacientes", json=carga_invalida)

    assert respuesta.status_code == 422


def test_control_de_acceso_por_rol_y_autenticacion_en_pacientes(
    cliente_como: Callable[[Rol], TestClient],
    cliente_anonimo: TestClient,
) -> None:
    sin_token_post = cliente_anonimo.post(
        "/api/v1/pacientes", json={"nombre_mostrado": "Paciente Demo Anonimo"}
    )
    sin_token_get = cliente_anonimo.get("/api/v1/pacientes")
    assert sin_token_post.status_code == 401
    assert sin_token_post.json()["codigo"] == "no_autenticado"
    assert sin_token_get.status_code == 401
    assert sin_token_get.json()["codigo"] == "no_autenticado"

    odontologo = cliente_como(Rol.ODONTOLOGO)
    denegado_post = odontologo.post(
        "/api/v1/pacientes", json={"nombre_mostrado": "Paciente Demo Odontologo"}
    )
    denegado_get = odontologo.get("/api/v1/pacientes")
    assert denegado_post.status_code == 403
    assert denegado_post.json()["codigo"] == "acceso_denegado"
    assert denegado_get.status_code == 403
    assert denegado_get.json()["codigo"] == "acceso_denegado"

    responsable = cliente_como(Rol.RESPONSABLE)
    alta_resp = responsable.post(
        "/api/v1/pacientes",
        json={"nombre_mostrado": "Paciente Demo Responsable", "contacto": "+54 9 11 0000-0999"},
    )
    lista_resp = responsable.get("/api/v1/pacientes", params={"q": "Responsable"})
    assert alta_resp.status_code == 201
    assert lista_resp.status_code == 200
    assert len(lista_resp.json()) == 1
