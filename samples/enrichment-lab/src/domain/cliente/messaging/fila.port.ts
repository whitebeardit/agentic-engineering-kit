/** Porta da fila: FIFO por grupo (documento) com deduplicação por id (eventId).
 * Implementação em infrastructure. */
export interface Mensagem<T = unknown> {
  id: string;
  grupo: string;
  dedupId: string;
  cid: string;
  corpo: T;
  tentativas: number;
}

export interface FilaPort<T = unknown> {
  publicar(entrada: {
    grupo: string;
    dedupId: string;
    cid: string;
    corpo: T;
  }): Promise<boolean>;
  receber(): Promise<Mensagem<T> | undefined>;
  confirmar(id: string): Promise<void>;
  devolver(id: string): Promise<void>;
}
