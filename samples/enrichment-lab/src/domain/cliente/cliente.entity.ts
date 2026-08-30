import type { EventoIngestao, Origem, TipoPessoa } from './interfaces/evento-ingestao';
import { achatar, aninhar, type Caminho } from './unidades';

/** Anotação de cada unidade gravada: valor, instante do evento que a escreveu e de quem
 * veio. */
export interface Unidade {
  valor: unknown;
  instante: string;
  origem: Origem;
}

export class Cliente {
  private constructor(
    readonly documento: string,
    readonly tipoPessoa: TipoPessoa,
    public versao: number,
    readonly unidades: Map<Caminho, Unidade>,
    public apto: boolean | undefined,
  ) {}

  static novo(documento: string, tipoPessoa: TipoPessoa): Cliente {
    return new Cliente(documento, tipoPessoa, 0, new Map(), undefined);
  }

  static reidratar(
    documento: string,
    tipoPessoa: TipoPessoa,
    versao: number,
    unidades: Map<Caminho, Unidade>,
    apto: boolean | undefined,
  ): Cliente {
    return new Cliente(documento, tipoPessoa, versao, new Map(unidades), apto);
  }

  /**
   * Substitui o cadastro pelo conteúdo do evento (comportamento provisório).
   * A regra de merge por unidade — RN-ENR-004 — chega com a feature 001 (card ENR-042).
   */
  substituir(evento: EventoIngestao): void {
    this.unidades.clear();
    for (const [caminho, valor] of achatar(evento.data)) {
      this.unidades.set(caminho, {
        valor,
        instante: evento.updatedAt,
        origem: evento.origin,
      });
    }
    if (evento.apto !== undefined) this.apto = evento.apto;
  }

  get quantidadeDeCampos(): number {
    return this.unidades.size;
  }

  snapshot(): Record<string, unknown> {
    const valores = new Map<Caminho, unknown>();
    for (const [c, u] of this.unidades) valores.set(c, u.valor);
    return aninhar(valores);
  }
}
