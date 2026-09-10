<!-- gerado por tools/gerar-docs.cjs a partir de src/ (dependency-cruiser, .dependency-cruiser.cjs) — não edite à mão; rode `npm run generate` -->

# Grafo de dependências

## Módulos por camada

### application (2)

- `src/application/consultar-cliente.ts`
- `src/application/ingerir-evento.handler.ts`

### contracts (1)

- `src/contracts/evento-ingestao.schema.json`

### domain (14)

- `src/domain/cliente/cliente.entity.ts`
- `src/domain/cliente/cliente.repository.ts`
- `src/domain/cliente/documento.ts`
- `src/domain/cliente/events/cliente-atualizado.v1.ts`
- `src/domain/cliente/interfaces/evento-ingestao.ts`
- `src/domain/cliente/messaging/fila.port.ts`
- `src/domain/cliente/messaging/publicador.port.ts`
- `src/domain/cliente/service/apto.ts`
- `src/domain/cliente/service/guardas.ts`
- `src/domain/cliente/service/merge.ts`
- `src/domain/cliente/specifications/evento-elegivel-para-merge.ts`
- `src/domain/cliente/unidades.ts`
- `src/domain/errors/domain-error.ts`
- `src/domain/errors/domain-rule-violation.ts`

### infrastructure (8)

- `src/infrastructure/config/env.ts`
- `src/infrastructure/config/factories.ts`
- `src/infrastructure/contracts/validador-evento.ts`
- `src/infrastructure/memory/cliente.memoria.ts`
- `src/infrastructure/memory/fila.memory.ts`
- `src/infrastructure/memory/publicador.memoria.ts`
- `src/infrastructure/messaging/worker.ts`
- `src/infrastructure/telemetry/logger.ts`

### interfaces (3)

- `src/interfaces/http/controllers/clientes.controller.ts`
- `src/interfaces/http/controllers/eventos.controller.ts`
- `src/interfaces/http/server.ts`

### legacy (1)

- `legacy/calcula-apto.js`

### outros (7)

- `crypto`
- `node_modules/ajv-formats/dist/index.js`
- `node_modules/ajv/dist/2020.js`
- `node_modules/express-openapi-validator/dist/index.js`
- `node_modules/express/index.js`
- `path`
- `src/main.ts`

## Arestas entre camadas (34)

Uma linha por importação que cruza camada; a direção permitida é a dos ADRs (`.dependency-cruiser.cjs`).

- `src/application/consultar-cliente.ts → src/domain/cliente/cliente.repository.ts`
- `src/application/consultar-cliente.ts → src/domain/errors/domain-error.ts`
- `src/application/ingerir-evento.handler.ts → src/domain/cliente/interfaces/evento-ingestao.ts`
- `src/application/ingerir-evento.handler.ts → src/domain/cliente/messaging/fila.port.ts`
- `src/domain/cliente/service/apto.ts → legacy/calcula-apto.js`
- `src/infrastructure/config/factories.ts → src/application/consultar-cliente.ts`
- `src/infrastructure/config/factories.ts → src/application/ingerir-evento.handler.ts`
- `src/infrastructure/config/factories.ts → src/domain/cliente/interfaces/evento-ingestao.ts`
- `src/infrastructure/config/factories.ts → src/domain/cliente/service/guardas.ts`
- `src/infrastructure/contracts/validador-evento.ts → src/contracts/evento-ingestao.schema.json`
- `src/infrastructure/contracts/validador-evento.ts → src/domain/cliente/interfaces/evento-ingestao.ts`
- `src/infrastructure/contracts/validador-evento.ts → src/domain/errors/domain-error.ts`
- `src/infrastructure/memory/cliente.memoria.ts → src/domain/cliente/cliente.entity.ts`
- `src/infrastructure/memory/cliente.memoria.ts → src/domain/cliente/cliente.repository.ts`
- `src/infrastructure/memory/cliente.memoria.ts → src/domain/errors/domain-error.ts`
- `src/infrastructure/memory/fila.memory.ts → src/domain/cliente/messaging/fila.port.ts`
- `src/infrastructure/memory/publicador.memoria.ts → src/domain/cliente/events/cliente-atualizado.v1.ts`
- `src/infrastructure/memory/publicador.memoria.ts → src/domain/cliente/messaging/publicador.port.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/cliente/cliente.entity.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/cliente/cliente.repository.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/cliente/documento.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/cliente/interfaces/evento-ingestao.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/cliente/messaging/fila.port.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/cliente/messaging/publicador.port.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/cliente/service/guardas.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/errors/domain-error.ts`
- `src/infrastructure/messaging/worker.ts → src/domain/errors/domain-rule-violation.ts`
- `src/interfaces/http/controllers/clientes.controller.ts → src/application/consultar-cliente.ts`
- `src/interfaces/http/controllers/eventos.controller.ts → src/application/ingerir-evento.handler.ts`
- `src/interfaces/http/controllers/eventos.controller.ts → src/infrastructure/contracts/validador-evento.ts`
- `src/interfaces/http/server.ts → src/domain/errors/domain-error.ts`
- `src/interfaces/http/server.ts → src/infrastructure/config/factories.ts`
- `src/main.ts → src/infrastructure/config/factories.ts`
- `src/main.ts → src/interfaces/http/server.ts`
