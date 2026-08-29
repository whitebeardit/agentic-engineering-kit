# orders-sample — serviço de Pedidos (exemplo do kit Whitebeard; Domain/Application/Infrastructure + um pedaço de legado)

## Comandos
- Build: `dotnet build Orders.slnx` (≈ 2 s; warnings de análise são ERRO — o build é o que o agente obedece)
- Testes: `dotnet test Orders.slnx` (≈ 9 s; 9 testes: 5 regra, 3 arquitetura, 1 characterization)
- Só a regra: `dotnet test --filter "FullyQualifiedName~RN_ORD_012"`
- Formatar: `dotnet format Orders.slnx` (hook roda no arquivo tocado)

## Definição de pronto
Build sem erro + `dotnet test` verde + `.verified.txt` inalterado (ou mudança explicada no PR) + output colado no PR.

## Gotchas
- `Erp.Legacy` compila em `AnalysisMode=Minimum` (rampa); o resto em `Recommended` com warnings-as-errors.
- Characterization test: 1ª execução cria `*.received.txt` e FALHA; humano compara e renomeia para `.verified.txt`. Nunca aprove no automático.
- `DiffEngine_Disabled=true` no CI, senão o Verify tenta abrir um diff tool.

## Onde estão as regras
- Regras de negócio: `docs/regras/pedidos.md` (IDs RN-ORD-*) — procedimento: skill `regras-de-negocio`
- Decisões: `docs/adr/` (0003 domínio puro, 0004 regra no domínio) — impostas por `tests/Orders.Tests/ArchitectureTests.cs`
- Specs: `specs/001-cancelamento-parcial/`

## Never
- Editar `*.verified.txt`, `Migrations/`, `.env` (hook bloqueia).
- Referenciar `Orders.Infrastructure` de `Orders.Domain`/`Orders.Application` para "resolver" um erro de build.
