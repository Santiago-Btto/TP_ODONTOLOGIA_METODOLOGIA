"""Alta de usuarios del personal sin versionar contraseñas (C-08).

Uso: `python -m app.infrastructure.crear_usuario --nombre recepcion.demo --rol recepcion`
La contraseña se pide por consola o se toma de `CONTRASENA_NUEVO_USUARIO`; nunca se imprime.
"""

import argparse
import getpass
import os
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.autorizacion import Rol, Usuario
from app.infrastructure.db import crear_esquema, crear_fabrica_de_sesiones, crear_motor, url_de_base
from app.infrastructure.modelos import UsuarioModelo
from app.infrastructure.seguridad import HasherArgon2

LARGO_MINIMO_CONTRASENA = 12


class ContrasenaDebilError(ValueError):
    def __init__(self) -> None:
        super().__init__(f"La contraseña debe tener al menos {LARGO_MINIMO_CONTRASENA} caracteres.")


class UsuarioDuplicadoError(ValueError):
    def __init__(self, nombre_usuario: str) -> None:
        super().__init__(f"Ya existe el usuario '{nombre_usuario}'.")


def crear_usuario(
    sesion: Session,
    hasher: HasherArgon2,
    nombre_usuario: str,
    contrasena: str,
    rol: Rol,
    profesional_id: str | None = None,
) -> Usuario:
    if len(contrasena) < LARGO_MINIMO_CONTRASENA:
        raise ContrasenaDebilError()
    if sesion.scalar(select(UsuarioModelo.id).where(UsuarioModelo.nombre_usuario == nombre_usuario)) is not None:
        raise UsuarioDuplicadoError(nombre_usuario)
    usuario = Usuario(str(uuid4()), nombre_usuario, hasher.hashear(contrasena), rol, profesional_id)
    sesion.add(UsuarioModelo(
        id=usuario.id, nombre_usuario=usuario.nombre_usuario, hash_contrasena=usuario.hash_contrasena,
        rol=usuario.rol.value, profesional_id=usuario.profesional_id, activo=True,
    ))
    sesion.commit()
    return usuario


def _leer_contrasena() -> str:
    desde_entorno = os.environ.get("CONTRASENA_NUEVO_USUARIO")
    if desde_entorno:
        return desde_entorno
    primera = getpass.getpass("Contraseña: ")
    if primera != getpass.getpass("Repetir contraseña: "):
        raise SystemExit("Las contraseñas no coinciden.")
    return primera


def main() -> None:
    argumentos = argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument("--nombre", required=True, help="Nombre de usuario (único).")
    argumentos.add_argument("--rol", required=True, choices=[r.value for r in Rol])
    argumentos.add_argument("--profesional-id", default=None, help="Profesional vinculado (odontólogo/a).")
    opciones = argumentos.parse_args()

    motor = crear_motor(url_de_base())
    crear_esquema(motor)
    with crear_fabrica_de_sesiones(motor)() as sesion:
        try:
            usuario = crear_usuario(sesion, HasherArgon2(), opciones.nombre, _leer_contrasena(),
                                    Rol(opciones.rol), opciones.profesional_id)
        except ValueError as error:
            raise SystemExit(str(error)) from error
    print(f"Usuario creado: {usuario.nombre_usuario} ({usuario.rol.value}), id {usuario.id}")


if __name__ == "__main__":
    main()
