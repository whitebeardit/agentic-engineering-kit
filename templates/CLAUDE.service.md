# <serviço> — <uma linha: o que é e de quem é>

## Comandos
- Build: `dotnet build src/<Proj>.sln -c Debug` (≈ <N> s)
- Testes rápidos: `dotnet test --filter "Category!=Integration"` (≈ <N> s) — use SEMPRE antes da suíte completa
- Suíte completa: `dotnet test` (≈ <N> min; Testcontainers sobe Postgres/Kafka) — rode só antes do PR
- Rodar local: `docker compose up -d && dotnet run --project src/<Proj>.Api` → http://localhost:<porta>/swagger
- Formatar: `dotnet format` (hook roda no arquivo tocado)
- Contrato: `oasdiff breaking docs/openapi.yaml <novo>` deve retornar sem ERR

## Definição de pronto
Build sem warnings novos + testes rápidos verdes + contrato sem breaking + evidência colada no PR. Sem output, não está pronto.

## Gotchas (o que o agente não adivinha)
- <ex.: `IOrderRepository` tem duas implementações; a de `Legacy/` é a usada em produção>
- <ex.: testes de integração precisam de `DOTNET_ENVIRONMENT=Test`, senão batem no banco de dev>
- <ex.: `Migrations/` é gerado — mudança de schema passa por humano + PR separado>

## Onde estão as regras
- Regras de negócio deste domínio: `docs/regras/` (fonte de verdade; o card do Jira envelhece, isto não)
- Decisões: `docs/adr/` — conflito com ADR é sinalizado, não resolvido em silêncio
- Specs: `specs/NNN-…/` · Contratos: `docs/openapi.yaml`, `docs/asyncapi.yaml`

## Never (além do workspace)
- <ex.: tocar em `Payments.*` — outro time, outro repo>
