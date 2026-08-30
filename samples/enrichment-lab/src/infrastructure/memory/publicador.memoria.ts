import type { ClienteAtualizadoV1 } from '../../domain/cliente/events/cliente-atualizado.v1';
import type { PublicadorDeEventos } from '../../domain/cliente/messaging/publicador.port';

/** Guarda os eventos publicados em memória — o teste de integração observa; o serviço
 * real tem fila de saída. */
export class PublicadorMemoria implements PublicadorDeEventos {
  readonly publicados: ClienteAtualizadoV1[] = [];

  async publicar(evento: ClienteAtualizadoV1): Promise<void> {
    this.publicados.push(evento);
  }

  limpar(): void {
    this.publicados.length = 0;
  }
}
