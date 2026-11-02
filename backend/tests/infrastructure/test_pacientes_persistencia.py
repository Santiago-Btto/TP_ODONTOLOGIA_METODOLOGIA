"""Pruebas de integración de persistencia de pacientes contra PostgreSQL real (C-17)."""

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.domain.turnos import Paciente, PacienteDuplicadoError
from app.infrastructure.repositorios import PacientesSQLAlchemy
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy


def test_semillas_y_recursos_hidratan_contacto_ficticio(
    fabrica: sessionmaker[Session],
) -> None:
    uow = UnidadDeTrabajoSQLAlchemy(fabrica)
    with uow:
        p1 = uow.recursos.paciente("paciente-demo-001")
        p2 = uow.recursos.paciente("paciente-demo-002")

    assert p1 == Paciente(
        id="paciente-demo-001",
        nombre_mostrado="Paciente Demo Ficticia 001",
        contacto="+54 9 11 0000-0001",
    )
    assert p2 == Paciente(
        id="paciente-demo-002",
        nombre_mostrado="Paciente Demo Ficticio 002",
        contacto="paciente.demo.002@example.invalid",
    )


def test_pacientes_sqlalchemy_persiste_y_recupera_por_id_y_contacto_insensible_a_mayusculas(
    fabrica: sessionmaker[Session],
) -> None:
    uow = UnidadDeTrabajoSQLAlchemy(fabrica)
    nuevo = Paciente(
        id="paciente-demo-010",
        nombre_mostrado="Paciente Demo Ficticia 010",
        contacto="Paciente.Demo.010@Example.Invalid",
    )

    with uow:
        assert isinstance(uow.pacientes, PacientesSQLAlchemy)
        uow.pacientes.agregar(nuevo)
        uow.commit()

    with UnidadDeTrabajoSQLAlchemy(fabrica) as lectura:
        por_id = lectura.pacientes.obtener("paciente-demo-010")
        por_contacto = lectura.pacientes.obtener_por_contacto("  PACIENTE.DEMO.010@example.invalid ")

    assert por_id == nuevo
    assert por_contacto == nuevo


def test_postgresql_rechaza_id_o_contacto_duplicado_y_permite_multiples_contactos_nulos(
    fabrica: sessionmaker[Session],
) -> None:
    with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
        uow.pacientes.agregar(Paciente("paciente-demo-sin-1", "Paciente Demo Sin Contacto 1", None))
        uow.pacientes.agregar(Paciente("paciente-demo-sin-2", "Paciente Demo Sin Contacto 2", None))
        uow.commit()

    with pytest.raises(PacienteDuplicadoError):
        with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
            uow.pacientes.agregar(Paciente("paciente-demo-001", "Paciente Demo Duplicado ID", None))
            uow.commit()

    with pytest.raises(PacienteDuplicadoError):
        with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
            uow.pacientes.agregar(
                Paciente(
                    "paciente-demo-otro-id",
                    "Paciente Demo Duplicado Contacto",
                    "PACIENTE.DEMO.002@EXAMPLE.INVALID",
                )
            )
            uow.commit()


def test_buscar_en_postgresql_filtra_por_nombre_id_o_contacto_y_ordena(
    fabrica: sessionmaker[Session],
) -> None:
    with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
        uow.pacientes.agregar(
            Paciente("paciente-demo-003", "Paciente Demo Ana", "+54 9 11 0000-0303")
        )
        uow.commit()

    with UnidadDeTrabajoSQLAlchemy(fabrica) as lectura:
        todos = lectura.pacientes.buscar()
        por_nombre = lectura.pacientes.buscar("ana")
        por_contacto = lectura.pacientes.buscar("0000-0303")
        por_id = lectura.pacientes.buscar("DEMO-002")
        sin_resultados = lectura.pacientes.buscar("no-existe-999")

    assert [p.id for p in todos] == [
        "paciente-demo-003",
        "paciente-demo-001",
        "paciente-demo-002",
    ]
    assert [p.id for p in por_nombre] == ["paciente-demo-003"]
    assert [p.id for p in por_contacto] == ["paciente-demo-003"]
    assert [p.id for p in por_id] == ["paciente-demo-002"]
    assert sin_resultados == []
