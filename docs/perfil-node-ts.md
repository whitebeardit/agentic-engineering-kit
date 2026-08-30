# Perfil Node/TypeScript — os cinco mecanismos do kit em duas stacks

O kit impõe as mesmas cinco garantias em qualquer stack; muda só a ferramenta. Laboratórios: `samples/enrichment-lab`
(Node 22 / TypeScript — o do livro *Cercando a IA*) e `samples/orders-sample` (.NET — o do e-book *Engenharia com
Agentes em .NET*).

| Mecanismo | Node/TypeScript (`enrichment-lab`) | .NET (`orders-sample`) |
|---|---|---|
| Regra com ID em quatro lugares | `docs/regras/<dom>.md` · entidade/specification em `src/domain` · `it('RN_<DOM>_<n>_…')` · `DomainRuleViolation(ruleId, motivo)` | `docs/regras/<dom>.md` · agregado/`ISpecification` · `[Fact] RN_<DOM>_<n>_…` · `DomainRuleViolationException.RuleId` |
| Arquitetura por ADR | `.dependency-cruiser.cjs` (regra = ADR, `comment` = correção) lida por um teste jest | ArchUnitNET em `ArchitectureTests.cs` (`.Because(ADR…)`) |
| Contrato como código | OpenAPI 3.0 `validateResponses: true` + JSON Schema 2020-12 (Ajv) na borda + AsyncAPI para o que se publica; evento versionado no nome do arquivo (`*.v1.ts`) | `record` imutável em `Events/` (versão na doc); `rules/contracts.md` |
| Characterization do legado | jest snapshot + `@faker-js/faker` semente fixa; `jest --ci` falha sem baseline e não grava; `npm run baseline` só humano; hook bloqueia `.snap` e `jest -u` | Verify + Bogus semente fixa; 1ª execução gera `.received.txt` e falha; humano renomeia para `.verified.txt`; hook bloqueia `.verified.txt` |
| Rampa de severidade | `tsconfig` strict + `eslint.config.mjs` com override `legacy/**` (por regra, `warn` → `error`, dono e data) | `Directory.Build.props` (`AnalysisMode` Minimum → Recommended) + `.editorconfig` por regra com dono e data |
| Gate | `npm run gate` = `tsc --noEmit && eslint . && jest --ci` — jest não tipa | `dotnet build && dotnet test` — nunca `--no-build` (L-001) |
| Formatação no hook | `hooks/format.sh` → prettier + `eslint --fix` no arquivo tocado | `hooks/format.sh` → `dotnet format` no projeto do arquivo |

Aplicar: `apply.sh <repo> --claude --cursor --node-ts` (exemplos em `docs/node-ts/`) ou `--dotnet`.
