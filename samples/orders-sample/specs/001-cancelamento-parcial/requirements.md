# 001 — Cancelamento parcial de pedido · requirements

**Origem**: ORD-231 (Jira) · **Tier de risco**: médio (não toca pagamento nem dados pessoais) · **Sistemas**: Orders (micro), ERP legado (estoque — reserva)

## Objetivo
Permitir que o cliente cancele um item de um pedido ainda não faturado, para reduzir estornos manuais no financeiro.

## Fora de escopo
- Reembolso automático (Billing) — vira card próprio após esta entrega.
- Cancelamento de pedido inteiro (já existe).

## Histórias e critérios (EARS)
### H1 — como cliente, quero cancelar um item do meu pedido aberto para não pagar por ele
- R1.1 `WHEN o cliente cancela um item de pedido não faturado THE SYSTEM SHALL recalcular o total`
- R1.2 `WHEN o cliente cancela um item THE SYSTEM SHALL emitir OrderItemCancelled com o novo total`
- R1.3 `IF o pedido já foi faturado THEN THE SYSTEM SHALL recusar e não alterar o pedido`
- R1.4 `THE SYSTEM SHALL CONTINUE TO manter idempotência: cancelar o mesmo item duas vezes gera um único evento`

### H2 — como estoque (ERP), quero liberar a reserva do item cancelado
- R2.1 `WHEN OrderItemCancelled é consumido THE SYSTEM SHALL liberar a reserva no ERP` — atrás de flag `estoque.libera-por-evento`

## Nunca modificar
- Schema de `Payments`; contrato v1 de `OrderCreated`.

## Perguntas abertas
- [NEEDS CLARIFICATION: item já separado no estoque físico pode ser cancelado? PO decide — hoje o legado não distingue]

**Aprovação (gate 1)**: <PO> · 2026-08-27
