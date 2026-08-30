import type { Cliente } from './cliente.entity';

/** Porta de persistência, definida no domínio e implementada em infrastructure
 * (ADR-0003). */
export interface ClienteRepository {
  obter(documento: string): Promise<Cliente | undefined>;
  /**
   * RN-ENR-005 — gravação condicional por versão: grava só se a versão persistida for
   * `versaoEsperada`
   * (0 = ainda não existe); senão lança ConflictError e quem chamou relê e refaz o
   * merge.
   */
  gravar(cliente: Cliente, versaoEsperada: number): Promise<number>;
  jaProcessado(eventId: string): Promise<boolean>;
  registrarProcessado(eventId: string): Promise<void>;
}
