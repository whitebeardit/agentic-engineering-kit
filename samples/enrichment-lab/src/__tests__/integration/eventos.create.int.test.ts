import supertest from 'supertest';
import { criarApp } from '../../interfaces/http/server';
import { eventoValido } from '../helpers/eventos';
import { servicosDeTeste } from '../helpers/servicos';

const s = servicosDeTeste();
const app = criarApp(s);

describe('When we publish an ingestion event', () => {
  it('should answer 202 with a cid and enqueue it', async () => {
    const r = await supertest(app).post('/v1/eventos').send(eventoValido());
    expect(r.status).toBe(202);
    expect(r.body).toEqual({ message: 'aceito', cid: expect.any(String) });
    expect(s.fila.tamanho).toBe(1);
  });
  it('should answer 400 from the OpenAPI envelope on a bad field shape', async () => {
    const r = await supertest(app)
      .post('/v1/eventos')
      .send({ ...eventoValido(), tipoPessoa: 'X' });
    expect(r.status).toBe(400);
    expect(r.body.erro).toBe('contrato');
  });
  it('should answer 400 from the 2020-12 schema on a field outside it', async () => {
    const r = await supertest(app)
      .post('/v1/eventos')
      .send({ ...eventoValido(), campoNovo: 'que o front precisava' });
    expect(r.status).toBe(400);
    expect(r.body.erro).toBe('BadRequestError');
    expect(r.body.detalhes.join(' ')).toContain('additional properties');
  });
  it('should answer 400 when a CNPJ comes as pessoa fisica (schema)', async () => {
    const r = await supertest(app)
      .post('/v1/eventos')
      .send(eventoValido({ documento: '11444777000161' }));
    expect(r.status).toBe(400);
    expect(r.body.erro).toBe('BadRequestError');
  });
  it('should answer 404 for a route outside the contract', async () => {
    const r = await supertest(app).get('/v1/segredos');
    expect(r.status).toBe(404);
  });
  it('should keep /health outside the contract and alive', async () => {
    const r = await supertest(app).get('/health');
    expect(r.status).toBe(200);
  });
});
