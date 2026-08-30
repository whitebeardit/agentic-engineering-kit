# Perfil Node/TypeScript — linhas concretas para o AGENTS.md (do laboratório `samples/enrichment-lab`)

## Comandos
- Instalar: `npm install` (≈ 30 s, uma vez; Node 22 — `.nvmrc`)
- Gate: `npm run gate` = `tsc --noEmit && eslint . && jest --ci` (≈ 9 s; é o que o agente obedece)
- Tipos: `npm run typecheck` (≈ 2 s) · Lint: `npm run lint` (≈ 4 s; `legacy/` emite warnings da rampa, nunca erro)
- Testes: `npm test` (≈ 3 s) · Só a regra: `npm run test:regra` (`jest -t 'RN_<DOM>_'`) · Só arquitetura: `npm run test:arquitetura`
- Subir: `npm run dev`

## Gotchas
- **`jest` verde não é build verde**: ts-jest com `isolatedModules` não tipa. Gate = `tsc --noEmit` e `jest --ci`.
- Characterization: `npm test` roda com `--ci` — sem baseline falha e não grava; só humano aprova com `npm run baseline`; hook bloqueia `jest -u` e `__snapshots__/`.
- `legacy/` fora do type-check (só `legacy/*.d.ts`); lint dele é a rampa em `eslint.config.mjs` (`// Rampa`, dono e data por regra).

## Testes
| Camada | Tipo | Expectativa | Local | Comando |
|---|---|---|---|---|
| Domain (`src/domain`) | unit | 1:1 com cada cláusula EARS; nome `RN_<DOM>_<n>_…`; recusa carrega `ruleId` | `src/__tests__/unit/RN_*.unit.test.ts` | `npm run test:regra` |
| Application + HTTP | integration (supertest, app real, adaptadores em memória) | orquestra, não decide; contrato ativo | `src/__tests__/integration/*.int.test.ts` | `npm run test:int` |
| Arquitetura | dependency-cruiser em teste jest | todo ADR com `enforced-by` tem regra | `src/__tests__/unit/arquitetura.unit.test.ts` | `npm run test:arquitetura` |
| Legado (`legacy/`) | characterization (faker, semente fixa) | snapshot inalterado | `src/__tests__/unit/legacy/` | `npx jest --ci -t characterization` |

## Never
- Editar `__snapshots__/*.snap`, `.env` · `jest -u` · importar `src/infrastructure` de `src/domain`/`src/application` · lançar `DomainRuleViolation` fora de `src/domain`.
