# Cancelamento parcial de pedido (ORD-231) Specification

**Card**: ORD-231 · **Tier de risco**: médio · **Tamanho (auto-sizing)**: Large — cruza serviços (Orders → ERP) e cria contrato público novo
**Repo dono do contrato**: orders-sample (Orders). O consumidor do ERP é feature separada no repo do ERP.

## Problem Statement

Hoje um cliente que desiste de um item precisa cancelar o pedido inteiro ou pedir estorno depois do faturamento, e o
financeiro faz o estorno à mão. Queremos que um item de pedido **ainda não faturado** possa ser cancelado sozinho,
com o total recalculado e um evento publicado para quem precisa reagir (estoque, no ERP).

## Goals

- [ ] Cancelar um item de pedido aberto recalcula o total e emite `OrderItemCancelled` com o novo total.
- [ ] Pedido faturado recusa o cancelamento sem alterar nada.
- [ ] Cancelar o mesmo item duas vezes é idempotente (um único evento).

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
| ------- | ------ |
| Reembolso automático (Billing) | Card próprio depois desta entrega |
| Cancelamento do pedido inteiro | Já existe |
| Consumidor do evento no ERP (liberar reserva de estoque, atrás de flag) | Outro repositório; feature separada no repo do ERP — esta spec é a do repo dono do contrato |
| API HTTP e publicação do schema em catálogo AsyncAPI | Não existem neste exemplo; o contrato é o record do evento |
| Alterar schema de Payments ou o contrato v1 de OrderCreated | "Nunca modificar" do card |

---

## Assumptions & Open Questions

Every ambiguity is resolved or recorded here - nothing is left silently unclear.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Item já separado fisicamente no estoque pode ser cancelado? | Sim — o Orders não conhece separação; quem decide é o ERP ao consumir o evento | Orders não tem esse dado; bloquear aqui duplicaria regra do ERP | n (pergunta ao PO registrada) |
| Pedido em status Cancelado tenta cancelar item | Recusar, igual a Faturado: só pedido Aberto é elegível | Uma única regra de elegibilidade (status == Aberto) | n |
| Item que não pertence ao pedido | Recusar com violação de regra (RN-ORD-012), sem alterar o pedido | Entrada inválida não pode mutar o agregado | y (RN-ORD-002/003 seguem o mesmo padrão) |
| Payload do evento | OrderId, ItemId, NewTotal (Money), OccurredAt | Mínimo que o consumidor (ERP) precisa; mudar campo = versionar (rules/contracts) | y |
| Status `Cancelado` não é alcançável neste repositório (não existe `Order.Cancel()`) | A specification testa `Status == Aberto`; os casos Faturado e Aberto têm teste; Cancelado fica coberto por construção | Não adicionar código de produção só para testar; o card diz que cancelamento total "já existe" — não neste exemplo | y |
| Concorrência entre dois cancelamentos simultâneos | N/A neste exemplo (repositório in-memory, sem transação) | Fora do escopo do exemplo; registrar como limitação | y |

**Open questions:** none - all resolved or logged above (required before the spec is confirmed).

### Implicit-requirement dimensions (Large: cada dimensão vira requisito ou N/A)

| Dimension | Resolution |
| --------- | ---------- |
| Input validation & bounds | CANC-05 (item inexistente) |
| Failure / partial-failure states | N/A because o repositório é in-memory e a operação é uma única mutação do agregado |
| Idempotency / retry / duplicate handling | CANC-04 |
| Auth boundaries & rate limits | N/A because não há API neste exemplo; autorização é da borda HTTP, fora do escopo |
| Concurrency / ordering | N/A because in-memory, sem concorrência (registrado em Assumptions) |
| Data lifecycle / expiry | N/A because nada é apagado; item cancelado permanece no pedido com `Cancelled = true` |
| Observability | CANC-02 (o evento é o sinal observável); logs N/A neste exemplo |
| External-dependency failure | N/A because o consumidor do ERP está fora do escopo |
| State-transition integrity | CANC-03 e CANC-06 (só pedido Aberto é elegível) |

---

## User Stories

### P1: Cancelar um item do meu pedido aberto ⭐ MVP

**User Story**: As a cliente, I want cancelar um item do meu pedido enquanto ele não foi faturado so that eu não pague por ele.

**Why P1**: É o vertical slice inteiro: elegibilidade, recálculo, evento e recusa.

**Acceptance Criteria** (each line is one EARS pattern):
1. WHEN o cliente cancela um item de um pedido Aberto THEN system SHALL marcar o item como cancelado e recalcular o total como a soma dos subtotais dos itens não cancelados  <!-- event-driven -->
2. WHEN o cliente cancela um item de um pedido Aberto THEN system SHALL emitir exatamente um `OrderItemCancelled` com `OrderId`, `ItemId` e `NewTotal` igual ao total recalculado  <!-- event-driven -->
3. IF o pedido já foi faturado THEN system SHALL recusar com `DomainRuleViolationException` cujo `RuleId` é `RN-ORD-012`, sem alterar total, itens ou eventos  <!-- unwanted-behavior -->
4. The system SHALL ser idempotente: cancelar o mesmo item duas vezes produz um único `OrderItemCancelled` e o mesmo total  <!-- ubiquitous -->
5. IF o item não pertence ao pedido THEN system SHALL recusar com `DomainRuleViolationException` (`RuleId` `RN-ORD-012`) sem alterar o pedido  <!-- unwanted-behavior -->
6. WHILE o pedido não está Aberto (Faturado ou Cancelado) system SHALL considerar o pedido não elegível para cancelamento de item  <!-- state-driven -->
7. WHEN o handler de aplicação recebe o comando THEN system SHALL carregar o pedido, delegar a decisão ao domínio, persistir e devolver o novo total e os eventos emitidos — sem conter regra de negócio (ADR-0003/0004)  <!-- event-driven -->

**Independent Test**: Pedido com dois itens (100 + 30): cancelar o primeiro → total 30 e um evento com NewTotal 30; faturar e tentar cancelar → exceção RN-ORD-012 e total inalterado.

---

## Edge Cases

Edge cases are usually unwanted-behavior (IF/THEN) or boundary (WHEN) criteria:
- IF o item não pertence ao pedido THEN system SHALL recusar sem alterar o pedido (CANC-05)
- WHEN o único item restante é cancelado THEN system SHALL recalcular o total para 0,00 BRL (boundary de CANC-01)
- IF o pedido está Cancelado THEN system SHALL recusar como não elegível (CANC-06) — inalcançável neste repositório (sem `Order.Cancel()`; ver Assumptions): coberto por construção (`Status == Aberto`). A feature que criar `Order.Cancel()` deve adicionar o teste `RN_ORD_012_WHILE_pedido_Cancelado…`

---

## Requirement Traceability

Each requirement gets a unique ID for tracking across design, tasks, and validation.

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| CANC-01 | P1: recalcular total ao cancelar item | Done | ✅ Verified |
| CANC-02 | P1: emitir OrderItemCancelled com novo total | Done | ✅ Verified |
| CANC-03 | P1: pedido faturado recusa sem alterar | Done | ✅ Verified |
| CANC-04 | P1: idempotência (um único evento) | Done | ✅ Verified |
| CANC-05 | P1: item inexistente recusa sem alterar | Done | ✅ Verified |
| CANC-06 | P1: só pedido Aberto é elegível | Done | ✅ Verified |
| CANC-07 | P1: handler orquestra, não decide | Done | ✅ Verified |

**ID format:** `[CATEGORY]-[NUMBER]` · **Status values:** Pending → In Design → In Tasks → Implementing → Verified
**Coverage:** 7 total, 7 mapped to tasks (T1–T6), 0 unmapped

---

## Success Criteria

How we know the feature is successful:
- [ ] `dotnet test Orders.slnx` verde com os testes RN_ORD_012 cobrindo CANC-01..07 (1:1, nomes com o ID da regra).
- [ ] Verifier do tlc: validation.md PASS, mutantes injetados mortos.
- [ ] `docs/regras/pedidos.md` com o bloco RN-ORD-012 apontando código, teste e `Confiança: verified`.
