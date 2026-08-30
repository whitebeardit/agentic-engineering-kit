# <serviço> — <uma linha: o que é e de quem é>

Contexto canônico deste repositório, lido por qualquer agente (Claude Code, Cursor, Copilot) e pelo tlc-spec-driven.
Só fatos que o agente não adivinha: comandos, custos, gotchas, regras da casa. Menos de 150 linhas.
Os comandos concretos de cada stack estão em `templates/profiles/` do kit (`node-ts.md`, `dotnet.md`) — cole o seu aqui.

## Comandos
- Build/tipos: `<build>` (≈ <N> s; warnings tratados como ERRO — o build é o que o agente obedece)
- Testes rápidos: `<teste rápido>` (≈ <N> s) — SEMPRE antes da suíte completa
- Suíte completa: `<suíte>` (≈ <N> min; sobe dependências?) — só antes do PR
- Rodar local: `<subir>` → http://localhost:<porta>/...
- Formatar: `<formatador>` (hook roda no arquivo tocado) · Contrato: `oasdiff breaking docs/openapi.yaml <novo>` sem ERR

## Definição de pronto
Build sem erro + testes verdes + contrato sem breaking + `.specs/features/<f>/validation.md` com PASS + output colado no PR.
Sem output, não está pronto.

## Gotchas (o que o agente não adivinha)
- <ex.: o runner de testes não tipa; "testes verdes" ≠ "build verde" — gate = build + testes>
- <ex.: `IOrderRepository` tem duas implementações; a de `legacy/` é a usada em produção>
- <ex.: testes de integração precisam de `<ENV>=Test`, senão batem no banco de dev>
- <ex.: `migrations/` é gerado — mudança de schema passa por humano + PR separado>

## Onde estão as regras
- Regras de negócio deste domínio: `docs/regras/` (fonte de verdade; o card envelhece, isto não) — procedimento: skill `regras-de-negocio`
- Decisões: `docs/adr/` (com `enforced-by`) e `.specs/STATE.md` (AD-NNN, decisões leves) — conflito é sinalizado, não resolvido em silêncio
- Specs, tasks, validação e lições: `.specs/` (tlc-spec-driven)
- Contratos: `docs/openapi.yaml` ou `src/contracts/`, `asyncapi.yaml` (mudar = versionar)
- Produção: `docs/debug-prod.md` (coordenadas, primeiro movimento por sintoma, trace sob demanda) — lido pelo agente `trace-finder`

## Processo (tlc-spec-driven · © Tech Leads Club, CC-BY-4.0)
- Card entra por `card-intake` (Definition of Ready) → `specify feature` → gate humano 1 (spec) → design/tasks → gate humano 2 → execute → Verifier automático (autor ≠ verificador).
- Dimensionamento: cruza serviços ou toca legado = **Large** no mínimo; tier alto (auth, pagamento, dados pessoais, dependência nova) = **Complex**; contrato público muda = Design obrigatório.
- Multi-repo: a spec vive no repo dono do contrato; 1 task = 1 repo = 1 PR ≤ 400 linhas; ordem contrato → produtor → consumidor → legado atrás de feature flag.
- Legado: characterization test antes de tocar `**/legacy/**` ou `**/Legacy/**`; baseline (`.verified.txt` / `__snapshots__/*.snap`) só humano aprova.
- AD-NNN vira ADR quando ganha enforcement ou cruza serviços. Lição confirmada em `.specs/LESSONS.md` → ritual quinzenal → hook/analyzer/rule.

## Testes (o tlc lê isto para montar a Test Coverage Matrix)
| Camada | Tipo | Expectativa | Local | Comando |
|---|---|---|---|---|
| Domain | unit | 1:1 com cada cláusula EARS; nome `RN_<DOM>_<n>_…`; todos os edge cases | `<pasta de testes de regra>` | `<teste filtrado pela regra>` |
| Application | integration (in-memory) | orquestra, não decide; happy + erro | `<pasta de integração>` | `<suíte>` |
| Arquitetura | teste de dependências (ArchUnitNET · dependency-cruiser) | todo ADR com `enforced-by` tem teste | `<arquivo de arquitetura>` | `<filtro>` |
| Legado | characterization (Verify+Bogus · jest+faker, semente fixa) | baseline inalterado | `<pasta legacy>` | `<filtro>` |
| Contrato público | oasdiff / AsyncAPI | sem breaking; consumidores listados | `docs/openapi.yaml` | `oasdiff breaking` |
| Config / migrations | none | build gate; migração por humano | — | `<build>` |

Gate Quick: `<teste rápido>` · Gate Full: `<suíte>` · Gate Build: `<build> && <suíte>`.

## Never
- Editar `.env`, `appsettings.*.json`, `migrations/`, `docs/generated/`, `*.verified.txt`, `__snapshots__/*.snap` (hook bloqueia; peça a um humano).
- `git push --force`, `--no-verify`, migração aplicada pelo agente fora de dev local, `git reset --hard`, `jest -u`.
- Remover ou enfraquecer teste para passar. Instalar pacote sem verificar existência, idade e downloads.
- Referenciar Infrastructure de Domain/Application para "resolver" um erro de build.
