# card-intake · ORD-231 (fonte: texto colado — MCP atlassian não conectado nesta sessão)

## Definition of Ready
| Campo | Presente? |
|---|---|
| Objetivo (o quê + por quê) | ✅ cancelar item de pedido não faturado; reduzir estornos manuais |
| Critérios de aceite em EARS | ✅ 5 critérios (4 do Orders, 1 do ERP) |
| Escopo dentro/fora | ✅ fora: reembolso automático; cancelamento total já existe |
| Sistemas afetados | ✅ Orders (micro), ERP legado (estoque) |
| Caminhos prováveis | ⚠️ ausente — inferidos: `src/Orders.Domain/Order.cs`, `Events/`, `Specifications/`, `src/Orders.Application/`, `tests/Orders.Tests/` |
| Nunca modificar | ✅ schema de Payments; contrato v1 de OrderCreated |
| Tier de risco | ✅ médio |
| Como validar com o PO | ✅ pedido de teste com 2 itens em homologação |
Resultado: **passa** (caminhos inferidos — informar ao PO, não bloqueia).

## Conflitos com regras/ADRs
Nenhum. ADR-0003/0004 exigem que a regra viva em `Orders.Domain` e que Application só orquestre — a spec deve refletir isso.

## Dimensionamento (AGENTS.md › Processo)
Cruza serviços (Orders → ERP) e introduz **contrato público novo** (evento `OrderItemCancelled`) → **Large**. Tier médio → não é Complex.
Multi-repo: este repo é dono do contrato → a spec vive aqui; o consumidor do ERP (critério 5) é feature separada no repo do ERP.

## Perguntas abertas para o PO
1. Item já separado fisicamente no estoque pode ser cancelado? (o Orders não sabe de separação; default proposto: sim — quem decide é o ERP ao consumir o evento)
2. Pedido em status Cancelado: tratar como não elegível (igual Faturado)? (default proposto: sim)

## Briefing para o Specify
- Objetivo: permitir cancelar um item de pedido ainda não faturado, recalculando o total e emitindo `OrderItemCancelled`.
- Critérios: os 4 do Orders (recalcular total · emitir evento com novo total · recusar se faturado sem alterar · idempotente). O 5º (ERP) fica fora desta spec.
- Fora de escopo: reembolso; cancelamento total; consumidor do ERP; API HTTP e catálogo AsyncAPI (não existem no exemplo).
- Nunca modificar: Payments; OrderCreated v1. Repos: orders-sample (dono do contrato). Tier: médio. Tamanho: **Large**.

**Pronto para `specify feature 001-cancelamento-parcial` (tlc-spec-driven). Não escrevi spec.**
