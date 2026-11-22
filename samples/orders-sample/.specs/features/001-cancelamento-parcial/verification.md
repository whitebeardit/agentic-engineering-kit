# Cancelamento parcial de pedido (ORD-231) verification

**Verdict**: FAIL
**Proofs**: `proofs.md` at 1996e37
**Verifier**: independent sub-agent (author != verifier)

Lido: `spec.md`, `tasks.md` (Test Coverage Matrix e `## Checks`), `proofs.md`, o código em `src/Orders.Domain/` e
`src/Orders.Application/CancelOrderItem/` e os testes em `tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs`.
As provas não foram rodadas de novo na árvore real. Exemplos próprios e mutações rodaram numa cópia da pasta do
projeto fora da árvore (sem `bin/` e `obj/`), com o comando `Run regra` do `tasks.md`.

## Checks

| Check | Test | Holds |
| --- | --- | --- |
| C1 | `RN_ORD_012_CancelamentoParcialTests.cs` `RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_Aberto_SHALL_marcar_cancelado_e_recalcular_total` e `RN_ORD_012_WHEN_ultimo_item_e_cancelado_SHALL_recalcular_total_para_zero` | yes - afirma `a.Cancelled`, total 30,00 BRL e, cancelado o último item, total 0,00 BRL |
| C2 | `RN_ORD_012_CancelamentoParcialTests.cs` `RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_um_OrderItemCancelled_com_OrderId_ItemId_e_NewTotal` | yes - `Assert.Single` no evento, `OrderId`, `ItemId` e `NewTotal` 30,00 BRL |
| C3 | `RN_ORD_012_CancelamentoParcialTests.cs` `RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_RuleId_RN_ORD_012_sem_alterar_o_pedido` | yes - exceção, `RuleId`, item não cancelado, total 130,00 e `Events` vazio |
| C4 | `RN_ORD_012_CancelamentoParcialTests.cs` `RN_ORD_012_SHALL_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes` | yes - um único evento e total 30,00 depois de duas chamadas |
| C5 | `RN_ORD_012_CancelamentoParcialTests.cs` `RN_ORD_012_IF_item_nao_pertence_ao_pedido_THEN_SHALL_recusar_sem_alterar_o_pedido` | yes - exceção, `RuleId`, total 130,00 e `Events` vazio |
| C6 | `RN_ORD_012_CancelamentoParcialTests.cs` `RN_ORD_012_WHILE_pedido_Aberto_SHALL_ser_elegivel_para_cancelamento_de_item` e `RN_ORD_012_WHILE_pedido_Faturado_SHALL_nao_ser_elegivel_para_cancelamento_de_item` | no - o check afirma três estados (Aberto, Faturado, Cancelado) e os testes provam dois; `Cancelado` elegível deixa tudo verde (mutação M6) |
| C7 | `RN_ORD_012_CancelamentoParcialTests.cs` `RN_ORD_012_WHEN_handler_recebe_comando_SHALL_orquestrar_persistir_e_devolver_novo_total_e_eventos` | no - "persiste" não é provado: o teste salva o pedido antes de chamar o handler e o repositório em memória devolve a mesma instância, então o handler sem `SaveAsync` passa (mutação M7) |

## Findings

| Finding | Evidence | Fix | Closed |
| --- | --- | --- | --- |
| O handler pode deixar de persistir e nenhum teste falha (C7, CANC-07) | Mutação M7: removida a linha `await orders.SaveAsync(order, cancellationToken);` de `src/Orders.Application/CancelOrderItem/CancelOrderItemHandler.cs:18`; `Run regra` terminou com exit 0, 10 de 10 verdes. O teste (`RN_ORD_012_CancelamentoParcialTests.cs:139-147`) faz `repo.SaveAsync(order)` antes do handler e depois lê do mesmo `InMemoryOrderRepository`, que guarda a referência; o item aparece cancelado com ou sem o `SaveAsync` do handler | No teste do handler, afirmar que `SaveAsync` foi chamado com o pedido depois de `CancelItem`: um `IOrderRepository` de teste que registra a chamada (ou conta as gravações), ou um repositório que devolve cópia na leitura. A asserção `Assert.Single(result.Events)` também pode afirmar `ItemId` e `NewTotal` do evento devolvido | `961b0ae` - C7 (o teste usa um repositório que registra o `SaveAsync` e afirma o conteúdo do evento) |
| Pedido `Cancelado` elegível para cancelamento de item não derruba nenhum teste (C6, CANC-06) | Mutação M6: `candidate.Status == OrderStatus.Aberto` trocado por `candidate.Status != OrderStatus.Faturado` em `src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs:9`; `Run regra` terminou com exit 0, 10 de 10 verdes. Os dois testes do check cobrem Aberto e Faturado. A spec registra o caso como "coberto por construção" (Assumptions, `Confirmed: y`; Edge Cases), porque não existe `Order.Cancel()` neste repositório; o texto do C6, porém, afirma os três estados, e a spec põe em Success Criteria que as mutações do kit "morrem todas" | Uma das duas: (a) teste `RN_ORD_012_WHILE_pedido_Cancelado…` que leva o pedido a `Cancelado` sem código de produção novo (por exemplo, reflexão sobre o setter privado de `Status`) e afirma `IsSatisfiedBy == false`; ou (b) o autor da spec decide que o caso fica fora da prova e o texto do C6 e o Success Criteria passam a dizer isso, como critério novo, sem editar o aprovado | `961b0ae` - C6 (teste novo `…WHILE_pedido_Cancelado_SHALL_nao_ser_elegivel…`, estado posto por reflexão) |

## Own examples

Rodados na cópia como testes descartáveis (`VerifierExemplosTests.cs`, não commitado), todos verdes em 1996e37:

| Regra | Valor tentado | Resultado |
| --- | --- | --- |
| CANC-01 e CANC-02 | pedido com 1000 itens, preços em centavos (0,01 a 10,00) e quantidades de 1 a 7; cancelados os 500 de índice par, um por vez | a cada cancelamento o total e o `NewTotal` do evento novo batem com a soma dos não cancelados; 500 eventos ao fim |
| CANC-05 | id de um item que existe, mas em outro pedido; `Guid.Empty`; pedido sem nenhum item | recusa com `RN-ORD-012` nos três; nenhum dos dois pedidos muda total, itens ou eventos |
| CANC-04 com CANC-03 (a mais) | cancelamentos intercalados a, b, a, b, a; item já cancelado em pedido depois faturado | 2 eventos, `NewTotal` 30,00 e 0,00; no faturado, recusa com `RN-ORD-012` em vez do retorno idempotente silencioso |
| CANC-07 (a mais) | handler chamado duas vezes para o mesmo item; handler em pedido faturado | segunda chamada devolve 1 evento e total 30,00; no faturado, a `DomainRuleViolationException` do domínio sobe com `RN-ORD-012` |

Nenhuma regra quebrou nos exemplos.

## Mutations

Uma mutação por rodada, na cópia fora da árvore, a partir dos fontes de 1996e37. Comando de todas as rodadas:
`dotnet test Orders.slnx --filter "FullyQualifiedName~RN_ORD_012" --logger "console;verbosity=normal"`.
Depois da última rodada a cópia voltou aos fontes originais e o mesmo comando deu 10 de 10 verdes.

| # | Regra | O que foi estragado | Arquivo e linha | Teste que morreu |
| --- | --- | --- | --- | --- |
| M1 | CANC-01 | `if (!item.Cancelled)` virou `if (true)`: o total soma itens cancelados | `src/Orders.Domain/Order.cs:30` | morta - 5 vermelhos, entre eles `RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_Aberto_SHALL_marcar_cancelado_e_recalcular_total` e `RN_ORD_012_WHEN_ultimo_item_e_cancelado_SHALL_recalcular_total_para_zero` |
| M2 | CANC-05 | item inexistente devolve `return` em vez de lançar a violação | `src/Orders.Domain/Order.cs:70-71` | morta - `RN_ORD_012_IF_item_nao_pertence_ao_pedido_THEN_SHALL_recusar_sem_alterar_o_pedido` |
| M3 | CANC-03 | a condição de elegibilidade em `CancelItem` foi desligada (`if (false && …)`) | `src/Orders.Domain/Order.cs:65` | morta - `RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_RuleId_RN_ORD_012_sem_alterar_o_pedido` |
| M4 | CANC-04 | a guarda de idempotência `if (item.Cancelled)` virou `if (false)` | `src/Orders.Domain/Order.cs:73` | morta - `RN_ORD_012_SHALL_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes` |
| M5 | CANC-02 | ordem trocada: o evento é criado antes de `item.Cancel()`, com o total antigo em `NewTotal` | `src/Orders.Domain/Order.cs:78-79` | morta - `RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_um_OrderItemCancelled_com_OrderId_ItemId_e_NewTotal` |
| M6 | CANC-06 | `Status == OrderStatus.Aberto` virou `Status != OrderStatus.Faturado` (Cancelado passa a ser elegível) | `src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs:9` | **sobreviveu** - exit 0, 10 de 10 verdes; rodada duas vezes; ver Findings |
| M7 | CANC-07 | removida a chamada `await orders.SaveAsync(order, cancellationToken);` | `src/Orders.Application/CancelOrderItem/CancelOrderItemHandler.cs:18` | **sobreviveu** - exit 0, 10 de 10 verdes; rodada duas vezes; ver Findings |
| M8 | CANC-06 | comparação invertida: `Status == OrderStatus.Aberto` virou `Status != OrderStatus.Aberto` | `src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs:9` | morta - 8 vermelhos, entre eles `RN_ORD_012_WHILE_pedido_Aberto_SHALL_ser_elegivel_para_cancelamento_de_item` e `RN_ORD_012_WHILE_pedido_Faturado_SHALL_nao_ser_elegivel_para_cancelamento_de_item` |

## Not verified

- Linha "Arquitetura (ADR-0003/0004)" da Test Coverage Matrix: `ArchitectureTests` fica fora do filtro `RN_ORD_012`
  do `Run regra` e não aparece em `proofs.md`; nenhum check C1..C7 o seleciona. Não foi rodado aqui. A parte de C7 e
  do critério 7 que diz "sem conter regra de negócio" depende dele e fica sem prova nesta rodada.
- `dotnet build` e `dotnet format --verify-no-changes`: aceitos como estão em `proofs.md`, não rodados de novo.
- `docs/regras/pedidos.md` (bloco RN-ORD-012, terceiro Success Criteria): não conferido.
- Concorrência entre dois cancelamentos: fora do escopo pela spec; não tentada.
