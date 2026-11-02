"""Pruebas unitarias de la entidad Paciente y sus errores de dominio (C-17)."""

import pytest

from app.domain.turnos import (
    DatosPacienteInvalidosError,
    ErrorDeDominio,
    Paciente,
    PacienteDuplicadoError,
)


def test_paciente_con_nombre_mostrado_y_contacto_opcional_recorta_espacios() -> None:
    paciente = Paciente(
        id="  paciente-demo-010  ",
        nombre_mostrado="  Paciente Demo Ficticio 010  ",
        contacto="  +54 9 11 0000-0010  ",
    )

    assert paciente.id == "paciente-demo-010"
    assert paciente.nombre_mostrado == "Paciente Demo Ficticio 010"
    assert paciente.contacto == "+54 9 11 0000-0010"


@pytest.mark.parametrize("contacto_vacio", [None, "", "   "])
def test_paciente_sin_contacto_o_con_contacto_en_blanco_normaliza_a_none(
    contacto_vacio: str | None,
) -> None:
    paciente = Paciente(
        id="paciente-demo-011",
        nombre_mostrado="Paciente Demo Ficticia 011",
        contacto=contacto_vacio,
    )

    assert paciente.contacto is None


@pytest.mark.parametrize(
    "paciente_id,nombre_mostrado",
    [
        ("", "Paciente Demo Ficticio 012"),
        ("   ", "Paciente Demo Ficticio 012"),
        ("paciente-demo-012", ""),
        ("paciente-demo-012", "   "),
    ],
)
def test_paciente_con_id_o_nombre_mostrado_vacio_lanza_error_de_dominio(
    paciente_id: str, nombre_mostrado: str
) -> None:
    with pytest.raises(DatosPacienteInvalidosError) as exc_info:
        Paciente(id=paciente_id, nombre_mostrado=nombre_mostrado)

    assert isinstance(exc_info.value, ErrorDeDominio)
    assert exc_info.value.codigo == "datos_paciente_invalidos"


def test_paciente_duplicado_error_expone_codigo_estable() -> None:
    error = PacienteDuplicadoError("Ya existe un paciente registrado con ese identificador.")

    assert isinstance(error, ErrorDeDominio)
    assert error.codigo == "paciente_duplicado"
    assert "identificador" in str(error)


def test_paciente_compatible_con_argumentos_posicionales_y_contacto_normalizado() -> None:
    sin_contacto = Paciente("paciente-demo-001", "Paciente Demo Ficticia 001")
    con_contacto = Paciente(
        "paciente-demo-002",
        "Paciente Demo Ficticio 002",
        "  PACIENTE.DEMO.002@Example.Invalid  ",
    )

    assert sin_contacto.contacto is None
    assert sin_contacto.contacto_normalizado is None
    assert con_contacto.contacto == "PACIENTE.DEMO.002@Example.Invalid"
    assert con_contacto.contacto_normalizado == "paciente.demo.002@example.invalid"
