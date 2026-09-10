# Definition of Ready — o card só entra se…

Um card de uma linha entregue ao agente é o erro mais comum. Antes de `card-intake` (e do Specify do tlc-spec-driven), o card tem:

| Campo | Quem preenche | Exemplo | Sem isso… |
|---|---|---|---|
| **Objetivo** (o quê + por quê) | PO | "Permitir cancelamento parcial de pedido para reduzir estornos manuais" | o agente otimiza a coisa errada |
| **Critérios de aceite em EARS** | PO | `WHEN o cliente cancela um item THE SYSTEM SHALL recalcular o total e emitir evento OrderItemCancelled` | sem resultado observável não há critério verificável |
| **Escopo: dentro / fora** | PO | fora: reembolso automático | o agente "aproveita" e amplia |
| **Sistemas afetados** | PO + tech lead | Orders (micro), ERP legado (estoque) | ordem de implementação errada |
| **Caminhos prováveis** | agente (`card-intake`), marcado `inferido` | `src/Orders/Cancel/*`, `Erp/Estoque/Reserva.cs` | horas de navegação |
| **Nunca modificar** | PO + tech lead | schema de `Payments`, contrato v1 de `OrderCreated` | quebra de contrato silenciosa |
| **Tier de risco** | tech lead (PO confirma) | médio (não toca pagamento nem dados pessoais) | revisão humana no lugar errado |
| **Como validar com o PO** | PO | UAT no ambiente X com pedido de teste Y | "pronto" sem prova |

Formatos EARS: `WHEN <gatilho> THE SYSTEM SHALL …` · `WHILE <estado> …` · `IF <condição> THEN …` · `WHERE <feature> …`.
Para bugfix, acrescente o **comportamento que não muda**: `THE SYSTEM SHALL CONTINUE TO …`.

Campo do **PO** ausente → o card volta com as lacunas listadas. Campo do **agente** ausente (caminhos prováveis) → o
agente preenche, marca `inferido` e lista no briefing como "a confirmar"; o PO confirma antes do Specify. O agente nunca
preenche campo do PO.
