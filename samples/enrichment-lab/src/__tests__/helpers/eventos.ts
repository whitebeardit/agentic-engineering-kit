import { randomUUID } from 'node:crypto';
import type { EventoIngestao } from '../../domain/cliente/interfaces/evento-ingestao';

/** CPF e CNPJ sintéticos com dígitos válidos (gerados pela RN-ENR-001, não copiados de
 * lugar nenhum). */
export const CPF_VALIDO = '52998224725';
export const CNPJ_VALIDO = '11444777000161';

export function eventoValido(extra: Partial<EventoIngestao> = {}): EventoIngestao {
  return {
    schemaVersion: '2.1',
    type: 'CLIENTE.NOVO',
    origin: 'cliente:app',
    eventId: randomUUID(),
    updatedAt: '2026-08-30T12:00:00Z',
    documento: CPF_VALIDO,
    tipoPessoa: 'F',
    data: {
      cadastro: { nome: 'Ana Exemplo', canalEntrada: 'app' },
      contato: { email: 'ana@exemplo.test', telefone: '11999990000' },
      endereco: { cep: '01001000', cidade: 'São Paulo', uf: 'SP' },
    },
    ...extra,
  };
}
