from datetime import UTC, datetime

import pytest

from app.domain.bloqueos import BloqueoDeDisponibilidad, RecursoDeBloqueoInvalidoError
from app.domain.disponibilidad import (
    ConflictoBloqueoBoxError,
    ConflictoBloqueoProfesionalError,
    ConflictoTurnoExistenteError,
    verificar_bloqueos_de_turno,
    verificar_turnos_para_bloqueo,
)
from app.domain.turnos import IntervaloInvalidoError, Turno


def hora(h: int, m: int = 0) -> datetime:
    return datetime(2030, 1, 10, h, m, tzinfo=UTC)


def bloqueo(*, profesional_id: str | None = "profesional-demo-001", box_id: str | None = None,
            inicio: datetime | None = None, fin: datetime | None = None) -> BloqueoDeDisponibilidad:
    return BloqueoDeDisponibilidad("bloqueo-demo-001", profesional_id, box_id,
                                   inicio or hora(9), fin or hora(10), None)


def turno(*, profesional_id: str = "profesional-demo-001", box_id: str = "box-demo-001",
          inicio: datetime | None = None, fin: datetime | None = None) -> Turno:
    return Turno("turno-demo-001", "paciente-demo-001", profesional_id, box_id,
                 "prestacion-demo-001", inicio or hora(9, 30), fin or hora(10, 30))


@pytest.mark.parametrize("recurso", [{"profesional_id": "profesional-demo-001", "box_id": None},
                                    {"profesional_id": None, "box_id": "box-demo-001"}])
def test_bloqueo_acepta_exactamente_un_recurso(recurso: dict[str, str | None]) -> None:
    creado = bloqueo(**recurso)
    assert (creado.profesional_id, creado.box_id) == (recurso["profesional_id"], recurso["box_id"])


@pytest.mark.parametrize("recurso", [{"profesional_id": None, "box_id": None},
                                    {"profesional_id": "profesional-demo-001", "box_id": "box-demo-001"},
                                    {"profesional_id": "", "box_id": None},
                                    {"profesional_id": None, "box_id": ""}])
def test_bloqueo_rechaza_cero_o_dos_recursos(recurso: dict[str, str | None]) -> None:
    with pytest.raises(RecursoDeBloqueoInvalidoError):
        bloqueo(**recurso)


@pytest.mark.parametrize("fin", [hora(9), hora(8, 30)])
def test_bloqueo_rechaza_fin_no_posterior(fin: datetime) -> None:
    with pytest.raises(IntervaloInvalidoError) as capturado:
        bloqueo(fin=fin)
    assert "bloqueo" in str(capturado.value)


@pytest.mark.parametrize("campo", ["inicio", "fin"])
def test_bloqueo_rechaza_fecha_sin_zona(campo: str) -> None:
    with pytest.raises(ValueError, match="zona horaria"):
        bloqueo(**{campo: datetime(2030, 1, 10, 9 if campo == "inicio" else 10)})


@pytest.mark.parametrize("fin", [hora(9, 31), hora(10)])
def test_bloqueo_conflicta_con_turno_intersectante(fin: datetime) -> None:
    with pytest.raises(ConflictoTurnoExistenteError):
        verificar_turnos_para_bloqueo(bloqueo(fin=fin), [turno()])


@pytest.mark.parametrize("intervalo", [(hora(8), hora(9)), (hora(10), hora(11))])
def test_bloqueo_permite_turno_contiguo(intervalo: tuple[datetime, datetime]) -> None:
    verificar_turnos_para_bloqueo(bloqueo(), [turno(inicio=intervalo[0], fin=intervalo[1])])


@pytest.mark.parametrize("recurso,esperado", [
    ({"profesional_id": "profesional-demo-001", "box_id": None}, ConflictoBloqueoProfesionalError),
    ({"profesional_id": None, "box_id": "box-demo-001"}, ConflictoBloqueoBoxError),
])
def test_turno_rechaza_bloqueo_de_su_recurso(recurso: dict[str, str | None], esperado: type[Exception]) -> None:
    with pytest.raises(esperado):
        verificar_bloqueos_de_turno(turno(), [bloqueo(**recurso)])


@pytest.mark.parametrize("intervalo", [(hora(8), hora(9)), (hora(10, 30), hora(11))])
def test_turno_permite_bloqueo_contiguo(intervalo: tuple[datetime, datetime]) -> None:
    verificar_bloqueos_de_turno(turno(), [bloqueo(inicio=intervalo[0], fin=intervalo[1])])
