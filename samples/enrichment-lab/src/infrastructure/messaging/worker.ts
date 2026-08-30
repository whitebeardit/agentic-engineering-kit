import { Cliente } from '../../domain/cliente/cliente.entity';
import { mascarar } from '../../domain/cliente/documento';
import type { EventoIngestao } from '../../domain/cliente/interfaces/evento-ingestao';
import type { FilaPort } from '../../domain/cliente/messaging/fila.port';
import type { ClienteRepository } from '../../domain/cliente/cliente.repository';
import {
  aplicarGuardas,
  type BlacklistConfig,
} from '../../domain/cliente/service/guardas';
import { ConflictError } from '../../domain/errors/domain-error';
import { DomainRuleViolation } from '../../domain/errors/domain-rule-violation';
import type { Logger } from '../telemetry/logger';

export type Resultado = 'gravado' | 'duplicado' | 'descartado' | 'retry';

/** Consome a fila: guardas → aplica o evento → gravação condicional (com releitura em
 * conflito) → ack. */
export class EventoIngestaoWorker {
  constructor(
    private readonly fila: FilaPort<EventoIngestao>,
    private readonly repo: ClienteRepository,
    private readonly blacklist: BlacklistConfig,
    private readonly log: Logger,
    private readonly maxTentativasDeEscrita = 3,
  ) {}

  /** Processa tudo que está pendente e devolve os resultados na ordem. Útil em testes e
   * no modo lote. */
  async processarPendentes(): Promise<Resultado[]> {
    const resultados: Resultado[] = [];
    for (;;) {
      const m = await this.fila.receber();
      if (!m) return resultados;
      resultados.push(await this.processar(m.id, m.corpo, m.cid));
    }
  }

  private async processar(
    id: string,
    evento: EventoIngestao,
    cid: string,
  ): Promise<Resultado> {
    const ctx = {
      trace_id: cid,
      cid,
      eventId: evento.eventId,
      documento: mascarar(evento.documento),
    };
    try {
      const guarda = await aplicarGuardas(evento, this.repo, this.blacklist);
      if (!guarda.ok) {
        this.log.info('evento duplicado, ack', ctx);
        await this.fila.confirmar(id);
        return 'duplicado';
      }
      await this.gravarComRetry(guarda.evento);
      await this.repo.registrarProcessado(evento.eventId);
      await this.fila.confirmar(id);
      this.log.info('evento gravado', ctx);
      return 'gravado';
    } catch (erro) {
      if (erro instanceof DomainRuleViolation) {
        // Descarte por regra: registra o ID da regra e o motivo, e faz ack — retry não
        // muda o resultado.
        this.log.warn('evento descartado por regra', {
          ...ctx,
          ruleId: erro.ruleId,
          motivo: erro.motivo,
        });
        await this.repo.registrarProcessado(evento.eventId);
        await this.fila.confirmar(id);
        return 'descartado';
      }
      this.log.error('falha técnica, devolvendo à fila', {
        ...ctx,
        erro: String(erro),
      });
      await this.fila.devolver(id);
      return 'retry';
    }
  }

  private async gravarComRetry(evento: EventoIngestao): Promise<void> {
    for (let tentativa = 1; ; tentativa++) {
      const cliente =
        (await this.repo.obter(evento.documento)) ??
        Cliente.novo(evento.documento, evento.tipoPessoa);
      const versaoEsperada = cliente.versao;
      cliente.aplicar(evento, 11);
      try {
        await this.repo.gravar(cliente, versaoEsperada);
        return;
      } catch (erro) {
        if (
          !(erro instanceof ConflictError) ||
          tentativa >= this.maxTentativasDeEscrita
        )
          throw erro;
      }
    }
  }
}
