# <Empresa> — workspace de engenharia

Este diretório contém todos os repositórios. Inicie o agente **no subdiretório do serviço** que vai mudar; este arquivo
carrega junto. Para o agente ler os serviços irmãos, inicie a sessão com `--add-dir` para cada um. Regras por
repositório ficam no `AGENTS.md` de cada um.

## Serviços
| Serviço | Pasta | Tipo | Responsabilidade | Dono (pessoa) | Fala com |
|---|---|---|---|---|---|
| Orders | `./orders-svc` | micro .NET 8 | pedidos | <nome> | Billing (HTTP), Kafka `order.created` |
| ERP legado | `./erp-mono` | monolito .NET Fw 4.8 | cadastro, estoque | <nome> | SQL direto, WCF |

Mapa transversal (fluxos ponta a ponta, tabelas compartilhadas, ordem de release): vault → `engenharia/mapa-da-empresa.md`
(não copiar para cá; os agentes do kit não leem o vault — quem roda o `impact-analyzer` cola no pedido o trecho do mapa). Grafo de dependências gerado: `docs/generated/deps.md` em cada repo (o agente lê; não edita).

## Ordem padrão entre serviços
Para acrescentar (o consumidor antigo tolera o campo novo): contrato (API/evento/schema) → produtor → consumidor → legado por último, atrás de feature flag com dono e data para sair.
Para retirar, ou quando o consumidor novo precisa ler dado antigo: inverte — consumidores primeiro. Regra por trás das duas: sobe primeiro quem pode mudar sem quebrar quem ainda não mudou.
Exceção: o dado nasce no legado (legado é fonte de verdade) → o legado vai primeiro, atrás de flag; tirar a verdade do legado é outra mudança (expandir → migrar → contrair). Na dúvida, rode o agente `impact-analyzer`.

## Fluxo por card (tlc-spec-driven · © Tech Leads Club, CC-BY-4.0)
`card-intake` (DoR) → `specify feature` → gate 1 (PO) → `impact-analyzer` → design → gate 2 (tech lead) → tasks (1 task = 1 repo = 1 PR)
→ execute (sessão nova por task) → Verifier do tlc (≠ autor) → PR draft com intenção + `validation.md` + risco → humano por tier → UAT com PO → nota no vault.

## Etiqueta
- Branch `feat/<card>-<slug>` a partir de `main`; commits atômicos (um por task); PR sempre draft; ≤ 400 linhas.
- Conventional commits; PR cita o card e a spec (`.specs/features/<f>/`).
- "Pronto" = comando com exit 0 e `validation.md` com PASS colados no PR. Isso libera o próximo repositório a **começar**;
  **implantar** segue a ordem acima e depende do check verde daquele commit, não do texto colado.

## Never
- Editar `.env`, `appsettings.*.json`, `Migrations/`, `docs/generated/`, `*.verified.txt` (hook bloqueia).
- `git push --force`, `--no-verify`, `dotnet ef database update` fora de dev local.
- Remover ou enfraquecer teste para passar. Instalar pacote sem verificar existência, idade e downloads.
