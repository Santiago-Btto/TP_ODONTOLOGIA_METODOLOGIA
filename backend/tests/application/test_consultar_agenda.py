"""Escenarios del spec `consulta-de-agenda` sobre el caso de uso `ConsultarAgenda`."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.application.consultar_agenda import ConsultarAgenda, SolicitudConsultarAgenda
from app.domain.disponibilidad import Intervalo, se_solapan
from app.domain.turnos import IntervaloInvalidoError, Turno
from tests.datos_demo import BOX, BOX_2, PACIENTE, PRESTACION, PROFESIONAL, PROFESIONAL_2

ZONA_ARG = timezone(timedelta(hours=-3))


def hora(hh: int, mm: int, dia: int = 10, zona: timezone = UTC) -> datetime:
    return datetime(2030, 1, dia, hh, mm, tzinfo=zona)


def turno_demo(
    id_: str,
    inicio: datetime,
    fin: datetime,
    profesional_id: str = PROFESIONAL.id,
    box_id: str = BOX.id,
) -> Turno:
    return Turno(
        id=id_,
        paciente_id=PACIENTE.id,
        profesional_id=profesional_id,
        box_id=box_id,
        prestacion_id=PRESTACION.id,
        inicio=inicio,
        fin=fin,
    )


class LectorAgendaEnMemoria:
    def __init__(self, turnos: list[Turno] | None = None) -> None:
        self.turnos = list(turnos or [])
        self.consultas: list[tuple[datetime, datetime, str | None, str | None]] = []
        self.commits = 0
        self.historiales_agregados = 0

    def en_rango(
        self,
        inicio: datetime,
        fin: datetime,
        profesional_id: str | None = None,
        box_id: str | None = None,
    ) -> list[Turno]:
        # Requerir que el caso de uso normalice a UTC antes de delegar al puerto
        assert inicio.tzinfo == UTC
        assert fin.tzinfo == UTC
        self.consultas.append((inicio, fin, profesional_id, box_id))
        rango = Intervalo(inicio=inicio, fin=fin)
        resultado = [
            t
            for t in self.turnos
            if se_solapan(t, rango)
            and (profesional_id is None or t.profesional_id == profesional_id)
            and (box_id is None or t.box_id == box_id)
        ]
        return sorted(resultado, key=lambda t: t.inicio)


# Escenario: Turnos contenidos en una agenda diaria (caso base de rango válido)
def test_consultar_agenda_con_rango_valido_devuelve_turnos_del_rango() -> None:
    t1 = turno_demo("turno-demo-001", hora(9, 0), hora(9, 30))
    t2 = turno_demo("turno-demo-002", hora(11, 0), hora(11, 30))
    lector = LectorAgendaEnMemoria([t1, t2])
    caso = ConsultarAgenda(lector)

    resultado = caso.ejecutar(SolicitudConsultarAgenda(inicio=hora(8, 0), fin=hora(12, 0)))

    assert resultado == [t1, t2]
    assert lector.consultas == [(hora(8, 0), hora(12, 0), None, None)]


# Escenario: Error de regla de consulta por rango inválido (fin <= inicio)
@pytest.mark.parametrize("fin", [hora(9, 0), hora(8, 30)])
def test_consultar_agenda_con_fin_igual_o_anterior_a_inicio_lanza_error(fin: datetime) -> None:
    lector = LectorAgendaEnMemoria([turno_demo("turno-demo-001", hora(9, 0), hora(9, 30))])
    caso = ConsultarAgenda(lector)

    with pytest.raises(IntervaloInvalidoError):
        caso.ejecutar(SolicitudConsultarAgenda(inicio=hora(9, 0), fin=fin))

    assert lector.consultas == []


# Escenario: Fecha sin zona horaria es rechazada en la regla de consulta
@pytest.mark.parametrize(
    ("inicio", "fin"),
    [
        (datetime(2030, 1, 10, 9, 0), hora(10, 0)),
        (hora(9, 0), datetime(2030, 1, 10, 10, 0)),
    ],
)
def test_consultar_agenda_con_fecha_sin_zona_horaria_lanza_error(inicio: datetime, fin: datetime) -> None:
    lector = LectorAgendaEnMemoria()
    caso = ConsultarAgenda(lector)

    with pytest.raises(IntervaloInvalidoError):
        caso.ejecutar(SolicitudConsultarAgenda(inicio=inicio, fin=fin))

    assert lector.consultas == []


# Escenario: Desplazamientos horarios equivalentes (-03:00 vs UTC)
def test_consultar_agenda_normaliza_desplazamientos_horarios_equivalentes_y_delega_en_utc() -> None:
    # Turno guardado a las 12:00 UTC (equivalente a 09:00 -03:00)
    turno_utc = turno_demo("turno-demo-utc", hora(12, 0, zona=UTC), hora(12, 30, zona=UTC))
    lector = LectorAgendaEnMemoria([turno_utc])
    caso = ConsultarAgenda(lector)

    # Consulta expresada con desplazamiento -03:00 (08:00 a 10:00 -03:00 == 11:00 a 13:00 UTC)
    inicio_arg = hora(8, 0, zona=ZONA_ARG)
    fin_arg = hora(10, 0, zona=ZONA_ARG)
    resultado = caso.ejecutar(SolicitudConsultarAgenda(inicio=inicio_arg, fin=fin_arg))

    assert resultado == [turno_utc]
    assert lector.consultas == [(hora(11, 0, zona=UTC), hora(13, 0, zona=UTC), None, None)]


# Escenario: Agenda semanal con filtros opcionales de profesional, box y combinados
def test_consultar_agenda_semanal_con_filtros_opcionales_y_combinados() -> None:
    t_p1_b1 = turno_demo("turno-demo-1", hora(9, 0, dia=7), hora(9, 30, dia=7), PROFESIONAL.id, BOX.id)
    t_p1_b2 = turno_demo("turno-demo-2", hora(10, 0, dia=9), hora(10, 30, dia=9), PROFESIONAL.id, BOX_2.id)
    t_p2_b1 = turno_demo("turno-demo-3", hora(11, 0, dia=11), hora(11, 30, dia=11), PROFESIONAL_2.id, BOX.id)
    lector = LectorAgendaEnMemoria([t_p2_b1, t_p1_b1, t_p1_b2])
    caso = ConsultarAgenda(lector)
    inicio_sem = hora(0, 0, dia=7)
    fin_sem = hora(0, 0, dia=14)

    por_prof = caso.ejecutar(
        SolicitudConsultarAgenda(inicio=inicio_sem, fin=fin_sem, profesional_id=PROFESIONAL.id)
    )
    por_box = caso.ejecutar(
        SolicitudConsultarAgenda(inicio=inicio_sem, fin=fin_sem, box_id=BOX.id)
    )
    combinado = caso.ejecutar(
        SolicitudConsultarAgenda(
            inicio=inicio_sem, fin=fin_sem, profesional_id=PROFESIONAL.id, box_id=BOX.id
        )
    )
    sin_coincidencias = caso.ejecutar(
        SolicitudConsultarAgenda(
            inicio=inicio_sem, fin=fin_sem, profesional_id="profesional-inexistente-demo"
        )
    )

    assert por_prof == [t_p1_b1, t_p1_b2]
    assert por_box == [t_p1_b1, t_p2_b1]
    assert combinado == [t_p1_b1]
    assert sin_coincidencias == []
    assert lector.consultas == [
        (inicio_sem, fin_sem, PROFESIONAL.id, None),
        (inicio_sem, fin_sem, None, BOX.id),
        (inicio_sem, fin_sem, PROFESIONAL.id, BOX.id),
        (inicio_sem, fin_sem, "profesional-inexistente-demo", None),
    ]


# Escenario: Ausencia de escrituras o commit durante la consulta
def test_consultar_agenda_no_modifica_turnos_ni_invoca_commit() -> None:
    previos = [turno_demo("turno-demo-001", hora(9, 0), hora(9, 30))]
    lector = LectorAgendaEnMemoria(previos)
    caso = ConsultarAgenda(lector)

    caso.ejecutar(SolicitudConsultarAgenda(inicio=hora(8, 0), fin=hora(10, 0)))

    assert lector.turnos == previos
    assert lector.commits == 0
    assert lector.historiales_agregados == 0
