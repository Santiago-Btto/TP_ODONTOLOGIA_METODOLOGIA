"""Tabla `usuarios`, repositorio, comando de alta y actor en el historial (C-08) contra PostgreSQL real."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.domain.autorizacion import Rol
from app.infrastructure.crear_usuario import ContrasenaDebilError, UsuarioDuplicadoError, crear_usuario
from app.infrastructure.modelos import HistorialModelo, UsuarioModelo
from app.infrastructure.seguridad import HasherArgon2
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy, UsuariosSQLAlchemy

HASHER = HasherArgon2()


def alta(fabrica: sessionmaker[Session], nombre: str = "recepcion.demo", rol: Rol = Rol.RECEPCION,
         profesional_id: str | None = None, contrasena: str = "clave-demo-larga-001") -> str:
    with fabrica() as sesion:
        return crear_usuario(sesion, HASHER, nombre, contrasena, rol, profesional_id).id


def test_crear_usuario_guarda_solo_el_hash_argon2id(fabrica: sessionmaker[Session]) -> None:
    usuario_id = alta(fabrica)

    with fabrica() as sesion:
        fila = sesion.get(UsuarioModelo, usuario_id)
        assert fila is not None
        assert (fila.nombre_usuario, fila.rol, fila.activo) == ("recepcion.demo", "recepcion", True)
        assert fila.hash_contrasena.startswith("$argon2id$")
        assert HASHER.verificar("clave-demo-larga-001", fila.hash_contrasena)


def test_crear_usuario_rechaza_contrasena_corta(fabrica: sessionmaker[Session]) -> None:
    with pytest.raises(ContrasenaDebilError):
        alta(fabrica, contrasena="corta")


def test_crear_usuario_rechaza_nombre_duplicado(fabrica: sessionmaker[Session]) -> None:
    alta(fabrica)
    with pytest.raises(UsuarioDuplicadoError):
        alta(fabrica)


def test_odontologo_vinculado_a_un_profesional_existente(fabrica: sessionmaker[Session]) -> None:
    usuario_id = alta(fabrica, "odontologo.demo", Rol.ODONTOLOGO, "profesional-demo-001")

    usuario = UsuariosSQLAlchemy(fabrica).por_id(usuario_id)

    assert usuario is not None
    assert usuario.como_actor().profesional_id == "profesional-demo-001"


def test_la_tabla_rechaza_rol_desconocido_y_profesional_inexistente(fabrica: sessionmaker[Session]) -> None:
    base = dict(nombre_usuario="x.demo", hash_contrasena="h", activo=True)
    with pytest.raises(IntegrityError, match="usuarios_rol_valido"):
        with fabrica() as sesion:
            sesion.execute(insert(UsuarioModelo).values(id="u-demo-1", rol="administrador", **base))
            sesion.commit()
    with pytest.raises(IntegrityError):
        with fabrica() as sesion:
            sesion.execute(insert(UsuarioModelo).values(
                id="u-demo-2", rol="odontologo", profesional_id="profesional-inexistente", **base))
            sesion.commit()


def test_repositorio_busca_por_nombre_e_id(fabrica: sessionmaker[Session]) -> None:
    usuario_id = alta(fabrica)
    repositorio = UsuariosSQLAlchemy(fabrica)

    por_nombre = repositorio.por_nombre("recepcion.demo")

    assert por_nombre is not None and por_nombre.id == usuario_id
    assert repositorio.por_id(usuario_id) == por_nombre
    assert repositorio.por_nombre("inexistente.demo") is None
    assert repositorio.por_id("inexistente") is None


def test_historial_persiste_el_actor(fabrica: sessionmaker[Session]) -> None:
    usuario_id = alta(fabrica)
    CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: datetime(2030, 1, 1, tzinfo=UTC)).ejecutar(
        SolicitudCrearTurno("turno-demo-001", "paciente-demo-001", "profesional-demo-001", "box-demo-001",
                            "prestacion-demo-001", datetime(2030, 1, 10, 9, tzinfo=UTC), actor_id=usuario_id))

    with fabrica() as sesion:
        assert sesion.scalar(select(HistorialModelo.actor_id)) == usuario_id


def test_historial_rechaza_actor_inexistente(fabrica: sessionmaker[Session]) -> None:
    with pytest.raises(IntegrityError):
        CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: datetime(2030, 1, 1, tzinfo=UTC)).ejecutar(
            SolicitudCrearTurno("turno-demo-001", "paciente-demo-001", "profesional-demo-001", "box-demo-001",
                                "prestacion-demo-001", datetime(2030, 1, 10, 9, tzinfo=UTC),
                                actor_id="usuario-inexistente"))
