import type { RepositorioHistoriales } from "../../application/puertos.ts";
import type { HistorialDeCambio } from "../../domain/turnos.ts";

export class RepositorioHistorialesEnMemoria implements RepositorioHistoriales {
  private readonly historiales: HistorialDeCambio[] = [];

  public guardar(historial: HistorialDeCambio): void {
    this.historiales.push(historial);
  }

  public todos(): readonly HistorialDeCambio[] {
    return [...this.historiales];
  }
}
