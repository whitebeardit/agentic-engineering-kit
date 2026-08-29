# <serviço> — <uma linha: o que é e de quem é>

Contexto canônico deste repositório, lido por qualquer agente (Claude Code, Cursor, Copilot) e pelo tlc-spec-driven.
Só fatos que o agente não adivinha: comandos, custos, gotchas, regras da casa. Menos de 150 linhas.

## Comandos
- Build: `dotnet build <Sol>.slnx` (≈ <N> s; warnings de análise são ERRO — o build é o que o agente obedece)
- Testes rápidos: `dotnet test --filter "Category!=Integration"` (≈ <N> s) — SEMPRE antes da suíte completa
- Suíte completa: `dotnet test` (≈ <N> min; Testcontainers sobe Postgres/Kafka) — só antes do PR
- Rodar local: `docker compose up -d && dotnet run --project src/<Proj>.Api` → http://localhost:<porta>/swagger
- Formatar: `dotnet format` (hook roda no arquivo tocado) · Contrato: `oasdiff breaking docs/openapi.yaml <novo>` sem ERR

## Definição de pronto
Build sem erro + testes verdes + contrato sem breaking + `.specs/features/<f>/validation.md` com PASS + output colado no PR.
Sem output, não está pronto.

## Gotchas (o que o agente não adivinha)
- <ex.: `IOrderRepository` tem duas implementações; a de `Legacy/` é a usada em produção>
- <ex.: testes de integração precisam de `DOTNET_ENVIRONMENT=Test`, senão batem no banco de dev>
- <ex.: `Migrations/` é gerado — mudança de schema passa por humano + PR separado>

## Onde estão as regras
- Regras de negócio deste domínio: `docs/regras/` (fonte de verdade; o card envelhece, isto não) — procedimento: skill `regras-de-negocio`
- Decisões: `docs/adr/` (com `enforced-by`) e `.specs/STATE.md` (AD-NNN, decisões leves) — conflito é sinalizado, não resolvido em silêncio
- Specs, tasks, validação e lições: `.specs/` (tlc-spec-driven)
- Contratos: `docs/openapi.yaml`, `docs/asyncapi.yaml` (mudar = versionar)

## Processo (tlc-spec-driven · © Tech Leads Club, CC-BY-4.0)
- Card entra por `card-intake` (Definition of Ready) → `specify feature` → gate humano 1 (spec) → design/tasks → gate humano 2 → execute → Verifier automático (autor ≠ verificador).
- Dimensionamento: cruza serviços ou toca legado = **Large** no mínimo; tier alto (auth, pagamento, dados pessoais, dependência nova) = **Complex**; contrato público muda = Design obrigatório.
- Multi-repo: a spec vive no repo dono do contrato; 1 task = 1 repo = 1 PR ≤ 400 linhas; ordem contrato → produtor → consumidor → legado atrás de feature flag.
- Legado: characterization test antes de tocar `**/Legacy/**`; `.verified.txt` só humano aprova.
- AD-NNN vira ADR quando ganha enforcement ou cruza serviços. Lição confirmada em `.specs/LESSONS.md` → ritual quinzenal → hook/analyzer/rule.

## Testes (o tlc lê isto para montar a Test Coverage Matrix)
| Camada | Tipo | Expectativa | Local | Comando |
|---|---|---|---|---|
| Domain | unit | 1:1 com cada cláusula EARS; nome `RN_<DOM>_<n>_…`; todos os edge cases | `tests/*/RN_*Tests.cs` | `dotnet test --filter "FullyQualifiedName~RN_"` |
| Application | integration (in-memory) | orquestra, não decide; happy + erro | `tests/*/*HandlerTests.cs` | `dotnet test` |
| Arquitetura | ArchUnitNET | todo ADR com `enforced-by` tem teste | `tests/*/ArchitectureTests.cs` | `dotnet test --filter ArchitectureTests` |
| Legado | characterization | baseline `.verified.txt` inalterado | `tests/*/Legacy/` | `dotnet test --filter Legacy` |
| Contrato público | oasdiff / AsyncAPI | sem breaking; consumidores listados | `docs/openapi.yaml` | `oasdiff breaking` |
| Config / migrations | none | build gate; migração por humano | — | `dotnet build` |

Gate Quick: `dotnet test --filter "Category!=Integration"` · Gate Full: `dotnet test` · Gate Build: `dotnet build && dotnet test`.

## Never
- Editar `.env`, `appsettings.*.json`, `Migrations/`, `docs/generated/`, `*.verified.txt` (hook bloqueia; peça a um humano).
- `git push --force`, `--no-verify`, `dotnet ef database update` fora de dev local, `git reset --hard`.
- Remover ou enfraquecer teste para passar. Instalar pacote sem verificar existência, idade e downloads.
- Referenciar Infrastructure de Domain/Application para "resolver" um erro de build.
