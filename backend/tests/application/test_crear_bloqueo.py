from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest

from app.application.crear_bloqueo import CrearBloqueo, SolicitudCrearBloqueo
from app.domain.bloqueos import BloqueoDeDisponibilidad
from app.domain.disponibilidad import ConflictoTurnoExistenteError, se_solapan
from app.domain.turnos import RecursoInexistenteError, Turno
from tests.datos_demo import BOX, BOX_2, PRESTACION, PROFESIONAL, PROFESIONAL_2


def hora(h: int, m: int = 0) -> datetime:
    return datetime(2030, 1, 10, h, m, tzinfo=UTC)


class RecursosFalsos:
    def __init__(self) -> None:
        self.profesionales = {p.id: p for p in (PROFESIONAL, PROFESIONAL_2)}
        self.boxes = {b.id: b for b in (BOX, BOX_2)}
        self.bloqueos_adquiridos: list[tuple[str | None, str | None]] = []

    def profesional(self, id_: str):
        return self.profesionales.get(id_)

    def box(self, id_: str):
        return self.boxes.get(id_)

    def bloquear(self, profesional_id: str | None, box_id: str | None) -> None:
        self.bloqueos_adquiridos.append((profesional_id, box_id))


class TurnosFalsos:
    def __init__(self) -> None:
        self.confirmados: list[Turno] = []
        self.lecturas: list[tuple[str | None, str | None]] = []

    def activos_del_recurso_que_se_solapan(self, profesional_id: str | None, box_id: str | None,
                                             inicio: datetime, fin: datetime) -> list[Turno]:
        self.lecturas.append((profesional_id, box_id))
        intervalo = BloqueoDeDisponibilidad("consulta", profesional_id, box_id, inicio, fin)
        return [t for t in self.confirmados if se_solapan(t, intervalo) and
                (t.profesional_id == profesional_id if profesional_id is not None else t.box_id == box_id)]


class BloqueosFalsos:
    def __init__(self) -> None:
        self.confirmados: list[BloqueoDeDisponibilidad] = []
        self.pendientes: list[BloqueoDeDisponibilidad] = []

    def agregar(self, bloqueo: BloqueoDeDisponibilidad) -> None:
        self.pendientes.append(bloqueo)


class UoWFalsa:
    def __init__(self) -> None:
        self.recursos = RecursosFalsos()
        self.turnos = TurnosFalsos()
        self.bloqueos = BloqueosFalsos()
        self.commits = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, tipo: type[BaseException] | None, error: BaseException | None,
                 traza: TracebackType | None) -> None:
        self.bloqueos.pendientes.clear()

    def commit(self) -> None:
        self.bloqueos.confirmados.extend(self.bloqueos.pendientes)
        self.bloqueos.pendientes.clear()
        self.commits += 1


def solicitud(**cambios: object) -> SolicitudCrearBloqueo:
    datos: dict[str, object] = dict(id="bloqueo-demo-001", profesional_id=PROFESIONAL.id,
                                    box_id=None, inicio=hora(9), fin=hora(10), motivo="Reunión Demo")
    datos.update(cambios)
    return SolicitudCrearBloqueo(**datos)  # type: ignore[arg-type]


def turno(profesional_id: str = PROFESIONAL.id, box_id: str = BOX.id,
          inicio: datetime | None = None, fin: datetime | None = None) -> Turno:
    return Turno("turno-demo-001", "paciente-demo-001", profesional_id, box_id, PRESTACION.id,
                 inicio or hora(9, 30), fin or hora(10, 30))


@pytest.mark.parametrize("recurso,motivo", [
    ({"profesional_id": PROFESIONAL.id, "box_id": None}, "Reunión Demo"),
    ({"profesional_id": None, "box_id": BOX.id}, None),
])
def test_crear_bloqueo_persiste_un_recurso_y_un_commit(recurso: dict[str, str | None], motivo: str | None) -> None:
    uow = UoWFalsa()
    creado = CrearBloqueo(lambda: uow).ejecutar(solicitud(**recurso, motivo=motivo))
    assert uow.bloqueos.confirmados == [creado]
    assert (creado.profesional_id, creado.box_id, creado.motivo) == (
        recurso["profesional_id"], recurso["box_id"], motivo)
    assert uow.commits == 1
    assert uow.recursos.bloqueos_adquiridos == [(recurso["profesional_id"], recurso["box_id"])]


@pytest.mark.parametrize("recurso", [
    {"profesional_id": "profesional-inexistente", "box_id": None},
    {"profesional_id": None, "box_id": "box-inexistente"},
])
def test_crear_bloqueo_recurso_inexistente_no_escribe(recurso: dict[str, str | None]) -> None:
    uow = UoWFalsa()
    with pytest.raises(RecursoInexistenteError):
        CrearBloqueo(lambda: uow).ejecutar(solicitud(**recurso))
    assert uow.bloqueos.confirmados == []
    assert uow.commits == 0


@pytest.mark.parametrize("recurso,turno_existente", [
    ({"profesional_id": PROFESIONAL.id, "box_id": None}, turno(box_id=BOX_2.id)),
    ({"profesional_id": None, "box_id": BOX.id}, turno(profesional_id=PROFESIONAL_2.id)),
])
def test_crear_bloqueo_con_turno_intersectante_no_muta(
    recurso: dict[str, str | None], turno_existente: Turno
) -> None:
    uow = UoWFalsa()
    uow.turnos.confirmados.append(turno_existente)
    with pytest.raises(ConflictoTurnoExistenteError):
        CrearBloqueo(lambda: uow).ejecutar(solicitud(**recurso))
    assert uow.turnos.confirmados == [turno_existente]
    assert uow.bloqueos.confirmados == []
    assert uow.commits == 0


@pytest.mark.parametrize("intervalo", [(hora(8), hora(9)), (hora(10), hora(11))])
def test_crear_bloqueo_permite_turno_contiguo(intervalo: tuple[datetime, datetime]) -> None:
    uow = UoWFalsa()
    uow.turnos.confirmados.append(turno(inicio=intervalo[0], fin=intervalo[1]))
    creado = CrearBloqueo(lambda: uow).ejecutar(solicitud())
    assert uow.bloqueos.confirmados == [creado]
    assert uow.commits == 1


@pytest.mark.parametrize("inicio,fin", [(hora(9, 30), hora(10, 30)), (hora(10), hora(11))])
def test_crear_bloqueo_admite_superposicion_entre_bloqueos(inicio: datetime, fin: datetime) -> None:
    uow = UoWFalsa()
    caso = CrearBloqueo(lambda: uow)
    primero = caso.ejecutar(solicitud())
    segundo = caso.ejecutar(solicitud(id="bloqueo-demo-002", inicio=inicio, fin=fin))
    assert uow.bloqueos.confirmados == [primero, segundo]
    assert uow.commits == 2
