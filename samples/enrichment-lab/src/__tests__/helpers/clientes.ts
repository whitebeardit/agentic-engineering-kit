import { Cliente, type Unidade } from '../../domain/cliente/cliente.entity';
import type { Origem } from '../../domain/cliente/interfaces/evento-ingestao';
import { CPF_VALIDO } from './eventos';

/** Cadastro sintético com `n` unidades `campo.i`, todas com o mesmo instante e origem. */
export function clienteComUnidades(
  n: number,
  instante = '2026-08-30T12:00:00.000Z',
  origem: Origem = 'cliente:app',
  versao = 1,
): Cliente {
  const unidades = new Map<string, Unidade>();
  for (let i = 1; i <= n; i++)
    unidades.set(`campo.c${i}`, { valor: `v${i}`, instante, origem });
  return Cliente.reidratar(CPF_VALIDO, 'F', versao, unidades);
}
