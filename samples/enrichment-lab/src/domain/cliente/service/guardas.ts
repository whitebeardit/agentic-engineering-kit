import { DomainRuleViolation } from '../../errors/domain-rule-violation';
import type { EventoIngestao } from '../interfaces/evento-ingestao';
import { exigirDocumentoValido } from '../documento';
import { achatar, aninhar } from '../unidades';
import type { ClienteRepository } from '../cliente.repository';
import { inferirApto } from './apto';

export interface BlacklistConfig {
  /** Valores proibidos em qualquer unidade (ex.: placeholders que sistemas antigos
   * mandam). */
  global: readonly string[];
  /** Valores proibidos por caminho (ex.: contato.email → ["nao@informado.com"]). */
  porCaminho: Readonly<Record<string, readonly string[]>>;
}

export type ResultadoGuarda =
  { ok: true; evento: EventoIngestao } | { ok: false; motivo: 'duplicado' };

/**
 * Ordem fixa das guardas (docs/regras/enriquecimento.md): idempotência → dígitos →
 * blacklist → apto (RN-ENR-006) → limiar (RN-ENR-004).
 * Descarte por regra lança DomainRuleViolation; duplicado devolve `ok: false` (não é
 * erro, é ack).
 */
export async function aplicarGuardas(
  evento: EventoIngestao,
  repo: Pick<ClienteRepository, 'jaProcessado'>,
  blacklist: BlacklistConfig,
): Promise<ResultadoGuarda> {
  // RN-ENR-002 — idempotência por eventId
  if (await repo.jaProcessado(evento.eventId))
    return { ok: false, motivo: 'duplicado' };
  // RN-ENR-001 — documento válido
  exigirDocumentoValido(evento.documento, evento.tipoPessoa);
  // RN-ENR-003 — blacklist remove a unidade, não o evento
  const unidades = achatar(evento.data);
  for (const [caminho, valor] of unidades) {
    const texto = typeof valor === 'string' ? valor : undefined;
    const proibido =
      texto !== undefined &&
      (blacklist.global.includes(texto) ||
        (blacklist.porCaminho[caminho] ?? []).includes(texto));
    if (proibido) unidades.delete(caminho);
  }
  if (unidades.size === 0 && evento.apto === undefined) {
    throw new DomainRuleViolation('RN-ENR-003', 'descartado-blacklist');
  }
  // RN-ENR-006 — apto inferido pelo legado quando o evento não declara
  return { ok: true, evento: inferirApto({ ...evento, data: aninhar(unidades) }) };
}
