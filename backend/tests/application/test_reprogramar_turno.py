"""Escenarios de `reprogramacion-de-turnos` sobre el caso de uso, con una unidad de trabajo en memoria."""

from dataclasses import replace
from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest

from app.application.reprogramar_turno import ReprogramarTurno, SolicitudReprogramarTurno
from app.domain.bloqueos import BloqueoDeDisponibilidad
from app.domain.disponibilidad import (
    ConflictoBloqueoBoxError,
    ConflictoBloqueoProfesionalError,
    ConflictoBoxError,
    ConflictoProfesionalError,
    se_solapan,
)
from app.domain.turnos import (
    Box,
    EstadoTurno,
    HistorialDeCambio,
    IntervaloInvalidoError,
    Profesional,
    RecursoInexistenteError,
    ReprogramacionSinCambiosError,
    ResumenTurno,
    TipoCambio,
    TransicionInvalidaError,
    Turno,
)
from tests.datos_demo import BOX, BOX_2, PACIENTE, PRESTACION, PROFESIONAL, PROFESIONAL_2

AHORA = datetime(2030, 1, 1, 8, 0, tzinfo=UTC)


def hora(h: int, m: int = 0) -> datetime:
    return datetime(2030, 1, 10, h, m, tzinfo=UTC)


def turno(id_: str = "turno-demo-001", profesional_id: str = PROFESIONAL.id, box_id: str = BOX.id,
          inicio: datetime | None = None, fin: datetime | None = None) -> Turno:
    return Turno(id_, PACIENTE.id, profesional_id, box_id, PRESTACION.id,
                 inicio or hora(9), fin or hora(9, 30))


class Registro(list[str]):
    pass


class Recursos:
    def __init__(self, registro: Registro) -> None:
        self._registro = registro
        self.profesionales = {p.id: p for p in (PROFESIONAL, PROFESIONAL_2)}
        self.boxes = {b.id: b for b in (BOX, BOX_2)}

    def profesional(self, id_: str) -> Profesional | None:
        return self.profesionales.get(id_)

    def box(self, id_: str) -> Box | None:
        return self.boxes.get(id_)

    def bloquear(self, profesional_id: str | None, box_id: str | None) -> None:
        self._registro.append(f"bloquear:{profesional_id}:{box_id}")


class Turnos:
    def __init__(self, registro: Registro, turnos: list[Turno]) -> None:
        self._registro = registro
        self.confirmados = {t.id: t for t in turnos}
        self.pendientes: dict[str, Turno] = {}

    def obtener_para_actualizar(self, turno_id: str) -> Turno | None:
        self._registro.append(f"turno:{turno_id}")
        return self.confirmados.get(turno_id)

    def activos_que_se_solapan(self, profesional_id: str, box_id: str,
                               inicio: datetime, fin: datetime) -> list[Turno]:
        self._registro.append("leer-turnos")
        intervalo = turno("_", profesional_id, box_id, inicio, fin)
        return [t for t in self.confirmados.values() if t.activo and se_solapan(t, intervalo)
                and (t.profesional_id == profesional_id or t.box_id == box_id)]

    def actualizar(self, nuevo: Turno) -> None:
        self.pendientes[nuevo.id] = nuevo


class Bloqueos:
    def __init__(self, registro: Registro) -> None:
        self._registro = registro
        self.confirmados: list[BloqueoDeDisponibilidad] = []

    def que_se_solapan(self, profesional_id: str, box_id: str,
                       inicio: datetime, fin: datetime) -> list[BloqueoDeDisponibilidad]:
        self._registro.append("leer-bloqueos")
        return [b for b in self.confirmados if b.inicio < fin and inicio < b.fin
                and (b.profesional_id == profesional_id or b.box_id == box_id)]


class Historiales:
    def __init__(self, falla: bool = False) -> None:
        self.confirmados: list[HistorialDeCambio] = []
        self.pendientes: list[HistorialDeCambio] = []
        self._falla = falla

    def agregar(self, historial: HistorialDeCambio) -> None:
        if self._falla:
            raise RuntimeError("Fallo simulado al registrar historial")
        self.pendientes.append(historial)


class UoW:
    def __init__(self, turnos: list[Turno], falla_historial: bool = False) -> None:
        self.registro = Registro()
        self.recursos = Recursos(self.registro)
        self.turnos = Turnos(self.registro, turnos)
        self.bloqueos = Bloqueos(self.registro)
        self.historiales = Historiales(falla_historial)
        self.commits = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, tipo: type[BaseException] | None, error: BaseException | None,
                 traza: TracebackType | None) -> None:
        self.turnos.pendientes.clear()
        self.historiales.pendientes.clear()

    def commit(self) -> None:
        self.turnos.confirmados.update(self.turnos.pendientes)
        self.historiales.confirmados += self.historiales.pendientes
        self.turnos.pendientes.clear()
        self.historiales.pendientes.clear()
        self.commits += 1


def reprogramar(uow: UoW, **cambios: object) -> Turno:
    return ReprogramarTurno(lambda: uow, reloj=lambda: AHORA).ejecutar(
        SolicitudReprogramarTurno(turno_id="turno-demo-001", **cambios))  # type: ignore[arg-type]


def assert_sin_cambios(uow: UoW, original: Turno) -> None:
    assert uow.turnos.confirmados[original.id] == original
    assert uow.historiales.confirmados == []
    assert uow.commits == 0


# Escenario: Cambio de horario válido
def test_cambio_de_horario_registra_reprogramado_con_antes_y_despues() -> None:
    original = turno()
    uow = UoW([original])

    nuevo = reprogramar(uow, inicio=hora(11))

    assert (nuevo.inicio, nuevo.fin) == (hora(11), hora(11, 30))
    assert uow.turnos.confirmados[original.id] == nuevo
    assert uow.historiales.confirmados == [HistorialDeCambio(
        original.id, TipoCambio.REPROGRAMADO, AHORA,
        antes=ResumenTurno(PROFESIONAL.id, BOX.id, hora(9), hora(9, 30)),
        despues=ResumenTurno(PROFESIONAL.id, BOX.id, hora(11), hora(11, 30)),
    )]
    assert uow.commits == 1


# Escenario: Cambio de recursos válido
def test_cambio_de_recursos_conserva_el_intervalo() -> None:
    uow = UoW([turno()])

    nuevo = reprogramar(uow, profesional_id=PROFESIONAL_2.id, box_id=BOX_2.id)

    assert (nuevo.profesional_id, nuevo.box_id, nuevo.inicio, nuevo.fin) == (
        PROFESIONAL_2.id, BOX_2.id, hora(9), hora(9, 30))


# Escenario: Reprogramar conserva el estado confirmado
def test_reprogramar_conserva_el_estado_confirmado() -> None:
    uow = UoW([turno().confirmar()])

    assert reprogramar(uow, inicio=hora(11)).estado is EstadoTurno.CONFIRMADO


# Escenario: Correr un turno dentro de su propio intervalo
def test_autoexclusion_permite_solapar_el_intervalo_anterior() -> None:
    uow = UoW([turno()])

    nuevo = reprogramar(uow, inicio=hora(9, 15))

    assert (nuevo.inicio, nuevo.fin) == (hora(9, 15), hora(9, 45))
    assert uow.commits == 1


# Escenarios: Conflicto por profesional / box
@pytest.mark.parametrize("otro,esperado", [
    (turno("turno-demo-otro", PROFESIONAL.id, BOX_2.id, hora(11), hora(11, 30)), ConflictoProfesionalError),
    (turno("turno-demo-otro", PROFESIONAL_2.id, BOX.id, hora(11), hora(11, 30)), ConflictoBoxError),
])
def test_conflicto_con_otro_turno_no_modifica_nada(otro: Turno, esperado: type[Exception]) -> None:
    original = turno()
    uow = UoW([original, otro])

    with pytest.raises(esperado):
        reprogramar(uow, inicio=hora(11))

    assert_sin_cambios(uow, original)


# Escenarios: Conflicto por bloqueo / Conflicto en el nuevo recurso
@pytest.mark.parametrize("bloqueo,cambios,esperado", [
    (BloqueoDeDisponibilidad("bloqueo-demo-001", PROFESIONAL.id, None, hora(11), hora(12)),
     {"inicio": hora(11, 15)}, ConflictoBloqueoProfesionalError),
    (BloqueoDeDisponibilidad("bloqueo-demo-001", None, BOX_2.id, hora(9), hora(10)),
     {"box_id": BOX_2.id}, ConflictoBloqueoBoxError),
])
def test_conflicto_con_bloqueo_no_modifica_nada(
    bloqueo: BloqueoDeDisponibilidad, cambios: dict[str, object], esperado: type[Exception]
) -> None:
    original = turno()
    uow = UoW([original])
    uow.bloqueos.confirmados.append(bloqueo)

    with pytest.raises(esperado):
        reprogramar(uow, **cambios)

    assert_sin_cambios(uow, original)


# Escenarios: Destino contiguo / Turno cancelado en el destino
@pytest.mark.parametrize("otro", [
    turno("turno-demo-otro", PROFESIONAL.id, BOX_2.id, hora(10, 30), hora(11)),
    turno("turno-demo-otro", PROFESIONAL.id, BOX_2.id, hora(11), hora(11, 30)).cancelar(),
])
def test_destino_contiguo_o_cancelado_se_acepta(otro: Turno) -> None:
    uow = UoW([turno(), otro])

    assert reprogramar(uow, inicio=hora(11)).inicio == hora(11)


# Escenarios: Turno cancelado / Box de destino inexistente / Intervalo inválido / Sin cambios
@pytest.mark.parametrize("original,cambios,esperado", [
    (turno().cancelar(), {"inicio": hora(11)}, TransicionInvalidaError),
    (turno(), {"box_id": "box-demo-inexistente"}, RecursoInexistenteError),
    (turno(), {"profesional_id": "profesional-demo-inexistente"}, RecursoInexistenteError),
    (turno(), {"fin": hora(9)}, IntervaloInvalidoError),
    (turno(), {"inicio": hora(9), "box_id": BOX.id}, ReprogramacionSinCambiosError),
])
def test_reprogramacion_invalida_no_persiste(
    original: Turno, cambios: dict[str, object], esperado: type[Exception]
) -> None:
    uow = UoW([original])

    with pytest.raises(esperado):
        reprogramar(uow, **cambios)

    assert_sin_cambios(uow, original)


def test_turno_inexistente_informa_recurso_inexistente() -> None:
    uow = UoW([])

    with pytest.raises(RecursoInexistenteError) as error:
        reprogramar(uow, inicio=hora(11))

    assert error.value.tipo == "turno"
    assert uow.commits == 0


# Escenario: Fallo al registrar el historial
def test_fallo_al_registrar_historial_no_confirma_el_cambio() -> None:
    original = turno()
    uow = UoW([original], falla_historial=True)

    with pytest.raises(RuntimeError):
        reprogramar(uow, inicio=hora(11))

    assert_sin_cambios(uow, original)


def test_bloquea_turno_y_luego_recursos_de_destino_antes_de_leer_conflictos() -> None:
    uow = UoW([turno()])

    reprogramar(uow, profesional_id=PROFESIONAL_2.id, box_id=BOX_2.id)

    assert uow.registro[:2] == ["turno:turno-demo-001", f"bloquear:{PROFESIONAL_2.id}:{BOX_2.id}"]
    assert set(uow.registro[2:]) == {"leer-turnos", "leer-bloqueos"}


def test_conserva_paciente_y_prestacion() -> None:
    original = replace(turno(), paciente_id="paciente-demo-002")
    uow = UoW([original])

    nuevo = reprogramar(uow, inicio=hora(11))

    assert (nuevo.paciente_id, nuevo.prestacion_id) == ("paciente-demo-002", PRESTACION.id)


def test_reprogramar_registra_el_actor_en_el_historial() -> None:
    uow = UoW([turno()])

    reprogramar(uow, inicio=hora(11), actor_id="usuario-demo-001")

    assert uow.historiales.confirmados[0].actor_id == "usuario-demo-001"
