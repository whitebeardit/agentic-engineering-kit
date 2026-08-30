# Perfil Node/TypeScript (`apply.sh --node-ts`)

Os cinco mecanismos do kit, na versão Node 22 / TypeScript — extraídos do laboratório `samples/enrichment-lab`.
`apply.sh --node-ts` copia estes arquivos para `docs/node-ts/` do repositório alvo (nunca sobrescreve): o time
adapta e move para a raiz.

| Mecanismo | Arquivo | Como o laboratório usa |
|---|---|---|
| Rampa de severidade | `eslint.config.example.mjs` (bloco `// Rampa`) + `tsconfig.base.json` (strict; `legacy/` fora do type-check, só `*.d.ts`) | severidade sobe por regra, com dono e data; nunca `eslint-disable` no arquivo |
| Arquitetura por ADR | `dependency-cruiser.example.cjs` + teste jest que lê a saída da CLI | cada regra cita o ADR e a correção; vermelho aparece no `npm test` |
| Teste nomeado pela regra | `jest.config.example.cjs` (`testRegex` por sufixo `.unit.test.ts` / `.int.test.ts`) | `jest -t 'RN_<DOM>_'` roda só os sensores da regra |
| Characterization do legado | snapshot jest com faker de semente fixa; `npm test` = `jest --ci` (falha sem baseline, não grava); `npm run baseline` só humano; hook bloqueia `.snap` e `jest -u` | ver `samples/enrichment-lab/src/__tests__/unit/legacy/` |
| Contrato em duas camadas | OpenAPI 3.0 com `validateResponses: true` + JSON Schema 2020-12 (Ajv) na borda + AsyncAPI para o que se publica | ver `samples/enrichment-lab/src/contracts/` |

Gate: `npm run gate` = `tsc --noEmit && eslint . && jest --ci`. **jest verde não é build verde** (ts-jest com
`isolatedModules` não tipa): os três comandos, sempre.
