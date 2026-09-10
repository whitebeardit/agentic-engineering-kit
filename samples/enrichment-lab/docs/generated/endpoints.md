<!-- gerado por tools/gerar-docs.cjs a partir de src/contracts/service.yaml (OpenAPI) — não edite à mão; rode `npm run generate` -->

# Inventário de endpoints — enrichment-lab 2.1.0

| Método | Path | operationId | Respostas |
|---|---|---|---|
| GET | `/v1/clientes/{documento}` | `consultarCliente` | 200, 304, 404, default |
| POST | `/v1/eventos` | `publicarEvento` | 202, 400, default |

Rota fora deste inventário responde 404 (validador de request); `/health` é registrado antes do validador e não faz parte do contrato.
