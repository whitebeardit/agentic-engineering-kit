# Definition of Ready — o card só entra se…

Um card de uma linha entregue ao agente é o erro mais comum. Antes de `jira-intake`, o card tem:

| Campo | Exemplo | Sem isso… |
|---|---|---|
| **Objetivo** (o quê + por quê) | "Permitir cancelamento parcial de pedido para reduzir estornos manuais" | o agente otimiza a coisa errada |
| **Critérios de aceite em EARS** | `WHEN o cliente cancela um item THE SYSTEM SHALL recalcular o total e emitir evento OrderItemCancelled` | não há teste possível |
| **Escopo: dentro / fora** | fora: reembolso automático | o agente "aproveita" e amplia |
| **Sistemas afetados** | Orders (micro), ERP legado (estoque) | ordem de implementação errada |
| **Caminhos prováveis** | `src/Orders/Cancel/*`, `Erp/Estoque/Reserva.cs` | horas de navegação |
| **Nunca modificar** | schema de `Payments`, contrato v1 de `OrderCreated` | quebra de contrato silenciosa |
| **Tier de risco** | médio (não toca pagamento nem dados pessoais) | revisão humana no lugar errado |
| **Como validar com o PO** | UAT no ambiente X com pedido de teste Y | "pronto" sem prova |

Formatos EARS: `WHEN <gatilho> THE SYSTEM SHALL …` · `WHILE <estado> …` · `IF <condição> THEN …` · `WHERE <feature> …`.
Para bugfix, acrescente o **comportamento que não muda**: `THE SYSTEM SHALL CONTINUE TO …`.

Card sem DoR volta para o PO com as lacunas listadas — não é o agente que preenche.
