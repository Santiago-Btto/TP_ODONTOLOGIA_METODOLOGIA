from datetime import UTC, datetime

import pytest

from app.domain.turnos import (
    DuracionInvalidaError,
    EstadoTurno,
    IntervaloInvalidoError,
    Prestacion,
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
