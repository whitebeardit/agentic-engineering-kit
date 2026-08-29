# 001 — Cancelamento parcial · design

## Impacto (saída do impact-analyzer)
| Repo | Muda | Contrato afetado | Ordem |
|---|---|---|---|
| orders-sample (Orders) | `Order.CancelItem`, handler, evento | `OrderItemCancelled` (novo, v1) | 1º contrato, 2º produtor |
| erp-mono (ERP) | consumidor do evento → libera reserva | — | 3º, atrás de flag |

## Contratos (primeiro)
- AsyncAPI: novo evento `orders.order-item-cancelled.v1` `{orderId, itemId, newTotal{amount,currency}, occurredAt}`. Aditivo → compatível.

## Sequência
Cliente → API Orders → `CancelOrderItemHandler` → `Order.CancelItem` (RN-ORD-012) → persiste → publica `OrderItemCancelled` → ERP consome → `ReservaEstoque.Liberar` (flag).

## Legado
- Characterization test: `CalculadoraFrete` já congelado (`tests/Legacy`); reserva de estoque precisa do seu antes de mexer.
- Feature flag: `estoque.libera-por-evento` (off em prod até UAT).

## Estratégia de teste (critério → teste)
| Critério | Teste | Tipo |
|---|---|---|
| R1.1 | `RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_aberto_SHALL_recalcular_total` | unit |
| R1.2 | `RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_OrderItemCancelled_com_novo_total` | unit |
| R1.3 | `RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_PedidoFaturado` | unit |
| R1.4 | `RN_ORD_012_SHALL_CONTINUE_TO_ser_idempotente_…` | unit |
| orquestração | `RN_ORD_012_handler_orquestra_e_nao_decide` | integration (in-memory) |
| camadas | `ArchitectureTests.*` | arquitetura |

## ADRs
- Segue ADR-0003 e ADR-0004. Nenhum conflito.

**Aprovação (gate 2)**: <tech lead> · 2026-08-27
