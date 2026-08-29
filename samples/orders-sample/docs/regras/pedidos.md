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
WHEN o cliente cancela um item de pedido não faturado
THE SYSTEM SHALL recalcular o total e emitir `OrderItemCancelled` com o novo total
IF o pedido já foi faturado THEN THE SYSTEM SHALL recusar com `DomainRuleViolationException(RN-ORD-012)` e não alterar o pedido
THE SYSTEM SHALL CONTINUE TO ser idempotente: cancelar o mesmo item duas vezes emite um único evento
Código: `src/Orders.Domain/Order.cs → CancelItem` · predicado em `Specifications/PedidoElegivelParaCancelamento.cs`
Teste: `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs` (um teste por cláusula)  Confiança: verified
Contrato afetado: evento `OrderItemCancelled` (público — `rules/contracts.md`)
Dono: <pessoa>  Desde: ADR-0003, spec `specs/001-cancelamento-parcial`  Última revisão: 2026-08-27

## Regras transversais (vivem no vault, não aqui)
- Política de reembolso após cancelamento → Billing + Orders concordam no vault `engenharia/regras-transversais.md#reembolso`.
