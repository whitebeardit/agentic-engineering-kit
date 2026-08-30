import { NotFoundError } from '../domain/errors/domain-error';
import type { ClienteRepository } from '../domain/cliente/cliente.repository';

export interface ClienteConsolidado {
  documento: string;
  tipoPessoa: 'F' | 'J';
  versao: number;
  apto?: boolean;
  data: Record<string, unknown>;
}

export class ConsultarCliente {
  constructor(private readonly repo: Pick<ClienteRepository, 'obter'>) {}

  async executar(documento: string): Promise<ClienteConsolidado> {
    const cliente = await this.repo.obter(documento);
    if (!cliente) throw new NotFoundError('documento sem cadastro');
    const saida: ClienteConsolidado = {
      documento: cliente.documento,
      tipoPessoa: cliente.tipoPessoa,
      versao: cliente.versao,
      data: cliente.snapshot(),
    };
    if (cliente.apto !== undefined) saida.apto = cliente.apto;
    return saida;
  }
}
