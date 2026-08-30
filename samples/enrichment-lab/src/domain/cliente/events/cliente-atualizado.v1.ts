/**
 * Contrato público (v1): consumido por outro serviço (CRM). Mudar campo = `cliente-atualizado.v2.ts`, nunca
 * edição in-place (AD-001; rules/contracts.md). Catalogado em src/contracts/asyncapi.yaml.
 */
export interface ClienteAtualizadoV1 {
  readonly type: 'ClienteAtualizado';
  readonly version: 1;
  readonly documento: string;
  readonly versao: number;
  readonly occurredAt: string;
}

export function criarClienteAtualizadoV1(
  documento: string,
  versao: number,
  agora: Date = new Date(),
): ClienteAtualizadoV1 {
  return Object.freeze({
    type: 'ClienteAtualizado',
    version: 1,
    documento,
    versao,
    occurredAt: agora.toISOString(),
  });
}
