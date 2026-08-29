# orders-sample — serviço de Pedidos (exemplo do kit Whitebeard: Domain/Application/Infrastructure + um pedaço de legado)

Contexto canônico deste repositório, lido por qualquer agente (Claude Code, Cursor, Copilot) e pelo tlc-spec-driven.

## Comandos
- Build: `dotnet build Orders.slnx` (≈ 2 s; warnings de análise são ERRO — o build é o que o agente obedece)
- Testes: `dotnet test Orders.slnx` (≈ 9 s com build; 14 testes: 10 regra RN_ORD_012, 3 arquitetura, 1 characterization)
- Só a regra: `dotnet test --filter "FullyQualifiedName~RN_ORD_012"` · Só arquitetura: `dotnet test --filter ArchitectureTests`
- Formatar: `dotnet format Orders.slnx` (hook roda no arquivo tocado) · Usings: `dotnet format --diagnostics IDE0005`

## Definição de pronto
Build sem erro + `dotnet test` verde + `.verified.txt` inalterado (ou mudança explicada no PR) + `.specs/features/<f>/validation.md` com PASS + output colado no PR.

## Gotchas
- `Erp.Legacy` compila em `AnalysisMode=Minimum` (rampa); o resto em `Recommended` com warnings-as-errors.
- Characterization test: 1ª execução cria `*.received.txt` e FALHA; humano compara e renomeia para `.verified.txt`. Nunca aprove no automático.
- `DiffEngine_Disabled=true` no CI, senão o Verify tenta abrir um diff tool.
- **Nunca julgue um gate com `dotnet test --no-build`**: ele roda o binário anterior e "passa" com o build quebrado. Gate = `dotnet build` (exit 0) + `dotnet test` (exit 0), sempre com build fresco.
- `nuget.config` isola o feed: o NuGet.config global desta máquina aponta para feeds de outros clientes.
- Só existe repositório in-memory; não há API nem catálogo AsyncAPI (fora do exemplo).

## Onde estão as regras
- Regras de negócio: `docs/regras/pedidos.md` (IDs RN-ORD-*, com `Confiança:`) — procedimento: skill `regras-de-negocio`
- Decisões: `docs/adr/` (0003 domínio puro, 0004 regra no domínio) — impostas por `tests/Orders.Tests/ArchitectureTests.cs`; decisões leves em `.specs/STATE.md`
- Specs, tasks, validação e lições: `.specs/` (tlc-spec-driven)
- Contrato público: evento `OrderItemCancelled` (`src/Orders.Domain/Events/`) — mudar = versionar

## Processo (tlc-spec-driven · © Tech Leads Club, CC-BY-4.0)
- Card entra por `card-intake` (Definition of Ready) → `specify feature` → gate 1 → design/tasks → gate 2 → execute → Verifier automático (autor ≠ verificador).
- Dimensionamento: toca `src/Erp.Legacy/**` ou cruza serviços = **Large** no mínimo; tier alto = **Complex**; muda evento público = Design obrigatório.
- Multi-repo: este repo é dono do contrato `OrderItemCancelled`; o consumidor no ERP é outra feature/outro PR.
- Legado: characterization test antes de tocar `src/Erp.Legacy/**`; `.verified.txt` só humano aprova.

## Testes (o tlc lê isto para montar a Test Coverage Matrix)
| Camada | Tipo | Expectativa | Local | Comando |
|---|---|---|---|---|
| Domain (`Orders.Domain`) | unit | 1:1 com cada cláusula EARS; nome `RN_ORD_<n>_…`; idempotência e recusa cobertas | `tests/Orders.Tests/RN_*Tests.cs` | `dotnet test --filter "FullyQualifiedName~RN_"` |
| Application (handler) | integration in-memory | orquestra, não decide; usa `InMemoryOrderRepository` | `tests/Orders.Tests/RN_*Tests.cs` (teste do handler) | `dotnet test` |
| Arquitetura | ArchUnitNET | todo ADR com `enforced-by` tem teste; mensagem cita o ADR | `tests/Orders.Tests/ArchitectureTests.cs` | `dotnet test --filter ArchitectureTests` |
| Legado (`Erp.Legacy`) | characterization (Verify + Bogus, seed 20260827) | baseline `.verified.txt` inalterado | `tests/Orders.Tests/Legacy/` | `dotnet test --filter Legacy` |
| Infrastructure / config | none | build gate | — | `dotnet build` |

Gate Quick: `dotnet test --filter "FullyQualifiedName~RN_"` · Gate Full: `dotnet test Orders.slnx` · Gate Build: `dotnet build Orders.slnx && dotnet test Orders.slnx`.

## Never
- Editar `*.verified.txt`, `Migrations/`, `.env` (hook bloqueia).
- Referenciar `Orders.Infrastructure` de `Orders.Domain`/`Orders.Application` para "resolver" um erro de build.
- Lançar `DomainRuleViolationException` fora de `Orders.Domain` (ADR-0004; o teste de arquitetura falha).
- Remover ou enfraquecer teste para passar.
