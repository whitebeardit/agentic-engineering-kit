# Regras de negócio — Pedidos (Orders.Domain)

Fonte de verdade escrita. O card do Jira descreve a **mudança**; este arquivo descreve o **estado**. Toda regra tem ID, EARS,
onde vive no código, qual teste a prova, **confiança** (`verified` = teste passa; `inferred` = lida do código, sem teste), dono e data. A skill `regras-de-negocio` é o procedimento para mudar isto.

## RN-ORD-001 — Valor monetário válido
THE SYSTEM SHALL recusar valor negativo e moeda que não seja código ISO de 3 letras
THE SYSTEM SHALL recusar soma de moedas diferentes
Código: `src/Orders.Domain/Money.cs` (construtor, `Add`)  Teste: —  Confiança: inferred  Dono: <pessoa>  Desde: ADR-0003  Última revisão: 2026-08-27

## RN-ORD-002 — Quantidade positiva
THE SYSTEM SHALL recusar item com quantidade ≤ 0
Código: `src/Orders.Domain/OrderItem.cs` (construtor)  Teste: —  Confiança: inferred  Dono: <pessoa>  Última revisão: 2026-08-27

## RN-ORD-003 — Só pedido aberto recebe itens
Código: `src/Orders.Domain/Order.cs → AddItem`  Teste: —  Confiança: inferred  Última revisão: 2026-08-27

## RN-ORD-004 — Só pedido aberto pode ser faturado
Código: `src/Orders.Domain/Order.cs → Invoice`  Teste: —  Confiança: inferred  Última revisão: 2026-08-27

## RN-ORD-012 — Cancelamento parcial
WHEN o cliente cancela um item de pedido Aberto
THE SYSTEM SHALL marcar o item como cancelado, recalcular o total (soma dos subtotais não cancelados) e emitir exatamente um `OrderItemCancelled` com o novo total
IF o pedido já foi faturado (ou está Cancelado) THEN THE SYSTEM SHALL recusar com `DomainRuleViolationException(RN-ORD-012)` e não alterar total, itens nem eventos
IF o item não pertence ao pedido THEN THE SYSTEM SHALL recusar com `DomainRuleViolationException(RN-ORD-012)` sem alterar o pedido
THE SYSTEM SHALL CONTINUE TO ser idempotente: cancelar o mesmo item duas vezes emite um único evento e mantém o total
Código: `src/Orders.Domain/Order.cs → CancelItem` · predicado em `Specifications/PedidoElegivelParaCancelamento.cs` · handler `src/Orders.Application/CancelOrderItem/CancelOrderItemHandler.cs`
Teste: `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs` (10 testes, um por cláusula EARS + edge + handler)  Confiança: verified
Contrato afetado: evento `OrderItemCancelled` v1 (público — `rules/contracts.md`; AD-001)
Dono: <pessoa>  Desde: ADR-0003/0004, spec `.specs/features/001-cancelamento-parcial/` (CANC-01..07)  Última revisão: 2026-08-29

## Regras transversais (vivem no vault, não aqui)
- Política de reembolso após cancelamento → Billing + Orders concordam no vault `engenharia/regras-transversais.md#reembolso`.
