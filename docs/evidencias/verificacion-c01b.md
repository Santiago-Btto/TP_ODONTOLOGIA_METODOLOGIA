# Verify — C-01b `crear-turno-sin-solapamientos-fastapi`

**Fecha:** 2026-10-08

La instalación no ofrece una fase de verificación como comando propio, así que la suite se ejecutó a mano.

## Entorno

- Python 3.12.10, FastAPI 0.115.6, SQLAlchemy 2.0.36, psycopg 3.2.3, pytest 8.3.4.
- PostgreSQL 17.11 local (clúster descartable, extensión `btree_gist`).
- Docker no estaba instalado en la máquina de verificación: la opción A del README (Docker Compose) **no se ejecutó**; se verificó la opción B (Python + PostgreSQL locales).

## Ejecución desde un clon limpio, siguiendo sólo el README (opción B)

```text
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt
TEST_DATABASE_URL=postgresql+psycopg://...@localhost:55432/turnos_limpio .venv/Scripts/python -m pytest -v
...
============================= 40 passed in 5.33s ==============================
```

Prueba de humo adicional con `uvicorn app.api.main:app` y semillas ficticias: `GET /health` → `200 {"estado":"ok","base_de_datos":"ok"}`; `POST /api/v1/turnos` → `201`; segundo alta solapada del mismo profesional → `409 conflicto_profesional`; `GET /docs` → `200`.

## Trazabilidad escenario → test

| Escenario del spec | Tests |
|---|---|
| Alta exitosa | `application/test_crear_turno.py::test_alta_exitosa_crea_el_turno_y_un_unico_historial_creado`; `infrastructure/test_persistencia.py::test_alta_por_caso_de_uso_persiste_turno_e_historial_en_postgresql` |
| Conflicto por profesional | `application/...::test_conflicto_por_profesional_no_escribe_turno_ni_historial`; `domain/test_disponibilidad.py::test_informa_conflicto_por_profesional_aunque_el_box_sea_distinto` |
| Conflicto por box | `application/...::test_conflicto_por_box_no_escribe_turno_ni_historial`; `domain/...::test_informa_conflicto_por_box_aunque_el_profesional_sea_distinto` |
| Reserva contigua (borde) | `application/...::test_reserva_contigua_con_mismo_profesional_y_box_se_crea`; `domain/...::test_admite_intervalos_contiguos_en_ambos_bordes` |
| Intervalo sin duración positiva | `application/...::test_intervalo_sin_duracion_positiva_no_persiste_cambios[fin0, fin1]`; `domain/test_turnos.py::test_rechaza_un_intervalo_cuyo_fin_*` |
| Prestación con duración inválida | `application/...::test_prestacion_con_duracion_invalida_no_persiste_cambios[0, -30]`; `domain/test_turnos.py::test_rechaza_una_prestacion_de_duracion_no_positiva` |
| Profesional inexistente | `application/...::test_recurso_inexistente_no_persiste_cambios[paciente_id, profesional_id, box_id, prestacion_id]` |
| Escritura solapada que elude la aplicación | `infrastructure/...::test_la_base_rechaza_un_solapamiento_de_profesional_insertado_directamente`, `..._de_box_insertado_directamente`, `test_carrera_entre_dos_altas_se_traduce_a_conflicto_sin_estado_parcial` |
| Escritura contigua directa | `infrastructure/...::test_la_base_acepta_un_turno_contiguo_insertado_directamente` |
| Alta por API | `api/test_turnos_api.py::test_alta_por_api_responde_201_con_el_turno` |
| Conflicto por API | `api/...::test_conflicto_de_profesional_por_api_responde_409`, `test_conflicto_de_box_por_api_responde_409` |
| Intervalo inválido por API | `api/...::test_intervalo_invalido_por_api_responde_422`, `test_fecha_sin_zona_horaria_responde_422` |
| Recurso inexistente por API | `api/...::test_recurso_inexistente_por_api_responde_404` |

## Hallazgo durante Apply

El primer intento de persistir turno + historial falló (`ForeignKeyViolation`): sin una relación ORM declarada, SQLAlchemy no garantiza insertar el turno antes que su historial. Se corrigió con un `flush` del turno que traduce la violación de la restricción de exclusión al conflicto de dominio correspondiente. El comportamiento especificado no cambió; se ajustó una frase del `design.md` para reflejarlo.
