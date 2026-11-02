from dataclasses import replace
from datetime import UTC, datetime

import pytest

from app.domain.turnos import (
    DuracionInvalidaError,
    EstadoTurno,
    IntervaloInvalidoError,
    Prestacion,
    ReprogramacionSinCambiosError,
    ResumenTurno,
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


# Reprogramación (C-04)
def test_reprogramar_el_inicio_conserva_la_duracion_y_el_estado() -> None:
    original = replace(turno(INICIO, FIN), estado=EstadoTurno.CONFIRMADO)

    nuevo = original.reprogramar(inicio=datetime(2030, 1, 10, 11, 0, tzinfo=UTC))

    assert (nuevo.inicio, nuevo.fin) == (datetime(2030, 1, 10, 11, 0, tzinfo=UTC),
                                         datetime(2030, 1, 10, 11, 30, tzinfo=UTC))
    assert nuevo.estado is EstadoTurno.CONFIRMADO
    assert (nuevo.id, nuevo.paciente_id, nuevo.prestacion_id) == (
        original.id, original.paciente_id, original.prestacion_id)


def test_reprogramar_recursos_conserva_el_intervalo() -> None:
    nuevo = turno(INICIO, FIN).reprogramar(profesional_id="profesional-demo-002", box_id="box-demo-002")

    assert (nuevo.profesional_id, nuevo.box_id, nuevo.inicio, nuevo.fin) == (
        "profesional-demo-002", "box-demo-002", INICIO, FIN)


def test_reprogramar_solo_el_fin_extiende_el_turno() -> None:
    nuevo = turno(INICIO, FIN).reprogramar(fin=datetime(2030, 1, 10, 10, 0, tzinfo=UTC))

    assert (nuevo.inicio, nuevo.fin) == (INICIO, datetime(2030, 1, 10, 10, 0, tzinfo=UTC))


@pytest.mark.parametrize("cambios", [{"fin": INICIO}, {"inicio": FIN, "fin": INICIO}])
def test_reprogramar_con_fin_no_posterior_se_rechaza(cambios: dict[str, datetime]) -> None:
    with pytest.raises(IntervaloInvalidoError):
        turno(INICIO, FIN).reprogramar(**cambios)


@pytest.mark.parametrize("cambios", [{}, {"inicio": INICIO, "fin": FIN, "box_id": "box-demo-001"}])
def test_reprogramar_sin_cambios_se_rechaza(cambios: dict[str, object]) -> None:
    with pytest.raises(ReprogramacionSinCambiosError) as error:
        turno(INICIO, FIN).reprogramar(**cambios)  # type: ignore[arg-type]

    assert error.value.codigo == "reprogramacion_sin_cambios"


def test_reprogramar_un_turno_cancelado_es_una_transicion_invalida() -> None:
    cancelado = turno(INICIO, FIN).cancelar()

    with pytest.raises(TransicionInvalidaError):
        cancelado.reprogramar(inicio=datetime(2030, 1, 10, 11, 0, tzinfo=UTC))


def test_resumen_describe_recursos_e_intervalo() -> None:
    assert ResumenTurno.de(turno(INICIO, FIN)) == ResumenTurno(
        "profesional-demo-001", "box-demo-001", INICIO, FIN)
