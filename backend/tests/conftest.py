"""Fixtures de integración contra PostgreSQL real (`TEST_DATABASE_URL`).

Los tests de dominio y de aplicación no usan estas fixtures y corren sin base.
"""

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db import crear_esquema, crear_fabrica_de_sesiones, crear_motor
from app.infrastructure.modelos import Base
from app.infrastructure.semillas import cargar_semillas


@pytest.fixture(scope="session")
def motor() -> Iterator[Engine]:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.fail(
            "Los tests de integración necesitan TEST_DATABASE_URL apuntando a una base PostgreSQL "
            "descartable (ver README.md). Se borra y recrea su esquema."
        )
    motor = crear_motor(url)
    Base.metadata.drop_all(motor)
    crear_esquema(motor)
    yield motor
    motor.dispose()


@pytest.fixture
def fabrica(motor: Engine) -> sessionmaker[Session]:
    tablas = ", ".join(tabla.name for tabla in Base.metadata.sorted_tables)
    with motor.begin() as conexion:
        conexion.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))
    fabrica = crear_fabrica_de_sesiones(motor)
    with fabrica() as sesion:
        cargar_semillas(sesion)
    return fabrica
