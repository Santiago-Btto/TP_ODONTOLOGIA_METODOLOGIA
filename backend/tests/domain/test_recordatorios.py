"""Pruebas unitarias del modelo de dominio de recordatorios simulados (C-16)."""

from datetime import UTC, datetime

import pytest

from app.domain.recordatorios import (
    MotivoRecordatorio,
    RecordatorioEnviado,
    TareaRecordatorio,
)
from app.domain.turnos import ErrorDeDominio


def test_motivo_recordatorio_define_creado_y_confirmado() -> None:
    assert MotivoRecordatorio.CREADO.value == "creado"
    assert MotivoRecordatorio.CONFIRMADO.value == "confirmado"
    assert set(MotivoRecordatorio) == {
        MotivoRecordatorio.CREADO,
        MotivoRecordatorio.CONFIRMADO,
    }


def test_tarea_recordatorio_con_datos_validos_es_inmutable() -> None:
    tarea = TareaRecordatorio(
        turno_id="turno-demo-001",
        motivo=MotivoRecordatorio.CREADO,
    )

    assert tarea.turno_id == "turno-demo-001"
    assert tarea.motivo is MotivoRecordatorio.CREADO


@pytest.mark.parametrize("turno_id", ["", "   "])
def test_tarea_recordatorio_rechaza_turno_id_vacio(turno_id: str) -> None:
    with pytest.raises(ErrorDeDominio):
        TareaRecordatorio(turno_id=turno_id, motivo=MotivoRecordatorio.CONFIRMADO)


def test_recordatorio_enviado_conserva_trazabilidad_simulada() -> None:
    instante = datetime(2030, 1, 10, 9, 0, tzinfo=UTC)
    envio = RecordatorioEnviado(
        turno_id="turno-demo-001",
        motivo=MotivoRecordatorio.CONFIRMADO,
        destinatario="Paciente Demo Uno",
        enviado_en=instante,
        id=1,
    )

    assert envio.id == 1
    assert envio.turno_id == "turno-demo-001"
    assert envio.motivo is MotivoRecordatorio.CONFIRMADO
    assert envio.destinatario == "Paciente Demo Uno"
    assert envio.enviado_en == instante
