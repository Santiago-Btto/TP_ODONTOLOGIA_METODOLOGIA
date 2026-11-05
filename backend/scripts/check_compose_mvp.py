"""Comprueba el contrato de arranque de Compose sin mostrar secretos.

Uso desde la raíz: python backend/scripts/check_compose_mvp.py
"""

import json
import subprocess
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]


def cargar_compose() -> dict[str, object]:
    resultado = subprocess.run(
        ["docker", "compose", "config", "--no-interpolate", "--format", "json"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode:
        raise RuntimeError("docker compose config no pudo interpretar el archivo MVP")
    return json.loads(resultado.stdout)


class ConfiguracionComposeMVP(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.servicios = cargar_compose()["services"]

    def test_servicios_obligatorios_y_salud(self) -> None:
        self.assertEqual(set(self.servicios), {"db", "redis", "bootstrap", "api", "frontend", "worker"})
        for nombre in ("db", "redis", "api"):
            self.assertIn("healthcheck", self.servicios[nombre])

    def test_dependencias_del_arranque(self) -> None:
        self.assertEqual(self.servicios["bootstrap"]["depends_on"]["db"]["condition"], "service_healthy")
        self.assertEqual(self.servicios["api"]["depends_on"]["bootstrap"]["condition"], "service_completed_successfully")
        self.assertNotIn("redis", self.servicios["api"].get("depends_on", {}))
        self.assertEqual(self.servicios["frontend"]["depends_on"]["api"]["condition"], "service_healthy")
        self.assertEqual(self.servicios["worker"]["depends_on"]["redis"]["condition"], "service_healthy")
        self.assertEqual(self.servicios["worker"]["depends_on"]["bootstrap"]["condition"], "service_completed_successfully")

    def test_worker_se_reinicia_si_termina(self) -> None:
        self.assertEqual(self.servicios["worker"].get("restart"), "unless-stopped")

    def test_credenciales_son_variables_obligatorias(self) -> None:
        for nombre in ("bootstrap", "api"):
            self.assertTrue(self.servicios[nombre]["environment"]["JWT_SECRET"].startswith("${JWT_SECRET:?"))
        self.assertTrue(self.servicios["bootstrap"]["environment"]["DEMO_PASSWORD"].startswith("${DEMO_PASSWORD:?"))


if __name__ == "__main__":
    unittest.main()
