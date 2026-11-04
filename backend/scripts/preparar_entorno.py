"""Prepara credenciales locales del MVP en el .env ignorado por Git.

Uso desde la raíz: python backend/scripts/preparar_entorno.py
"""

import argparse
import os
import secrets
from pathlib import Path


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
MENSAJE_INVALIDO = "Configuración local incompleta o inválida. Revisá .env sin compartir sus valores."


def leer_configuracion(ruta: Path) -> dict[str, str]:
    valores: dict[str, str] = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if not linea or linea.lstrip().startswith("#"):
            continue
        if "=" not in linea:
            raise ValueError(MENSAJE_INVALIDO)
        clave, valor = linea.split("=", 1)
        if clave in valores:
            raise ValueError(MENSAJE_INVALIDO)
        valores[clave] = valor
    if len(valores.get("JWT_SECRET", "")) < 32 or len(valores.get("DEMO_PASSWORD", "")) < 12:
        raise ValueError(MENSAJE_INVALIDO)
    return valores


def preparar(ruta: Path) -> None:
    if ruta.exists():
        leer_configuracion(ruta)
        return
    secreto = secrets.token_urlsafe(48)
    contrasena = secrets.token_urlsafe(24)
    try:
        descriptor = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        leer_configuracion(ruta)
        return
    with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
        archivo.write(f"JWT_SECRET={secreto}\nDEMO_PASSWORD={contrasena}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RAIZ_PROYECTO / ".env")
    argumentos = parser.parse_args()
    try:
        preparar(argumentos.output)
    except (OSError, UnicodeError, ValueError) as error:
        if isinstance(error, ValueError):
            parser.exit(1, f"{MENSAJE_INVALIDO}\n")
        parser.exit(1, "No se pudo preparar .env local. Verificá permisos y ruta.\n")
    print("Configuración local preparada; las credenciales permanecen en el archivo .env.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
