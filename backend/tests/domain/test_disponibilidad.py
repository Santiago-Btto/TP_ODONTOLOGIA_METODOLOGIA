from datetime import UTC, datetime

import pytest

from app.domain.disponibilidad import (
    ConflictoBoxError,
    ConflictoProfesionalError,
    Intervalo,
    se_solapan,
    verificar_disponibilidad,
)
from app.domain.turnos import Turno


def hora(hh: int, mm: int) -> datetime:
    return datetime(2030, 1, 10, hh, mm, tzinfo=UTC)


def turno(id_: str, profesional_id: str, box_id: str, inicio: datetime, fin: datetime) -> Turno:
    return Turno(
        id=id_,
        paciente_id=f"paciente-demo-{id_}",
        profesional_id=profesional_id,
        box_id=box_id,
        prestacion_id="prestacion-demo-001",
        inicio=inicio,
        fin=fin,
    )


EXISTENTE = turno("existente", "profesional-demo-001", "box-demo-001", hora(9, 0), hora(9, 30))


def test_detecta_un_solapamiento_parcial() -> None:
    assert se_solapan(Intervalo(hora(9, 0), hora(9, 30)), Intervalo(hora(9, 15), hora(9, 45)))


def test_detecta_un_intervalo_contenido_en_otro() -> None:
    assert se_solapan(Intervalo(hora(9, 10), hora(9, 20)), Intervalo(hora(9, 0), hora(9, 30)))


def test_admite_intervalos_contiguos_en_ambos_bordes() -> None:
    assert not se_solapan(Intervalo(hora(9, 30), hora(10, 0)), Intervalo(hora(9, 0), hora(9, 30)))
    assert not se_solapan(Intervalo(hora(8, 30), hora(9, 0)), Intervalo(hora(9, 0), hora(9, 30)))


def test_informa_conflicto_por_profesional_aunque_el_box_sea_distinto() -> None:
    candidato = turno("candidato", "profesional-demo-001", "box-demo-002", hora(9, 15), hora(9, 45))

    with pytest.raises(ConflictoProfesionalError):
        verificar_disponibilidad(candidato, [EXISTENTE])


def test_informa_conflicto_por_box_aunque_el_profesional_sea_distinto() -> None:
    candidato = turno("candidato", "profesional-demo-002", "box-demo-001", hora(9, 15), hora(9, 45))

    with pytest.raises(ConflictoBoxError):
        verificar_disponibilidad(candidato, [EXISTENTE])


def test_acepta_un_candidato_contiguo_con_los_mismos_recursos() -> None:
    candidato = turno("candidato", "profesional-demo-001", "box-demo-001", hora(9, 30), hora(10, 0))

    verificar_disponibilidad(candidato, [EXISTENTE])


def test_ignora_turnos_de_otros_recursos() -> None:
    candidato = turno("candidato", "profesional-demo-002", "box-demo-002", hora(9, 0), hora(9, 30))

    verificar_disponibilidad(candidato, [EXISTENTE])
