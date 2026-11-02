"""Pruebas de integración de persistencia de recordatorios simulados contra PostgreSQL real (C-16)."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.domain.recordatorios import MotivoRecordatorio, RecordatorioEnviado
from app.domain.turnos import EstadoTurno, Turno
from app.infrastructure.modelos import RecordatorioEnviadoModelo
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy
from tests.datos_demo import BOX, PACIENTE, PRESTACION, PROFESIONAL

INICIO = datetime(2030, 1, 10, 9, 0, tzinfo=UTC)
FIN = datetime(2030, 1, 10, 9, 30, tzinfo=UTC)
ENVIADO_1 = datetime(2030, 1, 10, 8, 0, tzinfo=UTC)
ENVIADO_2 = datetime(2030, 1, 10, 8, 30, tzinfo=UTC)


def _insertar_turno_demo(fabrica: sessionmaker[Session], turno_id: str = "turno-demo-rec-1") -> Turno:
    turno = Turno(
        id=turno_id,
        paciente_id=PACIENTE.id,
        profesional_id=PROFESIONAL.id,
        box_id=BOX.id,
        prestacion_id=PRESTACION.id,
        inicio=INICIO,
        fin=FIN,
        estado=EstadoTurno.PROGRAMADO,
    )
    with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
        uow.turnos.agregar(turno)
        uow.commit()
    return turno


def test_persiste_y_lista_recordatorios_por_turno_en_orden_cronologico(
    fabrica: sessionmaker[Session],
) -> None:
    turno = _insertar_turno_demo(fabrica)

    with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
        leido = uow.turnos.obtener(turno.id)
        assert leido == turno
        assert uow.turnos.obtener("turno-no-existe") is None

        rec_confirmado = uow.recordatorios.agregar(
            RecordatorioEnviado(
                turno_id=turno.id,
                motivo=MotivoRecordatorio.CONFIRMADO,
                destinatario=PACIENTE.nombre_mostrado,
                enviado_en=ENVIADO_2,
            )
        )
        rec_creado = uow.recordatorios.agregar(
            RecordatorioEnviado(
                turno_id=turno.id,
                motivo=MotivoRecordatorio.CREADO,
                destinatario=PACIENTE.nombre_mostrado,
                enviado_en=ENVIADO_1,
            )
        )
        uow.commit()

    assert rec_creado.id is not None
    assert rec_confirmado.id is not None

    with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
        encontrado = uow.recordatorios.obtener(turno.id, MotivoRecordatorio.CREADO)
        assert encontrado == rec_creado
        assert uow.recordatorios.obtener("otro-turno", MotivoRecordatorio.CREADO) is None

        listado = uow.recordatorios.listar_por_turno(turno.id)
        assert [r.motivo for r in listado] == [
            MotivoRecordatorio.CREADO,
            MotivoRecordatorio.CONFIRMADO,
        ]


def test_restriccion_unique_impide_duplicar_turno_y_motivo_en_postgresql(
    fabrica: sessionmaker[Session],
) -> None:
    turno = _insertar_turno_demo(fabrica)

    with fabrica() as sesion:
        sesion.execute(
            insert(RecordatorioEnviadoModelo).values(
                turno_id=turno.id,
                motivo="creado",
                destinatario="Paciente Demo",
                enviado_en=ENVIADO_1,
            )
        )
        sesion.commit()

    with fabrica() as sesion:
        with pytest.raises(IntegrityError):
            sesion.execute(
                insert(RecordatorioEnviadoModelo).values(
                    turno_id=turno.id,
                    motivo="creado",
                    destinatario="Paciente Demo",
                    enviado_en=ENVIADO_2,
                )
            )
            sesion.commit()


def test_restriccion_check_rechaza_motivo_invalido_en_postgresql(
    fabrica: sessionmaker[Session],
) -> None:
    turno = _insertar_turno_demo(fabrica)

    with fabrica() as sesion:
        with pytest.raises(IntegrityError):
            sesion.execute(
                insert(RecordatorioEnviadoModelo).values(
                    turno_id=turno.id,
                    motivo="otro_motivo",
                    destinatario="Paciente Demo",
                    enviado_en=ENVIADO_1,
                )
            )
            sesion.commit()
