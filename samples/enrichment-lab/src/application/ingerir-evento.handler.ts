import type { EventoIngestao } from '../domain/cliente/interfaces/evento-ingestao';
import type { FilaPort } from '../domain/cliente/messaging/fila.port';

/** Orquestra, não decide: valida na borda (feito antes, pelo validador), enfileira e
 * devolve o cid. */
export class IngerirEventoHandler {
  constructor(private readonly fila: FilaPort<EventoIngestao>) {}

  async executar(
    evento: EventoIngestao,
    cid: string,
  ): Promise<{ message: 'aceito'; cid: string }> {
    await this.fila.publicar({
      grupo: evento.documento,
      dedupId: evento.eventId,
      cid,
      corpo: evento,
    });
    return { message: 'aceito', cid };
  }
}
