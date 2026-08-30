import { DomainError } from './domain-error';

/**
 * Recusa por regra de negócio. `ruleId` é o ID do bloco em
 * docs/regras/enriquecimento.md — o mesmo que está
 * no nome do teste. Só o domínio lança (ADR-0004); o worker captura, loga `{ ruleId,
 * motivo }` e faz ack:
 * descarte por regra não é retry.
 */
export class DomainRuleViolation extends DomainError {
  constructor(
    readonly ruleId: string,
    readonly motivo: string,
    message = `${ruleId}: ${motivo}`,
  ) {
    super(message, 422);
  }
}
