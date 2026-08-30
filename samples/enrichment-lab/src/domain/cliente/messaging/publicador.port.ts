import type { ClienteAtualizadoV1 } from '../events/cliente-atualizado.v1';

/** Porta de publicação dos eventos deste serviço; implementada em infrastructure. */
export interface PublicadorDeEventos {
  publicar(evento: ClienteAtualizadoV1): Promise<void>;
}
