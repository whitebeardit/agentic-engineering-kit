import { DomainRuleViolation } from '../errors/domain-rule-violation';
import {
  criarClienteAtualizadoV1,
  type ClienteAtualizadoV1,
} from './events/cliente-atualizado.v1';
import type { EventoIngestao, Origem, TipoPessoa } from './interfaces/evento-ingestao';
import { mesclar } from './service/merge';
import { EventoElegivelParaMerge } from './specifications/evento-elegivel-para-merge';
import { aninhar, type Caminho } from './unidades';

/** Anotação de cada unidade gravada: valor, instante do evento que a escreveu e de
 * quem veio. */
export interface Unidade {
  valor: unknown;
  instante: string;
  origem: Origem;
}

export interface ResultadoAplicacao {
  changed: boolean;
  eventos: ClienteAtualizadoV1[];
}

export class Cliente {
  private constructor(
    readonly documento: string,
    readonly tipoPessoa: TipoPessoa,
    public versao: number,
    readonly unidades: Map<Caminho, Unidade>,
  ) {}

  static novo(documento: string, tipoPessoa: TipoPessoa): Cliente {
    return new Cliente(documento, tipoPessoa, 0, new Map());
  }

  static reidratar(
    documento: string,
    tipoPessoa: TipoPessoa,
    versao: number,
    unidades: Map<Caminho, Unidade>,
  ): Cliente {
    return new Cliente(documento, tipoPessoa, versao, new Map(unidades));
  }

  /**
   * RN-ENR-004 — aplica o evento por unidade (recência e proveniência), recusa evento
   * incompleto
   * contra cadastro completo e emite um `ClienteAtualizado` só quando algo mudou. Não
   * grava: a
   * versão nova é a que a gravação condicional (RN-ENR-005) vai atribuir.
   */
  aplicar(evento: EventoIngestao, limiarN: number): ResultadoAplicacao {
    const elegivel = EventoElegivelParaMerge.estaSatisfeitaPor(this, evento, limiarN);
    if (!elegivel.ok) throw new DomainRuleViolation('RN-ENR-004', elegivel.motivo);
    const { unidades, changed } = mesclar(this.unidades, evento);
    if (!changed) return { changed: false, eventos: [] };
    this.unidades.clear();
    for (const [c, u] of unidades) this.unidades.set(c, u);
    return {
      changed: true,
      eventos: [criarClienteAtualizadoV1(this.documento, this.versao + 1)],
    };
  }

  /** `apto` é uma unidade como as outras — merge pelas mesmas regras. */
  get apto(): boolean | undefined {
    return this.unidades.get('apto')?.valor as boolean | undefined;
  }

  /** Quantidade de unidades de dados (não conta `apto`): é o que o limiar mede. */
  get quantidadeDeCampos(): number {
    return this.unidades.has('apto') ? this.unidades.size - 1 : this.unidades.size;
  }

  snapshot(): Record<string, unknown> {
    const valores = new Map<Caminho, unknown>();
    for (const [c, u] of this.unidades) if (c !== 'apto') valores.set(c, u.valor);
    return aninhar(valores);
  }
}
