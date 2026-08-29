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
- [x] `IsSatisfiedBy(pedido Aberto) == true`; `IsSatisfiedBy(Faturado) == false` — cada um com teste nomeado `RN_ORD_012_…`. `Cancelado` não é alcançável neste repo (sem `Order.Cancel()`): coberto por construção, registrado como assumption na spec
- [x] Gate check passes: `dotnet test Orders.slnx --filter "FullyQualifiedName~RN_"` — 2 passed (2026-08-29)
- [x] Test count: 2 testes RN_ORD_012 (total da suíte 6)
**Tests**: unit
**Gate**: quick
**Status**: ✅ Done
**Post-gate (Check A/C — evidência ou zero)**:
| Critério | `file:line` + assertion | Spec-defined outcome | Covered? |
|---|---|---|---|
| CANC-06 (Aberto → elegível = true) | `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs:30` - `Assert.True(elegivel);` | Aberto → elegível = true | ✅ Yes |
| CANC-06 (Faturado → elegível = false) | `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs:41` - `Assert.False(elegivel);` | Faturado → elegível = false | ✅ Yes |
| CANC-06 (Cancelado → não elegível) | — | status inalcançável neste repo (assumption na spec) | ⚠️ coberto por construção |
Check C: os 2 testes mapeiam para CANC-06; nenhum teste sem requisito. Veredito: adequado.


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
- [x] Testes 1:1: total recalculado (CANC-01); evento único com OrderId/ItemId/NewTotal (CANC-02); faturado recusa com RuleId RN-ORD-012 e nada muda (CANC-03); duas chamadas → um evento, mesmo total (CANC-04); item inexistente recusa sem alterar (CANC-05); último item cancelado → total 0,00 BRL (edge)
- [x] Gate check passes: `dotnet test Orders.slnx --filter "FullyQualifiedName~RN_"` — 8 passed (2026-08-29)
- [x] Test count: 8 testes RN_ORD_012 (total da suíte 12); nenhum teste anterior removido
- [x] Build gate passes (último da fase): `dotnet build Orders.slnx && dotnet test Orders.slnx` — 0 warnings, 12 passed
**Tests**: unit
**Gate**: build
**Status**: ✅ Done
**Post-gate (Check A/C — evidência ou zero)**:
| Critério | `file:line` + assertion | Spec-defined outcome | Covered? |
|---|---|---|---|
| CANC-01 | `…Tests.cs:54` - `Assert.True(a.Cancelled);`; `…Tests.cs:55` - `Assert.Equal(Money.Brl(30), order.Total);`; `…Tests.cs:67` - `var evt = Assert.Single(order.Events.OfType<OrderItemCancelled>());` | item.Cancelled == true; Total == 30,00 BRL | ✅ Yes |
| CANC-02 | `…Tests.cs:67` - `var evt = Assert.Single(order.Events.OfType<OrderItemCancelled>());`; `…Tests.cs:68` - `Assert.Equal(order.Id, evt.OrderId);`; `…Tests.cs:69` - `Assert.Equal(a.Id, evt.ItemId);`; `…Tests.cs:70` - `Assert.Equal(Money.Brl(30), evt.NewTotal);` | exatamente 1 evento; OrderId, ItemId, NewTotal == 30,00 BRL | ✅ Yes |
| CANC-03 | `…Tests.cs:81` - `var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(a.Id));`; `…Tests.cs:83` - `Assert.Equal("RN-ORD-012", ex.RuleId);`; `…Tests.cs:84` - `Assert.False(a.Cancelled);`; `…Tests.cs:85` - `Assert.Equal(Money.Brl(130), order.Total);`; `…Tests.cs:86` - `Assert.Empty(order.Events);` | DomainRuleViolationException RuleId RN-ORD-012; item não cancelado; Total 130,00; Events vazio | ✅ Yes |
| CANC-04 | `…Tests.cs:99` - `Assert.Single(order.Events.OfType<OrderItemCancelled>());`; `…Tests.cs:100` - `Assert.Equal(Money.Brl(30), order.Total);`; `…Tests.cs:110` - `var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(Guid.NewGuid()));` | 1 evento após 2 chamadas; Total 30,00 | ✅ Yes |
| CANC-05 | `…Tests.cs:110` - `var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(Guid.NewGuid()));`; `…Tests.cs:112` - `Assert.Equal("RN-ORD-012", ex.RuleId);`; `…Tests.cs:113` - `Assert.Equal(Money.Brl(130), order.Total);`; `…Tests.cs:114` - `Assert.Empty(order.Events);` | RuleId RN-ORD-012; Total 130,00; Events vazio | ✅ Yes |
| edge CANC-01 | `…Tests.cs:127` - `Assert.Equal(Money.Brl(0), order.Total);`; `…Tests.cs:128` - `Assert.Equal(2, order.Events.OfType<OrderItemCancelled>().Count());` | Total 0,00 BRL; 2 eventos | ✅ Yes |
Check B: nenhuma asserção tautológica; estado (Total, Cancelled, Events) é asserido, não só a chamada. Check C: 6 testes ↔ CANC-01..05 + edge listado na spec; nenhum teste sem requisito. Check D: nomes `RN_ORD_012_…`, local `tests/Orders.Tests/RN_*Tests.cs` (AGENTS.md). Veredito: adequado.


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
- [x] Handler devolve `NewTotal` 30,00 BRL e 1 evento para o pedido de dois itens; pedido inexistente → `KeyNotFoundException`
- [x] `ArchitectureTests` continuam verdes (Application não lança `DomainRuleViolationException`) — 3 passed
- [x] Gate check passes: `dotnet test Orders.slnx` — 14 passed (2026-08-29)
- [x] Test count: 10 RN_ORD_012 (total 14); nenhum teste anterior removido
**Tests**: integration
**Gate**: full
**Status**: ✅ Done
**Post-gate (Check A/C — evidência ou zero)**:
| Critério | `file:line` + assertion | Spec-defined outcome | Covered? |
|---|---|---|---|
| CANC-07 | `…Tests.cs:143` - `Assert.Equal(Money.Brl(30), result.NewTotal);`; `…Tests.cs:144` - `Assert.Single(result.Events);`; `…Tests.cs:146` - `Assert.True(persisted!.Items.Single(i => i.Id == a.Id).Cancelled);` | NewTotal 30,00; 1 evento; item persistido como cancelado | ✅ Yes |
| CANC-07 (erro) | `…Tests.cs:154` - `await Assert.ThrowsAsync<KeyNotFoundException>(() => handler.HandleAsync(new CancelOrderItemCommand(Guid.NewGuid(), Guid.NewGuid()), CancellationToken.None));` | KeyNotFoundException | ✅ Yes |
Check B: estado persistido é asserido (não só a chamada). Check C: 2 testes ↔ CANC-07 e caminho de erro do design. Check D: nomes e local conforme AGENTS.md. Veredito: adequado.


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
