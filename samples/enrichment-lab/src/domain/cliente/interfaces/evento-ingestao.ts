/** Forma do evento depois de validado na borda (evento-ingestao.schema.json). Espelha o
 * schema; não o substitui. */
export type Origem = `cliente:${string}` | `provedor:${string}`;
export type TipoPessoa = 'F' | 'J';

export interface DadosCadastro {
  cadastro?: { nome?: string; canalEntrada?: 'app' | 'site' | 'loja' | 'parceiro' };
  contato?: { email?: string; telefone?: string };
  endereco?: { cep?: string; cidade?: string; uf?: string };
}

export interface EventoIngestao {
  schemaVersion: '2.1';
  type: 'CLIENTE.NOVO' | 'CLIENTE.ATUALIZADO';
  origin: Origem;
  eventId: string;
  updatedAt: string;
  documento: string;
  tipoPessoa: TipoPessoa;
  apto?: boolean;
  data: DadosCadastro;
}

export function ehProvedor(origin: Origem): boolean {
  return origin.startsWith('provedor:');
}
