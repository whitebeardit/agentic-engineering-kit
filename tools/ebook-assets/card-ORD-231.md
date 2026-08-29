# ORD-231 — Cancelamento parcial de pedido (card, como veio do PO)

Tipo: História · Prioridade: Alta · Componente: Orders · Sistemas afetados: Orders (micro), ERP legado (estoque)

Como cliente, quero cancelar um item do meu pedido enquanto ele ainda não foi faturado, para não pagar por ele e
reduzir os estornos manuais que o financeiro faz hoje.

Critérios de aceite:
- WHEN o cliente cancela um item de pedido não faturado THE SYSTEM SHALL recalcular o total do pedido
- WHEN o cliente cancela um item THE SYSTEM SHALL emitir o evento OrderItemCancelled com o novo total
- IF o pedido já foi faturado THEN THE SYSTEM SHALL recusar o cancelamento e não alterar o pedido
- THE SYSTEM SHALL CONTINUE TO ser idempotente: cancelar o mesmo item duas vezes gera um único evento
- WHEN OrderItemCancelled é consumido pelo ERP THE SYSTEM SHALL liberar a reserva de estoque do item (atrás de flag)

Fora de escopo: reembolso automático (Billing) — card próprio depois. Cancelamento do pedido inteiro já existe.
Nunca modificar: schema de Payments; contrato v1 de OrderCreated.
Tier de risco: médio (não toca pagamento nem dados pessoais).
Validação com o PO: pedido de teste com dois itens no ambiente de homologação.
Pergunta aberta: item já separado fisicamente no estoque pode ser cancelado? (o legado não distingue)
