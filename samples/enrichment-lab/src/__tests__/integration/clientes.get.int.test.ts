import { randomUUID } from 'node:crypto';
import supertest from 'supertest';
import { criarApp } from '../../interfaces/http/server';
import { CNPJ_VALIDO, CPF_VALIDO, eventoValido } from '../helpers/eventos';
import { servicosDeTeste } from '../helpers/servicos';

const s = servicosDeTeste();
const app = criarApp(s);

describe('When we read a consolidated customer', () => {
  it('should answer 404 before any event was processed', async () => {
    const r = await supertest(app).get(`/v1/clientes/${CPF_VALIDO}`);
    expect(r.status).toBe(404);
  });
  it('should answer 200 with ETag = version after the worker ran', async () => {
    await supertest(app).post('/v1/eventos').send(eventoValido()).expect(202);
    await expect(s.worker.processarPendentes()).resolves.toEqual(['gravado']);
    const r = await supertest(app).get(`/v1/clientes/${CPF_VALIDO}`);
    expect(r.status).toBe(200);
    expect(r.headers.etag).toBe('"v1"');
    expect(r.body.data.cadastro.nome).toBe('Ana Exemplo');
  });
  it('should publish one ClienteAtualizado v1 per real change and none when nothing changes', async () => {
    expect(s.publicador.publicados).toHaveLength(1); // o evento do teste anterior
    const empresa = { documento: CNPJ_VALIDO, tipoPessoa: 'J' as const };
    const parcial = eventoValido({
      ...empresa,
      updatedAt: '2026-08-30T12:00:00Z',
      data: { cadastro: { nome: 'Empresa Exemplo', canalEntrada: 'parceiro' } },
    });
    const maisAntigoComCep = eventoValido({
      ...empresa,
      updatedAt: '2026-08-30T11:00:00Z',
      data: {
        cadastro: { nome: 'EMPRESA EXEMPLO LTDA' },
        endereco: { cep: '20040020' },
      },
    });
    await supertest(app).post('/v1/eventos').send(parcial).expect(202);
    await supertest(app).post('/v1/eventos').send(maisAntigoComCep).expect(202);
    await expect(s.worker.processarPendentes()).resolves.toEqual([
      'gravado',
      'gravado',
    ]);
    const r = await supertest(app).get(`/v1/clientes/${CNPJ_VALIDO}`);
    expect(r.headers.etag).toBe('"v2"');
    expect(r.body.data.cadastro.nome).toBe('Empresa Exemplo'); // mais antigo não sobrescreve
    expect(r.body.data.endereco.cep).toBe('20040020'); // lacuna preenchida
    expect(s.publicador.publicados.map((e) => [e.documento, e.versao])).toEqual([
      [CPF_VALIDO, 1],
      [CNPJ_VALIDO, 1],
      [CNPJ_VALIDO, 2],
    ]);
    const mesmoEstado = { ...parcial, eventId: randomUUID() }; // eventId novo: passa a dedup
    await supertest(app).post('/v1/eventos').send(mesmoEstado).expect(202);
    await expect(s.worker.processarPendentes()).resolves.toEqual(['sem-mudanca']);
    expect(s.publicador.publicados).toHaveLength(3);
  });
  it('should answer 304 when If-None-Match carries the current version', async () => {
    const r = await supertest(app)
      .get(`/v1/clientes/${CPF_VALIDO}`)
      .set('If-None-Match', '"v1"');
    expect(r.status).toBe(304);
  });
  it('should log the ruleId when an event is discarded by a rule', async () => {
    const invalido = eventoValido({ documento: '12345678900' });
    await supertest(app).post('/v1/eventos').send(invalido).expect(202);
    await expect(s.worker.processarPendentes()).resolves.toEqual(['descartado']);
    const linha = s.linhasDeLog
      .map((l) => JSON.parse(l) as Record<string, unknown>)
      .find((l) => l.ruleId);
    expect(linha).toMatchObject({
      ruleId: 'RN-ENR-001',
      motivo: 'descartado-documento',
      documento: '*******8900',
    });
  });
});
