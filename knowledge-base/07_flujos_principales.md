# Flujos Principales

## Flujo 1: Crear un turno sin conflicto

**Disparador**: recepción solicita una reserva.
**Actor**: recepción / secretaría.

**Pasos**:

1. El adaptador futuro o ejecutable entrega paciente ficticio, prestación, profesional, box e inicio al caso de uso.
2. El caso de uso verifica que los campos y el intervalo sean válidos.
3. El dominio calcula o verifica el fin según la prestación.
4. El dominio consulta turnos activos y bloqueos del profesional y del box.
5. Si no hay intersección, crea el turno y registra `creado` en el historial.
6. El caso de uso devuelve el turno creado.

```text
Recepción -> Caso de uso -> Dominio disponibilidad -> Repositorio en memoria
Recepción <- Resultado    <- Turno válido          <- Guardado
```

**Casos de error**:

- Falta un recurso o el intervalo es inválido -> rechazo con motivo de validación.
- Se cruza el profesional -> rechazo que identifica el conflicto de profesional.
- Se cruza el box -> rechazo que identifica el conflicto de box.
- Sólo toca el borde de un turno existente -> se acepta, pues es contiguo.

## Flujo 2: Reprogramar un turno

**Disparador**: se solicita cambiar horario, profesional y/o box.
**Actor**: recepción / secretaría.

**Pasos**:

1. El caso de uso obtiene el turno actual.
2. El dominio construye el intervalo candidato y excluye el propio turno de la comparación.
3. Valida el candidato contra los demás turnos activos y bloqueos de ambos recursos.
4. Si pasa la validación, reemplaza el intervalo/recurso y registra el resumen anterior y posterior.
5. Si falla, conserva el turno original sin liberar ni reservar parcialmente nada.

**Casos de error**:

- El turno no existe o ya está cancelado -> comportamiento pendiente de precisar.
- El nuevo profesional o box tiene conflicto -> rechazo atómico; se preserva el estado previo.

## Flujo 3: Cancelar un turno y reutilizar el horario

**Disparador**: recepción registra una cancelación.
**Actor**: recepción / secretaría.

**Pasos**:

1. El caso de uso identifica el turno existente.
2. El dominio cambia su estado a cancelado y registra el cambio.
3. La consulta de disponibilidad deja de considerar ese turno como reserva activa.
4. Una reserva posterior puede ocupar ese mismo intervalo si no hay otro conflicto.

**Casos de error**:

- La ventana temporal y quién está autorizado a cancelar aún no están definidos.
- El eventual aviso al paciente o lista de espera no forma parte del MVP.

## Flujo 4: Bloquear disponibilidad

**Disparador**: se debe reservar tiempo no clínico o indisponible.
**Actor**: recepción o responsable de clínica.

**Pasos**:

1. Se registra un intervalo válido asociado a un profesional o box.
2. El dominio persiste el bloqueo en memoria.
3. Altas y reprogramaciones futuras consultan el bloqueo junto a los turnos.
4. Una operación intersectante se rechaza de forma consistente, cualquiera sea su canal futuro.

**Casos de error**:

- La resolución de bloqueos que se crucen con turnos ya existentes no fue acordada.
