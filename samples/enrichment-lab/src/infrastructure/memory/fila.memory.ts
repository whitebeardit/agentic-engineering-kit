import { randomUUID } from 'node:crypto';
import type { FilaPort, Mensagem } from '../../domain/cliente/messaging/fila.port';

/**
 * Fila FIFO em processo com a semântica que o livro ensina: ordem por grupo,
 * deduplicação por id,
 * redelivery ao devolver e DLQ após `maxRecebimentos`. O serviço real usa uma fila
 * gerenciada — as
 * mesmas quatro propriedades, só que fora do processo.
 */
export class FilaMemoria<T = unknown> implements FilaPort<T> {
  private readonly pendentes: Mensagem<T>[] = [];
  private readonly emVoo = new Map<string, Mensagem<T>>();
  private readonly dedup = new Set<string>();
  readonly dlq: Mensagem<T>[] = [];

  constructor(private readonly maxRecebimentos = 5) {}

  async publicar(entrada: {
    grupo: string;
    dedupId: string;
    cid: string;
    corpo: T;
  }): Promise<boolean> {
    if (this.dedup.has(entrada.dedupId)) return false;
    this.dedup.add(entrada.dedupId);
    this.pendentes.push({ id: randomUUID(), tentativas: 0, ...entrada });
    return true;
  }

  async receber(): Promise<Mensagem<T> | undefined> {
    const gruposEmVoo = new Set([...this.emVoo.values()].map((m) => m.grupo));
    const i = this.pendentes.findIndex((m) => !gruposEmVoo.has(m.grupo));
    if (i < 0) return undefined;
    const [m] = this.pendentes.splice(i, 1) as [Mensagem<T>];
    m.tentativas += 1;
    this.emVoo.set(m.id, m);
    return m;
  }

  async confirmar(id: string): Promise<void> {
    this.emVoo.delete(id);
  }

  async devolver(id: string): Promise<void> {
    const m = this.emVoo.get(id);
    if (!m) return;
    this.emVoo.delete(id);
    if (m.tentativas >= this.maxRecebimentos) this.dlq.push(m);
    else this.pendentes.unshift(m);
  }

  get tamanho(): number {
    return this.pendentes.length;
  }

  limpar(): void {
    this.pendentes.length = 0;
    this.emVoo.clear();
    this.dedup.clear();
    this.dlq.length = 0;
  }
}
