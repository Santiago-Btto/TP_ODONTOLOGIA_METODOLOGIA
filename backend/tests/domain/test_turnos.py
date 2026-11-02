from dataclasses import replace
from datetime import UTC, datetime

import pytest

from app.domain.turnos import (
    DuracionInvalidaError,
    EstadoTurno,
    IntervaloInvalidoError,
    Prestacion,
    TransicionInvalidaError,
    Turno,
    calcular_fin,
)

INICIO = datetime(2030, 1, 10, 9, 0, tzinfo=UTC)
FIN = datetime(2030, 1, 10, 9, 30, tzinfo=UTC)


def turno(inicio: datetime, fin: datetime) -> Turno:
    return Turno(
        id="turno-demo-001",
        paciente_id="paciente-demo-001",
        profesional_id="profesional-demo-001",
        box_id="box-demo-001",
        prestacion_id="prestacion-demo-001",
        inicio=inicio,
        fin=fin,
    )


def test_crea_un_turno_programado_con_intervalo_positivo() -> None:
    creado = turno(INICIO, FIN)

    assert (creado.inicio, creado.fin) == (INICIO, FIN)
    assert creado.estado is EstadoTurno.PROGRAMADO


def test_rechaza_un_intervalo_cuyo_fin_coincide_con_el_inicio() -> None:
    with pytest.raises(IntervaloInvalidoError):
        turno(INICIO, INICIO)


def test_rechaza_un_intervalo_cuyo_fin_es_anterior_al_inicio() -> None:
    with pytest.raises(IntervaloInvalidoError):
        turno(FIN, INICIO)


def test_calcula_el_fin_desde_la_duracion_de_la_prestacion() -> None:
    prestacion = Prestacion(id="prestacion-demo-001", nombre="Prestación Demo", duracion_minutos=30)

    assert calcular_fin(INICIO, prestacion) == FIN


@pytest.mark.parametrize("duracion", [0, -15])
def test_rechaza_una_prestacion_de_duracion_no_positiva(duracion: int) -> None:
    prestacion = Prestacion(id="prestacion-demo-x", nombre="Prestación Demo Inválida", duracion_minutos=duracion)

    with pytest.raises(DuracionInvalidaError):
        calcular_fin(INICIO, prestacion)


# Ciclo de vida (C-05): programado → confirmado → cancelado
def test_confirmar_un_turno_programado_devuelve_copia_confirmada_con_el_mismo_intervalo() -> None:
    original = turno(INICIO, FIN)

    confirmado = original.confirmar()

    assert confirmado.estado is EstadoTurno.CONFIRMADO
    assert (confirmado.id, confirmado.inicio, confirmado.fin) == (original.id, INICIO, FIN)
    assert original.estado is EstadoTurno.PROGRAMADO


@pytest.mark.parametrize("estado_inicial", [EstadoTurno.PROGRAMADO, EstadoTurno.CONFIRMADO])
def test_cancelar_un_turno_activo_lo_deja_cancelado_e_inactivo(estado_inicial: EstadoTurno) -> None:
    original = replace(turno(INICIO, FIN), estado=estado_inicial)

    cancelado = original.cancelar()

    assert cancelado.estado is EstadoTurno.CANCELADO
    assert original.activo
    assert not cancelado.activo


@pytest.mark.parametrize("estado_inicial,accion", [
    (EstadoTurno.CONFIRMADO, "confirmar"),
    (EstadoTurno.CANCELADO, "confirmar"),
    (EstadoTurno.CANCELADO, "cancelar"),
])
def test_transiciones_no_permitidas_se_rechazan(estado_inicial: EstadoTurno, accion: str) -> None:
    original = replace(turno(INICIO, FIN), estado=estado_inicial)

    with pytest.raises(TransicionInvalidaError) as error:
        getattr(original, accion)()

    assert error.value.codigo == "transicion_invalida"
    assert estado_inicial.value in str(error.value)
