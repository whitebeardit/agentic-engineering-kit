import supertest from 'supertest';
import { criarApp } from '../../interfaces/http/server';
import { CPF_VALIDO, eventoValido } from '../helpers/eventos';
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
