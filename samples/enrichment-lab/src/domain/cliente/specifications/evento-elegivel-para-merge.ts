import type { Cliente } from '../cliente.entity';
import { ehProvedor, type EventoIngestao } from '../interfaces/evento-ingestao';
import { achatar } from '../unidades';

export type Elegibilidade = { ok: true } | { ok: false; motivo: 'descartado-limiar' };

/**
 * RN-ENR-004 (ING-05) — limiar de completude: um evento com menos de N unidades não
 * pode alterar um cadastro
 * que já tem N ou mais. Evento de provedor nunca é recusado por isto.
 */
export const EventoElegivelParaMerge = {
  estaSatisfeitaPor(
    cliente: Cliente,
    evento: EventoIngestao,
    limiarN: number,
  ): Elegibilidade {
    if (ehProvedor(evento.origin)) return { ok: true };
    const trazidas = achatar(evento.data).size;
    if (cliente.quantidadeDeCampos >= limiarN && trazidas < limiarN) {
      return { ok: false, motivo: 'descartado-limiar' };
    }
    return { ok: true };
  },
};
