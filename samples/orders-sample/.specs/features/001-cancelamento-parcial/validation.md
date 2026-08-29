# Cancelamento parcial de pedido (ORD-231) Validation

**Date**: 2026-08-29
**Spec**: `.specs/features/001-cancelamento-parcial/spec.md`
**Diff range**: `545d58a..HEAD` (branch `tlc/001`; commits `fa4eff9`, `42f1edc`, `c298625`, `b64ced9`, `d7f2314`, `5293152`, `bcdf056`)
**Verifier**: independent sub-agent (author ≠ verifier)
**Ambiente**: `DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 DiffEngine_Disabled=true`; todo gate com build fresco (nunca `--no-build`, lição L-001)

Legenda de caminhos: `T` = `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs` · `A` = `tests/Orders.Tests/ArchitectureTests.cs`. Todos os `file:line` foram re-derivados pelo Verifier lendo os arquivos no HEAD (`bcdf056`), não copiados de tasks.md.

---

## Task Completion

| Task | Status  | Commit | Notes |
| ---- | ------- | ------ | ----- |
| T1 — RN-ORD-012 em `docs/regras/pedidos.md` | ✅ Done | `fa4eff9` | bloco EARS + `Confiança: inferred` antes de codar |
| T2 — evento `OrderItemCancelled` | ✅ Done | `42f1edc` | `src/Orders.Domain/Events/OrderItemCancelled.cs:7` — record selado, XML-doc de contrato v1 |
| T3 — specification `PedidoElegivelParaCancelamento` | ✅ Done | `c298625` | `src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs:9` — `Status == Aberto` |
| T4 — `Order.CancelItem` | ✅ Done | `b64ced9` | `src/Orders.Domain/Order.cs:63-80` |
| T5 — `CancelOrderItemHandler` | ✅ Done (com fix) | `d7f2314` + `bcdf056` | 1º commit não compilava (`using Orders.Infrastructure;` ausente); corrigido 1 min depois; gate original julgado com `--no-build` (L-001 registrada) |
| T6 — `Confiança: verified` + rastreabilidade | ✅ Done | `5293152` | ver observação de sequência abaixo |

Todas as 6 tarefas estão marcadas `✅ Done` em tasks.md, com `Done when` totalmente marcado ([x]) e commit correspondente em `git log --oneline 545d58a..HEAD`. Nenhuma tarefa bloqueada ou parcial.

**Observação de sequência (não bloqueante)**: `5293152` (T6, "verified", 09:33:38) foi commitado antes de `bcdf056` (fix do build, 09:34:38). Naquele commit o arquivo de teste ainda não tinha `using Orders.Infrastructure;`, logo o "14 passed" registrado em T6 só pode ter vindo de binário anterior. No HEAD atual a afirmação é verdadeira (gate abaixo).

---

## Spec-Anchored Acceptance Criteria

### P1: Cancelar um item do meu pedido aberto ⭐ MVP

Fixture comum: `T:15-21` — pedido Aberto com itens A (2 × 50,00 = 100,00 BRL) e B (1 × 30,00 = 30,00 BRL); total inicial 130,00 BRL. Bate com o "Independent Test" da spec (100 + 30).

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| CANC-01 · WHEN cancela item de pedido Aberto THEN marca item cancelado e recalcula total = soma dos subtotais não cancelados | `item.Cancelled == true`; `Total == 30,00 BRL` | `T:55` - `Assert.True(a.Cancelled);` · `T:56` - `Assert.Equal(Money.Brl(30), order.Total);` | ✅ PASS |
| CANC-02 · WHEN cancela item THEN emite exatamente um `OrderItemCancelled` com `OrderId`, `ItemId`, `NewTotal` = total recalculado | exatamente 1 evento; `OrderId == order.Id`; `ItemId == a.Id`; `NewTotal == 30,00 BRL` | `T:68` - `var evt = Assert.Single(order.Events.OfType<OrderItemCancelled>());` · `T:69` - `Assert.Equal(order.Id, evt.OrderId);` · `T:70` - `Assert.Equal(a.Id, evt.ItemId);` · `T:71` - `Assert.Equal(Money.Brl(30), evt.NewTotal);` | ✅ PASS |
| CANC-03 · IF pedido faturado THEN recusa com `DomainRuleViolationException` `RuleId == "RN-ORD-012"`, sem alterar total, itens ou eventos | exceção com `RuleId "RN-ORD-012"`; `a.Cancelled == false`; `Total == 130,00 BRL`; `Events` vazio | `T:82` - `var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(a.Id));` · `T:84` - `Assert.Equal("RN-ORD-012", ex.RuleId);` · `T:85` - `Assert.False(a.Cancelled);` · `T:86` - `Assert.Equal(Money.Brl(130), order.Total);` · `T:87` - `Assert.Empty(order.Events);` | ✅ PASS |
| CANC-04 · SHALL ser idempotente: cancelar o mesmo item duas vezes → um único evento e o mesmo total | após 2 chamadas (`T:97-98`): 1 evento; `Total == 30,00 BRL` | `T:100` - `Assert.Single(order.Events.OfType<OrderItemCancelled>());` · `T:101` - `Assert.Equal(Money.Brl(30), order.Total);` | ✅ PASS (sensor MUT-C confirma discriminação) |
| CANC-05 · IF item não pertence ao pedido THEN recusa com `DomainRuleViolationException` (`RuleId "RN-ORD-012"`) sem alterar o pedido | exceção `RuleId "RN-ORD-012"`; `Total == 130,00 BRL`; `Events` vazio | `T:111` - `var ex = Assert.Throws<DomainRuleViolationException>(() => order.CancelItem(Guid.NewGuid()));` · `T:113` - `Assert.Equal("RN-ORD-012", ex.RuleId);` · `T:114` - `Assert.Equal(Money.Brl(130), order.Total);` · `T:115` - `Assert.Empty(order.Events);` | ✅ PASS |
| CANC-06 · WHILE pedido não está Aberto (Faturado ou Cancelado) SHALL considerar não elegível | `IsSatisfiedBy(Aberto) == true`; `IsSatisfiedBy(Faturado) == false`; `IsSatisfiedBy(Cancelado) == false` | `T:30-32` - `var elegivel = new PedidoElegivelParaCancelamento().IsSatisfiedBy(order); … Assert.True(elegivel);` · `T:41-43` - (após `order.Invoice()` em `T:39`) `Assert.False(elegivel);` · **Cancelado**: sem `file:line` — estado inalcançável no repo (`OrderStatus.Cancelado` existe em `src/Orders.Domain/OrderStatus.cs:7`, mas não há `Order.Cancel()` e `Status` tem `private set`, `src/Orders.Domain/Order.cs:19`); assumption confirmada em `spec.md:42` | ✅ PASS (Aberto/Faturado) · ⚠️ sub-estado Cancelado inalcançável — aceito por assumption confirmada; ver sensor MUT-D |
| CANC-07 · WHEN o handler recebe o comando THEN carrega, delega ao domínio, persiste e devolve novo total + eventos — sem regra de negócio (ADR-0003/0004) | `NewTotal == 30,00 BRL`; 1 evento; item persistido como cancelado; Application não lança `DomainRuleViolationException` nem depende de Infrastructure | `T:144` - `Assert.Equal(Money.Brl(30), result.NewTotal);` · `T:145` - `Assert.Single(result.Events);` · `T:147` - `Assert.True(persisted!.Items.Single(i => i.Id == a.Id).Cancelled);` · `A:50` - `.Should().NotDependOnAny(Types().That().Are(typeof(DomainRuleViolationException)))` (ADR-0004) · `A:41` - `.Should().NotDependOnAny(Infrastructure)` (ADR-0003) · leitura: `src/Orders.Application/CancelOrderItem/CancelOrderItemHandler.cs:13-21` não tem nenhum `if` de negócio | ✅ PASS |

**Independent Test da spec** (`spec.md:80`): coberto por `T:49-57` (cancelar A → 30,00 e evento em `T:62-72`) + `T:77-88` (faturar e tentar cancelar → RN-ORD-012, total 130,00 inalterado).

**Status**: ✅ All ACs covered — 7/7 com `file:line` e valor exato da spec. 0 spec-precision gaps (a spec define valores precisos em todos os critérios). Uma nota não bloqueante em CANC-06 (sub-estado `Cancelado` não testável por construção; ver avaliação abaixo).

### Avaliação do sub-estado `Cancelado` (CANC-06 / edge case 3)

- A spec declara (`spec.md:42`, `Confirmed? y`) que `Cancelado` não é alcançável neste repositório e que o caso fica "coberto por construção" porque a specification testa `Status == Aberto` (`PedidoElegivelParaCancelamento.cs:9`).
- Fato verificado: não existe `Order.Cancel()`; `Status` só muda via `Invoice()` (`Order.cs:52-60`). Sem reflexão, nenhum teste consegue produzir um pedido `Cancelado`.
- Evidência empírica (sensor diagnóstico MUT-D): trocar `== OrderStatus.Aberto` por `!= OrderStatus.Faturado` deixa os 10 testes verdes. Ou seja, a suíte **não fixa** o ramo `Cancelado`; a garantia é estrutural (forma da expressão), não testada. É um mutante equivalente neste repo, não fraqueza de asserção.
- Veredito: **aceitável, não bloqueante**. Não faz sentido adicionar código de produção (`Order.Cancel()`) ou reflexão só para testar. Risco residual documentado: quando `Order.Cancel()` for introduzido, a feature que o criar DEVE adicionar `RN_ORD_012_WHILE_pedido_Cancelado_SHALL_nao_ser_elegivel…` (a spec já lista o edge case, então a lacuna é visível).

---

## Discrimination Sensor

Executado em worktree git isolado (`git worktree add <scratch>/wt-sensor HEAD`, detached em `bcdf056`), uma mutação por vez, revertida com `git checkout -- .` dentro do worktree (worktree confirmado limpo após cada reversão e antes do `git worktree remove --force`). Comando: `dotnet test Orders.slnx --filter "FullyQualifiedName~RN_"` com build fresco (10 testes RN_). `git stash` não foi usado.

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| A | `src/Orders.Domain/Order.cs:65` | Inverteu a elegibilidade: `if (!new PedidoElegivelParaCancelamento().IsSatisfiedBy(this))` → `if (new PedidoElegivelParaCancelamento().IsSatisfiedBy(this))` | ✅ Killed — exit 1, 6 testes falharam (CANC-01, CANC-02, CANC-03, CANC-04, edge zero, CANC-07 handler) |
| B | `src/Orders.Domain/Order.cs:79` | Removeu o efeito colateral obrigatório `_events.Add(new OrderItemCancelled(Id, itemId, Total));` | ✅ Killed — exit 1, 4 testes falharam (CANC-02, CANC-04, edge zero, CANC-07 handler) |
| C | `src/Orders.Domain/Order.cs:73-76` | Removeu o early-return de idempotência `if (item.Cancelled) { return; }` | ✅ Killed — exit 1, 1 teste falhou (exatamente `RN_ORD_012_SHALL_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes`, `T:93`) |

**Sensor depth**: lightweight (3 mutações comportamentais no código novo de maior risco: elegibilidade, evento, idempotência)
**Result**: 3/3 killed - PASS ✅

**Diagnóstico adicional (não contabilizado no 3/3)**:

| Mutation | File:line | Description | Outcome |
| -------- | --------- | ----------- | ------- |
| D | `src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs:9` | `return candidate.Status == OrderStatus.Aberto;` → `return candidate.Status != OrderStatus.Faturado;` | ⚠️ Sobreviveu (exit 0, 10/10 verdes) — **mutante equivalente** neste repo: `Cancelado` é inalcançável, logo as duas expressões são indistinguíveis por teste. Não é fraqueza de asserção; é o limite documentado em `spec.md:42`. Sem fix task. |

**Isolamento**: baseline `git status --porcelain` na raiz do repo antes do sensor = vazio. Após remoção do worktree, o porcelain mostrava ` M samples/orders-sample/.specs/STATE.md` (mtime 09:36:53, edição do orquestrador: "Verifier independente em execução"), ` M tools/gen-ebook.py`, `?? tools/ebook-assets/` (mtime 09:40:25) e depois ` M README.md` — todos alterados **concorrentemente por outros atores** durante a verificação, em caminhos que o sensor nunca tocou. Prova de não-vazamento: `git diff --stat HEAD -- samples/orders-sample/src samples/orders-sample/tests samples/orders-sample/docs samples/orders-sample/AGENTS.md` vazio (os arquivos mutados — `Order.cs`, `PedidoElegivelParaCancelamento.cs` — são idênticos ao HEAD) e o worktree estava limpo antes de ser removido. O Verifier **não reverteu** os arquivos alheios (seria destrutivo). Sensor considerado válido.

---

## Interactive UAT Results (if performed)

Não realizado — feature backend-only (domínio + handler in-memory, sem UI nem API); checagens automatizadas são suficientes (validate.md §3).

---

## Code Quality

Arquivos do diff analisados: `src/Orders.Domain/Order.cs` (+21), `src/Orders.Domain/Events/OrderItemCancelled.cs` (+10), `src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs` (+11), `src/Orders.Application/CancelOrderItem/{CancelOrderItemCommand,CancelOrderItemHandler,CancelOrderItemResult}.cs` (+32), `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs` (+157), `docs/regras/pedidos.md` (+11), `AGENTS.md` (+1), `.specs/**`.

| Principle        | Status |
| ---------------- | ------ |
| Minimum code (no features beyond what was asked) | ✅ — nenhum dispatcher/outbox, nenhum `Order.Cancel()`, nenhum campo extra no evento (`Sku` rejeitado no design) |
| No abstractions for single-use code | ✅ — a specification é a única abstração e é decisão registrada (AD-002, ADR-0004) |
| No unnecessary flexibility | ✅ — `OccurredAt` com default `UtcNow`, sem clock injetável (in-memory example) |
| Surgical changes (only files required) | ✅ — `Order.cs` só ganhou `using` + `CancelItem`; `AGENTS.md` ganhou 1 linha (gotcha `--no-build`, decorrente de L-001) |
| Didn't "improve" unrelated code | ✅ — `AddItem`/`Invoice`/`Total` intactos (`git diff 545d58a..HEAD -- Order.cs` mostra só adições) |
| Matches patterns | ✅ — `DomainRuleViolationException("RN-ORD-012", msg)` igual a RN-ORD-003/004 (`Order.cs:44,56`); record selado como os value objects; testes com o padrão `RN_ORD_<n>_…` |
| Would senior engineer approve? | ✅ — duas notas cosméticas: (1) mensagem `"Pedido faturado não admite cancelamento de item."` (`Order.cs:67`) é mais estreita que a regra (também Cancelado); (2) `CancelOrderItemResult.Events` devolve todos os `OrderItemCancelled` acumulados no agregado (`CancelOrderItemHandler.cs:20`), não só os deste comando — coerente com "sem dispatcher" (design › Tech Decisions), mas vale registrar quando houver publicação |
| Tests map to ACs and are non-shallow (spot-check P1) | ✅ — CANC-03 assere exceção + RuleId + item + total + eventos (`T:82-87`), não só "lançou" |
| Spec-anchored outcome check (asserted values match spec) | ✅ — 30,00 / 130,00 / 0,00 BRL, `"RN-ORD-012"`, `Assert.Single`, `Assert.Empty`, `KeyNotFoundException` |
| Per-layer Coverage Expectation met | ✅ — Domain 1:1 (CANC-01..06 + edge, 8 testes); Application happy (`T:135`) + erro (`T:151`); Arquitetura 3 testes verdes cobrindo o novo tipo em Application; sem rotas no escopo |
| Every test maps to a spec requirement — no unclaimed tests | ✅ — 10 testes: 2×CANC-06, CANC-01, CANC-02, CANC-03, CANC-04, CANC-05, edge "último item → 0,00", CANC-07 happy, CANC-07 erro (`KeyNotFoundException`, design › Error Handling) |
| Documented guidelines followed | ✅ — `AGENTS.md` § Testes (nome `RN_ORD_<n>_…`, local `tests/Orders.Tests/RN_*Tests.cs`, handler com `InMemoryOrderRepository`, ArchitectureTests) e § Never (nenhum `DomainRuleViolationException` fora de Domain; Application sem referência a Infrastructure); `docs/adr/0003`, `0004`; `Directory.Build.props` warnings-as-errors (build com 0 warnings) |

---

## Edge Cases

- [x] IF o item não pertence ao pedido THEN recusa sem alterar o pedido (CANC-05): `T:111-115` — exceção `RuleId "RN-ORD-012"`, `Total == 130,00 BRL`, `Events` vazio
- [x] WHEN o único item restante é cancelado THEN total = 0,00 BRL (boundary CANC-01): `T:128` - `Assert.Equal(Money.Brl(0), order.Total);` · `T:129` - `Assert.Equal(2, order.Events.OfType<OrderItemCancelled>().Count());`
- [~] IF o pedido está Cancelado THEN recusa como não elegível (CANC-06): sem teste — estado inalcançável (sem `Order.Cancel()`); aceito por assumption confirmada `spec.md:42`; risco residual e gatilho de follow-up registrados na seção "Avaliação do sub-estado Cancelado". Não bloqueante.

---

## Gate Check

- **Gate command**: `dotnet build Orders.slnx && dotnet test Orders.slnx` (Build gate, tasks.md › Gate Check Commands) — build fresco, sem `--no-build`
- **Exit codes**: `dotnet build` = 0 (Build succeeded, 0 Warning(s), 0 Error(s)); `dotnet test` = 0
- **Result**: 14 passed, 0 failed, 0 skipped
- **Test count before feature**: 4 (base `545d58a`: 3 `[Fact]` em `ArchitectureTests.cs` + 1 em `Legacy/CalculadoraFreteCharacterizationTests.cs`)
- **Test count after feature**: 14 (10 `RN_ORD_012_*` + 3 ArchitectureTests + 1 characterization)
- **Delta**: +10 new tests (esperado +10 ✅)
- **Test integrity**: nenhum teste removido ou enfraquecido — `ArchitectureTests.cs` e `Legacy/**` não aparecem no diff `545d58a..HEAD`; `.verified.txt` inalterado
- **Skipped tests**: none
- **Failures**: none

Testes executados (14): `RN_ORD_012_WHILE_pedido_Aberto_SHALL_ser_elegivel_para_cancelamento_de_item`, `RN_ORD_012_WHILE_pedido_Faturado_SHALL_nao_ser_elegivel_para_cancelamento_de_item`, `RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_Aberto_SHALL_marcar_cancelado_e_recalcular_total`, `RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_um_OrderItemCancelled_com_OrderId_ItemId_e_NewTotal`, `RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_RuleId_RN_ORD_012_sem_alterar_o_pedido`, `RN_ORD_012_SHALL_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes`, `RN_ORD_012_IF_item_nao_pertence_ao_pedido_THEN_SHALL_recusar_sem_alterar_o_pedido`, `RN_ORD_012_WHEN_ultimo_item_e_cancelado_SHALL_recalcular_total_para_zero`, `RN_ORD_012_WHEN_handler_recebe_comando_SHALL_orquestrar_persistir_e_devolver_novo_total_e_eventos`, `RN_ORD_012_IF_pedido_inexistente_THEN_handler_SHALL_lancar_KeyNotFoundException`, `ArchitectureTests.Domain_nao_depende_de_Application_nem_de_Infrastructure`, `ArchitectureTests.Application_nao_depende_de_Infrastructure`, `ArchitectureTests.Application_nao_lanca_DomainRuleViolationException`, `Legacy.CalculadoraFreteCharacterizationTests.Congela_comportamento_atual_do_calculo_de_frete`.

---

## Fix Plans (if issues found)

Nenhum gap bloqueante. Sem fix tasks.

**Observações não bloqueantes sobre artefatos** (para o orquestrador, não exigem re-verificação):

1. `tasks.md` (T4/T5 Post-gate) cita `file:line` deslocados em −1 em relação ao HEAD (ex.: `…Tests.cs:54` → real `T:55`; `:143` → `T:144`; `:154` → `T:155`) porque `bcdf056` inseriu `using Orders.Infrastructure;` na linha 5. Este relatório usa as linhas reais.
2. `AGENTS.md:7` diz "9 testes: 5 regra, 3 arquitetura, 1 characterization"; o real é 14 (10 regra). Já estava errado na base (havia 4) e a linha foi mantida quando `AGENTS.md` foi editado em `bcdf056`.
3. `docs/regras/pedidos.md:28` marcou `Confiança: verified` no commit `5293152`, um minuto antes do fix de build (`bcdf056`) — no HEAD a afirmação é verdadeira, mas a ordem foi invertida em relação à definição de pronto do próprio AGENTS.md (validation.md PASS).
4. `spec.md` lista como edge case "pedido Cancelado" e, ao mesmo tempo, o declara inalcançável nas Assumptions — a spec contradiz levemente a si mesma. Sugestão: anotar o edge case como "por construção; gatilho: quando existir `Order.Cancel()`".

---

## Requirement Traceability Update

Update spec.md requirement statuses:

| Requirement | Previous Status | New Status  |
| ----------- | --------------- | ----------- |
| CANC-01     | Implementing    | ✅ Verified |
| CANC-02     | Implementing    | ✅ Verified |
| CANC-03     | Implementing    | ✅ Verified |
| CANC-04     | Implementing    | ✅ Verified |
| CANC-05     | Implementing    | ✅ Verified |
| CANC-06     | Implementing    | ✅ Verified (sub-estado Cancelado por construção; assumption `spec.md:42`) |
| CANC-07     | Implementing    | ✅ Verified |

Aplicado em `spec.md` › Requirement Traceability (Phase → Done, Status → ✅ Verified). Nenhum outro trecho da spec foi alterado.

---

## Summary

**Overall**: ✅ Ready — PASS

**Spec-anchored check**: 7/7 ACs matched spec outcome · 0 spec-precision gaps · 1 nota não bloqueante (CANC-06 sub-estado `Cancelado` inalcançável, aceito por assumption confirmada)
**Sensor**: 3/3 mutations killed (+1 diagnóstico equivalente, não contabilizado)
**Gate**: 14 passed, 0 failed, 0 skipped (build exit 0, test exit 0)

**What works**: recálculo do total (30,00 / 0,00 BRL), evento único `OrderItemCancelled` com `OrderId`/`ItemId`/`NewTotal`, recusa de pedido faturado e de item inexistente com `RuleId "RN-ORD-012"` sem mutação do agregado (130,00 BRL, `Events` vazio), idempotência (um evento após duas chamadas), handler que só orquestra (ArchitectureTests verdes, `KeyNotFoundException` para pedido inexistente).

**Issues found**: nenhum bloqueante. Notas: mensagem de exceção mais estreita que a regra (`Order.cs:67`); `Events` do resultado do handler é o acumulado do agregado (`CancelOrderItemHandler.cs:20`); artefatos com `file:line` deslocados (tasks.md) e contagem de testes desatualizada (`AGENTS.md:7`).

**Next steps**: orquestrador fecha a feature (`validate_state.py` abaixo), commita `validation.md` + `spec.md` (+ `STATE.md` já editado pelo orquestrador) e faz merge de `tlc/001`. Lessons: PASS limpo sem sinal grounded (nenhum mutante obrigatório sobreviveu, nenhuma spec-precision gap, nenhum AC sem evidência, nenhum `// SPEC_DEVIATION`) → nada registrado; L-001 (`gate_fail`) já existe e não foi duplicada.

---

## Deterministic gate

`python3 <skill-dir>/scripts/validate_state.py --root samples/orders-sample 001-cancelamento-parcial` (executado pelo Verifier em 2026-08-29, após escrever este relatório):

```

validate_state: 0 error(s) across [001-cancelamento-parcial]
```

Exit code: 0
