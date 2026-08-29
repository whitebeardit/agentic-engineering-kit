# Cancelamento parcial de pedido (ORD-231) Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for how a task is executed, gated, and committed.

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: `.specs/features/001-cancelamento-parcial/design.md`
**Status**: In Progress

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: `AGENTS.md` (seção "Testes", tabela por camada + gates), `docs/adr/0003-dominio-puro.md`, `docs/adr/0004-regra-no-dominio.md`, `Directory.Build.props` (warnings-as-errors), `.editorconfig` (CA1707 desligado em tests/**). Amostra de testes existentes: `tests/Orders.Tests/ArchitectureTests.cs` (ArchUnitNET), `tests/Orders.Tests/Legacy/CalculadoraFreteCharacterizationTests.cs` (Verify + Bogus).

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Domain (`Orders.Domain`: agregado, specification, evento) | unit | 1:1 com cada cláusula EARS (CANC-01..06); nome `RN_ORD_012_…`; edge cases listados na spec têm teste próprio | `tests/Orders.Tests/RN_*Tests.cs` | `dotnet test Orders.slnx --filter "FullyQualifiedName~RN_"` |
| Application (`CancelOrderItemHandler`) | integration (in-memory) | orquestra, não decide (CANC-07): carrega, delega, persiste, devolve total + eventos | `tests/Orders.Tests/RN_*Tests.cs` (teste do handler) | `dotnet test Orders.slnx` |
| Arquitetura (ADR-0003/0004) | ArchUnitNET | regra de camada continua imposta; Application não lança `DomainRuleViolationException` | `tests/Orders.Tests/ArchitectureTests.cs` | `dotnet test Orders.slnx --filter ArchitectureTests` |
| Docs (`docs/regras/pedidos.md`) | none | build gate only | - | `dotnet build Orders.slnx` |

## Gate Check Commands

> Generated from codebase - confirm before Execute.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After tasks with unit tests only | `dotnet test Orders.slnx --filter "FullyQualifiedName~RN_"` |
| Full | After tasks with e2e/integration tests | `dotnet test Orders.slnx` |
| Build | After phase completion or config/entity-only tasks | `dotnet build Orders.slnx && dotnet test Orders.slnx` |

---

## Execution Plan

Phases are ordered and run sequentially - each phase completes before the next begins, and tasks within a phase execute in order.

### Phase 1: Domínio

Regra escrita primeiro (skill `regras-de-negocio`), depois contrato, elegibilidade e o comportamento do agregado.

```
T1 → T2 → T3 → T4
```

### Phase 2: Aplicação e fechamento

Orquestração sem regra; regra marcada como verificada. (T5 depende de T4, último da fase 1.)

```
T4 → T5 → T6
```

---

## Task Breakdown

### T1: Registrar RN-ORD-012 em docs/regras/pedidos.md

**What**: Bloco `RN-ORD-012 — Cancelamento parcial` em EARS, com Código/Teste previstos e `Confiança: inferred`, antes de codar (skill `regras-de-negocio`, passo 1).
**Where**: `docs/regras/pedidos.md`
**Depends on**: None
**Reuses**: formato dos blocos RN-ORD-001..004 e modelo da skill `regras-de-negocio`
**Requirement**: CANC-01, CANC-02, CANC-03, CANC-04, CANC-05, CANC-06
**Tools**:
- MCP: NONE
- Skill: `regras-de-negocio`
**Done when**:
- [x] Bloco com as cláusulas WHEN/IF/SHALL CONTINUE TO da spec, `Código:` e `Teste:` apontando para os arquivos que T2–T5 criarão, `Confiança: inferred`
- [x] Build gate passes: `dotnet build Orders.slnx && dotnet test Orders.slnx` — 4 passed, 0 failed (2026-08-29)
**Tests**: none
**Gate**: build
**Status**: ✅ Done

---

### T2: Evento OrderItemCancelled

**What**: Record imutável `OrderItemCancelled(OrderId, ItemId, Money NewTotal)` implementando `IDomainEvent` com `OccurredAt` — contrato público novo (versão 1).
**Where**: `src/Orders.Domain/Events/OrderItemCancelled.cs`
**Depends on**: T1
**Reuses**: `src/Orders.Domain/Events/IDomainEvent.cs`, `src/Orders.Domain/Money.cs`
**Requirement**: CANC-02
**Tools**:
- MCP: NONE
- Skill: NONE
**Done when**:
- [x] Record com os quatro campos; comentário XML dizendo que é contrato público (mudar = versionar)
- [x] Build gate passes: `dotnet build Orders.slnx && dotnet test Orders.slnx` — 4 passed (2026-08-29)
**Tests**: none
**Gate**: build
**Status**: ✅ Done

---

### T3: Specification PedidoElegivelParaCancelamento

**What**: `PedidoElegivelParaCancelamento : ISpecification<Order>` — verdadeiro só quando `Status == Aberto`; testes RN_ORD_012 para elegibilidade (Aberto → elegível; Faturado e Cancelado → não).
**Where**: `src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs`, `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs`
**Depends on**: T2
**Reuses**: `src/Orders.Domain/Specifications/ISpecification.cs`, `OrderStatus`
**Requirement**: CANC-06
**Tools**:
- MCP: NONE
- Skill: NONE
**Done when**:
- [ ] `IsSatisfiedBy(pedido Aberto) == true`; `IsSatisfiedBy(Faturado) == false`; `IsSatisfiedBy(Cancelado) == false` — cada um com teste nomeado `RN_ORD_012_…`
- [ ] Gate check passes: `dotnet test Orders.slnx --filter "FullyQualifiedName~RN_"`
- [ ] Test count: 3 testes RN_ORD_012 (total da suíte 7)
**Tests**: unit
**Gate**: quick

---

### T4: Order.CancelItem (RN-ORD-012)

**What**: Método `CancelItem(Guid itemId)` no agregado: recusa se não elegível (specification) ou item inexistente (`DomainRuleViolationException`, RuleId `RN-ORD-012`), marca o item, recalcula o total, emite um único `OrderItemCancelled`, idempotente.
**Where**: `src/Orders.Domain/Order.cs`, `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs`
**Depends on**: T3
**Reuses**: `OrderItem.Cancel()` (internal), `Order.Total`, `_events`
**Requirement**: CANC-01, CANC-02, CANC-03, CANC-04, CANC-05
**Tools**:
- MCP: NONE
- Skill: NONE
**Done when**:
- [ ] Testes 1:1: total recalculado (CANC-01); evento único com OrderId/ItemId/NewTotal (CANC-02); faturado recusa com RuleId RN-ORD-012 e nada muda (CANC-03); duas chamadas → um evento, mesmo total (CANC-04); item inexistente recusa sem alterar (CANC-05); último item cancelado → total 0,00 BRL (edge)
- [ ] Gate check passes: `dotnet test Orders.slnx --filter "FullyQualifiedName~RN_"`
- [ ] Test count: 9 testes RN_ORD_012 (total da suíte 13); nenhum teste anterior removido
- [ ] Build gate passes (último da fase): `dotnet build Orders.slnx && dotnet test Orders.slnx`
**Tests**: unit
**Gate**: build

---

### T5: CancelOrderItemHandler (orquestra, não decide)

**What**: `CancelOrderItemCommand(OrderId, ItemId)`, `CancelOrderItemResult(NewTotal, Events)` e `CancelOrderItemHandler(IOrderRepository)`: carrega, chama `Order.CancelItem`, persiste, devolve; sem `if` de negócio; teste de integração in-memory.
**Where**: `src/Orders.Application/CancelOrderItem/CancelOrderItemHandler.cs`
**Depends on**: T4
**Reuses**: `IOrderRepository`, `InMemoryOrderRepository` (teste), `AssemblyMarker`
**Requirement**: CANC-07
**Tools**:
- MCP: NONE
- Skill: NONE
**Done when**:
- [ ] Handler devolve `NewTotal` 30,00 BRL e 1 evento para o pedido de dois itens; pedido inexistente → `KeyNotFoundException`
- [ ] `ArchitectureTests` continuam verdes (Application não lança `DomainRuleViolationException`)
- [ ] Gate check passes: `dotnet test Orders.slnx`
- [ ] Test count: 11 RN_ORD_012 (total 15); nenhum teste anterior removido
**Tests**: integration
**Gate**: full

---

### T6: Marcar RN-ORD-012 como verified e fechar rastreabilidade

**What**: Atualizar o bloco RN-ORD-012 (`Código:`, `Teste:`, `Confiança: verified`, `Última revisão`) e a tabela de rastreabilidade da spec (CANC-01..07 → Implementing).
**Where**: `docs/regras/pedidos.md`
**Depends on**: T5
**Reuses**: -
**Requirement**: CANC-01, CANC-02, CANC-03, CANC-04, CANC-05, CANC-06, CANC-07
**Tools**:
- MCP: NONE
- Skill: `regras-de-negocio`
**Done when**:
- [ ] Bloco aponta arquivo:método reais e o arquivo de teste; `Confiança: verified`
- [ ] Build gate passes: `dotnet build Orders.slnx && dotnet test Orders.slnx`
**Tests**: none
**Gate**: build

---

## Phase Execution Map

```
Phase 1 → Phase 2
Phase 1:  T1 ------→ T2 ------→ T3 ------→ T4
Phase 2:  T5 ------→ T6
```

Execution is strictly sequential - 6 tasks cabem em um batch (≤ ~8): execução inline, sem sub-agentes de batch. O Verifier roda automaticamente após T6.
