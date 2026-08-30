import Ajv2020 from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import schema from '../../contracts/evento-ingestao.schema.json';
import { BadRequestError } from '../../domain/errors/domain-error';
import type { EventoIngestao } from '../../domain/cliente/interfaces/evento-ingestao';

/**
 * Validação autoritativa do evento na borda (JSON Schema 2020-12). O validador OpenAPI
 * não expressa este
 * schema (OpenAPI 3.0 usa um dialeto próprio), por isso o Ajv roda antes de enfileirar.
 */
const ajv = new Ajv2020({ allErrors: true, strict: true });
addFormats(ajv);
const validar = ajv.compile<EventoIngestao>(schema);

export function validarEvento(payload: unknown): EventoIngestao {
  if (validar(payload)) return payload;
  const detalhes = (validar.errors ?? []).map((e) =>
    `${e.instancePath || '/'} ${e.message ?? ''}`.trim(),
  );
  throw new BadRequestError('evento fora do schema 2.1', detalhes);
}
