import fs from 'node:fs';
import path from 'node:path';
import Ajv2020 from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import yaml from 'js-yaml';
import { criarClienteAtualizadoV1 } from '../../../domain/cliente/events/cliente-atualizado.v1';

/**
 * O catálogo AsyncAPI e a fábrica do evento podem divergir em silêncio: a interface
 * TS não sabe o que o YAML promete aos consumidores. Este teste compila o payload do
 * canal e valida o que a fábrica produz — e o que ela NÃO deve produzir.
 */
type Catalogo = {
  components: { messages: { ClienteAtualizadoV1: { payload: object } } };
};

const catalogo = yaml.load(
  fs.readFileSync(path.resolve(__dirname, '../../../contracts/asyncapi.yaml'), 'utf8'),
) as Catalogo;
const ajv = new Ajv2020({ allErrors: true, strict: true });
addFormats(ajv);
const valida = ajv.compile(catalogo.components.messages.ClienteAtualizadoV1.payload);

describe('Contrato de evento — ClienteAtualizado v1 contra src/contracts/asyncapi.yaml', () => {
  const evento = criarClienteAtualizadoV1('12345678900', 3, new Date('2026-08-30T12:00:00Z'));

  it('should validate what the factory produces', () => {
    expect(valida(evento)).toBe(true);
  });

  it('should reject a payload with a field outside the catalog', () => {
    expect(valida({ ...evento, extra: 1 })).toBe(false);
    expect(JSON.stringify(valida.errors)).toMatch(/additional propert/i);
  });

  it('should reject version 2 on the v1 channel (a new version is a new event)', () => {
    expect(valida({ ...evento, version: 2 })).toBe(false);
  });
});
