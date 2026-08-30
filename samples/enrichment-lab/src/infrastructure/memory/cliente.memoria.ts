import { Cliente } from '../../domain/cliente/cliente.entity';
import type { ClienteRepository } from '../../domain/cliente/cliente.repository';
import { ConflictError } from '../../domain/errors/domain-error';

/** Store em memória com a mesma semântica do banco real: gravação condicional por
 * versão
 * (RN-ENR-005). */
export class ClienteRepositoryMemoria implements ClienteRepository {
  private readonly itens = new Map<string, Cliente>();
  private readonly processados = new Set<string>();

  async obter(documento: string): Promise<Cliente | undefined> {
    const c = this.itens.get(documento);
    return c
      ? Cliente.reidratar(c.documento, c.tipoPessoa, c.versao, c.unidades, c.apto)
      : undefined;
  }

  async gravar(cliente: Cliente, versaoEsperada: number): Promise<number> {
    const atual = this.itens.get(cliente.documento);
    const versaoPersistida = atual?.versao ?? 0;
    if (versaoPersistida !== versaoEsperada) {
      throw new ConflictError(
        `escrita concorrente em cliente: esperava versão ${versaoEsperada}, ` +
          `encontrou ${versaoPersistida}`,
      );
    }
    const nova = versaoEsperada + 1;
    this.itens.set(
      cliente.documento,
      Cliente.reidratar(
        cliente.documento,
        cliente.tipoPessoa,
        nova,
        cliente.unidades,
        cliente.apto,
      ),
    );
    return nova;
  }

  async jaProcessado(eventId: string): Promise<boolean> {
    return this.processados.has(eventId);
  }

  async registrarProcessado(eventId: string): Promise<void> {
    this.processados.add(eventId);
  }

  /** Só para testes: cada arquivo de teste começa com o store vazio. */
  limpar(): void {
    this.itens.clear();
    this.processados.clear();
  }
}
