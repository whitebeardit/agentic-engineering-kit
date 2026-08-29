---
name: run-and-test
description: Como subir e testar cada serviço deste workspace — comandos exatos, custos e o que "verde" significa. Use antes de rodar qualquer build, teste ou serviço local; evita a suíte completa por engano.
---
# run-and-test

Preencha por serviço ao aplicar o kit. Sem isto, o agente roda a suíte de 20 min para checar um typo.

| Serviço | Subir local | Testes rápidos (≈ s) | Suíte completa (≈ min) | Verde significa |
|---|---|---|---|---|
| `<orders-svc>` | `docker compose up -d && dotnet run --project src/Orders.Api` | `dotnet test --filter "Category!=Integration"` (≈ 40 s) | `dotnet test` (≈ 12 min, Testcontainers) | 0 falhas + `oasdiff` sem ERR |
| `<erp-mono>` | `<como subir o legado>` | `<projeto de testes>` | `<…>` | characterization `.verified.txt` inalterado |

## Regras
- Rode **sempre** os rápidos primeiro; suíte completa só antes do PR.
- Cole o output no PR (últimas linhas com contagem). "Passou" sem output não conta.
- Teste vermelho que você não entende → pare e pergunte; não altere o teste.
- Integração precisa de `DOTNET_ENVIRONMENT=Test`; sem isso bate em dev.
