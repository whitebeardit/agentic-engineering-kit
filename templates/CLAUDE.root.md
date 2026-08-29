# <Empresa> — workspace de engenharia

Este diretório contém todos os repositórios. Inicie o Claude **no subdiretório do serviço** que vai mudar; este
arquivo carrega junto. Regras por repositório ficam no `CLAUDE.md` de cada um.

## Serviços
| Serviço | Pasta | Tipo | Responsabilidade | Dono (pessoa) | Fala com |
|---|---|---|---|---|---|
| Orders | `./orders-svc` | micro .NET 8 | pedidos | <nome> | Billing (HTTP), Kafka `order.created` |
| ERP legado | `./erp-mono` | monolito .NET Fw 4.8 | cadastro, estoque | <nome> | SQL direto, WCF |

Mapa transversal (fluxos ponta a ponta, tabelas compartilhadas, ordem de release): vault → `engenharia/mapa-da-empresa.md`
(consultar via MCP; não copiar para cá). Grafo de dependências gerado: `docs/generated/deps.md` em cada repo.

## Ordem padrão entre serviços
contrato (API/evento/schema) → produtor → consumidor → legado por último, atrás de feature flag.
Exceção: legado é fonte de verdade do dado → vai primeiro, atrás de flag. Na dúvida, rode o agente `impact-analyzer`.

## Fluxo por card
`jira-intake` (DoR → requirements.md) → gate 1 → `impact-analyzer` → design.md → gate 2 → tasks.md (1 task = 1 repo = 1 PR)
→ execute (sessão nova por task, plan mode) → `verifier` (≠ autor) → PR draft com intenção + prova + risco → humano por tier.

## Etiqueta
- Branch `feat/<card>-<slug>` a partir de `main`; commits atômicos, mensagem no imperativo; PR sempre draft; ≤ 400 linhas.
- Conventional commits; PR cita o card e a spec (`specs/NNN-…`).
- "Pronto" = comando com exit 0 colado no PR. Sem output, não está pronto.

## Never
- Editar `.env`, `appsettings.*.json`, `Migrations/`, `docs/generated/` (hook bloqueia; peça a um humano).
- `git push --force`, `--no-verify`, `dotnet ef database update` fora de dev local.
- Remover ou enfraquecer teste para passar. Apagar `.verified.txt` de characterization test.
- Instalar pacote sem verificar existência, idade e downloads.
