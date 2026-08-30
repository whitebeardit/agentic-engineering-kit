import { calculaApto } from '../../../../legacy/calcula-apto';
import type { EventoIngestao } from '../interfaces/evento-ingestao';
import { achatar } from '../unidades';

/**
 * RN-ENR-006 — Aptidão inferida pelo legado: quando o evento não declara `apto`, a pontuação de
 * `legacy/calcula-apto.js` decide (só "APTO" vira true). Ninguém explica os pesos; o characterization
 * test congela o comportamento.
 */
export function inferirApto(evento: EventoIngestao): EventoIngestao {
  if (evento.apto !== undefined) return evento;
  const campos = Object.fromEntries(achatar(evento.data));
  return {
    ...evento,
    apto: calculaApto(campos, evento.tipoPessoa, evento.origin) === 'APTO',
  };
}
