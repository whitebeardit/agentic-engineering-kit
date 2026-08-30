# enrichment-lab — serviço de enriquecimento de cadastro em miniatura (laboratório do kit Whitebeard: domain/application/infrastructure + um pedaço de legado)

Contexto canônico deste repositório, lido por qualquer agente (Claude Code, Cursor, Copilot) e pelo tlc-spec-driven. Sintético: espelha a arquitetura de um serviço real, sem nuvem — banco e fila são adaptadores em memória.

## Comandos

- Instalar: `npm install` (≈ 30 s, uma vez; Node 22 — `.nvmrc`)
- Gate: `npm run gate` = `tsc --noEmit && eslint . && jest --ci` (≈ 9 s; é o que o agente obedece)
- Tipos: `npm run typecheck` (≈ 2 s) · Lint: `npm run lint` (≈ 4 s; `legacy/` emite warnings da rampa, nunca erro — ver Gotchas)
- Testes: `npm test` (≈ 3 s; 44 testes: 29 regra RN_ENR_*, 3 arquitetura, 1 characterization, 11 integração)
- Ordem dos arquivos invertida (caça dependência de ordem): `npm run test:reverso`
- Só a regra: `npm run test:regra` (`jest -t 'RN_ENR_'`) · Só arquitetura: `npm run test:arquitetura` · Unit/int: `npm run test:unit` / `npm run test:int`
- Subir: `npm run dev` (build + `http://localhost:3000`: `POST /v1/eventos`, `GET /v1/clientes/{documento}`, `/health`)

## Definição de pronto

`npm run gate` exit 0 + snapshot de characterization inalterado (ou mudança explicada no PR) + `.specs/features/<f>/validation.md` com PASS + saída do gate colada no PR.

## Gotchas

- **`jest` verde não é build verde**: o ts-jest roda com `isolatedModules` e não tipa nada. Gate = `tsc --noEmit` (exit 0) **e** `jest --ci` (exit 0). Nunca julgue um gate só pelo jest.
- Characterization test (`src/__tests__/unit/legacy/`): `npm test` roda com `--ci` — sem baseline ele **falha e não grava**. Só um humano aprova o baseline com `npm run baseline`, no terminal; o hook bloqueia `jest -u` e edições em `__snapshots__/`.
- `legacy/` não é type-checked (só `legacy/*.d.ts` entra no `tsc`); o lint dele é a rampa em `eslint.config.mjs` (`// Rampa`): severidade sobe por regra, com dono e data, nunca com `eslint-disable` no arquivo.
- Contrato em duas camadas: `src/contracts/service.yaml` valida request **e** response (rota fora dele = 404; `/health` é registrado antes); o payload de `POST /v1/eventos` é validado pelo `evento-ingestao.schema.json` (Ajv 2020-12) antes de enfileirar — o validador OpenAPI não expressa esse schema.
- A fila em memória reentrega na hora (sem visibility timeout): uma mensagem envenenada vai para a DLQ em cinco recebimentos numa passada só.
- Ordem das guardas é fixa (`docs/regras/enriquecimento.md`): idempotência → dígitos → blacklist → apto pelo legado (RN-ENR-006) → limiar e merge (RN-ENR-004) → gravação condicional (RN-ENR-005).

## Onde estão as regras

- Regras de negócio: `docs/regras/enriquecimento.md` (IDs RN-ENR-*, com `Confiança:`) — procedimento: skill `regras-de-negocio`
- Decisões: `docs/adr/` (0003 domínio puro, 0004 regra no domínio) — impostas por `src/__tests__/unit/arquitetura.unit.test.ts` via `.dependency-cruiser.cjs`; decisões leves em `.specs/STATE.md`
- Specs, tasks, validação e lições: `.specs/` (tlc-spec-driven)
- Contratos públicos: `src/contracts/service.yaml` (HTTP), `src/contracts/asyncapi.yaml` (eventos publicados), `src/contracts/evento-ingestao.schema.json` (evento recebido) — mudar = versionar (`rules/contracts.md`)

## Processo (tlc-spec-driven · © Tech Leads Club, CC-BY-4.0)

- Card entra por `card-intake` (Definition of Ready) → `specify feature` → gate 1 → design/tasks → gate 2 → execute → Verifier automático (autor ≠ verificador).
- Dimensionamento: toca `legacy/**` ou cruza serviços = **Large** no mínimo; tier alto (dados pessoais) = **Complex**; muda contrato público = Design obrigatório.
- Multi-repo: este repo é dono dos contratos `POST /v1/eventos` e `ClienteAtualizado`; consumidores são outra feature/outro PR.
- Legado: characterization test antes de tocar `legacy/**`; baseline só humano aprova.

## Testes (o tlc lê isto para montar a Test Coverage Matrix)

| Camada                  | Tipo                                                | Expectativa                                                              | Local                                         | Comando                             |
| ----------------------- | --------------------------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------- | ----------------------------------- |
| Domain (`src/domain`)   | unit                                                | 1:1 com cada cláusula EARS; nome `RN_ENR_<n>_…`; recusa carrega `ruleId` | `src/__tests__/unit/RN_ENR_*.unit.test.ts`    | `npm run test:regra`                |
| Application + HTTP      | integration (supertest, app real, store em memória) | orquestra, não decide; contrato ativo (400/404/304)                      | `src/__tests__/integration/*.int.test.ts`     | `npm run test:int`                  |
| Arquitetura             | dependency-cruiser em teste jest                    | todo ADR com `enforced-by` tem regra; mensagem cita o ADR                | `src/__tests__/unit/arquitetura.unit.test.ts` | `npm run test:arquitetura`          |
| Legado (`legacy/`)      | characterization (faker, seed 20260827, 60 casos)   | snapshot inalterado                                                      | `src/__tests__/unit/legacy/`                  | `npx jest --ci -t characterization` |
| Infrastructure / config | none                                                | gate de tipos e lint                                                     | —                                             | `npm run typecheck && npm run lint` |

Gate Quick: `npm run test:regra` · Gate Full: `npm test` · Gate Build: `npm run gate`.

## Never

- Editar `__snapshots__/*.snap`, `.env` (hook bloqueia) · rodar `jest -u` (hook bloqueia).
- Importar `src/infrastructure` de `src/domain`/`src/application` para "resolver" um erro (ADR-0003; o teste de arquitetura falha).
- Lançar `DomainRuleViolation` fora de `src/domain` (ADR-0004; o teste de arquitetura falha).
- Remover ou enfraquecer teste para passar · `git push --force` · `--no-verify`.
