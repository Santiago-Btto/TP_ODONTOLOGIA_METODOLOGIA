"""Ejecuta el MVP por HTTP en un proyecto Compose aislado y lo limpia siempre.

Uso desde la raíz: python backend/scripts/ejecutar_e2e.py
Requiere ejecutar antes preparar_entorno.py; nunca imprime credenciales.
"""

import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


RAIZ = Path(__file__).resolve().parents[2]
NOMBRE = f"c06e2e{uuid4().hex[:12]}"
COMPOSE = ["docker", "compose", "-p", NOMBRE, "-f", "docker-compose.yml", "-f", "docker-compose.e2e.yml"]


def comprobar_aislamiento() -> bool:
    resultado = subprocess.run(
        [*COMPOSE, "config", "--format", "json"],
        cwd=RAIZ, capture_output=True, text=True, check=False,
    )
    if resultado.returncode:
        print("No se pudo leer la configuración E2E. Ejecutá primero preparar_entorno.py.", file=sys.stderr)
        return False
    servicios = json.loads(resultado.stdout)["services"]
    for nombre in ("db", "redis", "api", "frontend", "worker", "bootstrap", "e2e"):
        if nombre not in servicios or servicios[nombre].get("ports"):
            print("El entorno E2E debe contener todos los servicios sin publicar puertos.", file=sys.stderr)
            return False
    return True


def ejecutar(*argumentos: str) -> int:
    return subprocess.run([*COMPOSE, *argumentos], cwd=RAIZ, check=False).returncode


def main() -> int:
    if not comprobar_aislamiento():
        return 2
    print(f"Iniciando verificación en proyecto aislado {NOMBRE}.", flush=True)
    estado = 0
    try:
        if ejecutar("up", "-d", "--build", "--wait", "db", "redis", "bootstrap", "api", "frontend", "worker"):
            print("El stack E2E no llegó al estado saludable.", file=sys.stderr)
            estado = 1
        elif ejecutar("run", "--rm", "--no-deps", "e2e"):
            print("La prueba HTTP E2E falló.", file=sys.stderr)
            estado = 1
    finally:
        if ejecutar("down", "--volumes", "--remove-orphans"):
            print("La limpieza del proyecto E2E falló; revisar Docker.", file=sys.stderr)
            estado = 1
    if estado == 0:
        print("Recorrido E2E completo y verificado.")
    return estado


if __name__ == "__main__":
    raise SystemExit(main())
