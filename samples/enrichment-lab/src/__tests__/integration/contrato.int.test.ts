import supertest from 'supertest';
import type { ConsultarCliente } from '../../application/consultar-cliente';
import { criarApp } from '../../interfaces/http/server';
import { servicosDeTeste } from '../helpers/servicos';

/**
 * O contrato vale nos dois sentidos. `validateResponses: true` com
 * `additionalProperties: false` em `Cliente` (service.yaml) faz uma resposta com campo
 * a mais virar 500 — o produtor não consegue vazar campo fora do contrato, nem por
 * engano. O caso de uso é substituído por um stub para forçar a resposta; o app é o
 * real (criarApp), sem mudança.
 */
const base = {
  documento: '12345678900',
  tipoPessoa: 'F' as const,
  versao: 3,
  data: { cadastro: { nome: 'Ana Exemplo' } },
};

function appCom(resposta: Record<string, unknown>) {
  const s = servicosDeTeste();
  const consultar = { executar: async () => resposta } as unknown as ConsultarCliente;
  return criarApp({ ...s, consultar });
}

describe('Contrato de resposta — GET /v1/clientes/{documento}', () => {
  it('should answer 200 when the use case returns exactly the contract shape', async () => {
    const r = await supertest(appCom(base)).get(`/v1/clientes/${base.documento}`);
    expect(r.status).toBe(200);
    expect(r.body.versao).toBe(3);
  });

  it('should answer 500 when the response carries a field outside the contract', async () => {
    const r = await supertest(appCom({ ...base, campoQueNaoExiste: 'vazou' })).get(
      `/v1/clientes/${base.documento}`,
    );
    expect(r.status).toBe(500);
    expect(JSON.stringify(r.body)).toMatch(/additional propert/i);
    expect(r.body).not.toHaveProperty('campoQueNaoExiste');
  });
});
