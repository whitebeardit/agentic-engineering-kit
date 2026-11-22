# 001-cancelamento-parcial proofs

**HEAD**: 95019de
**Tree**: clean
**Shell**: /bin/sh
**Result**: 12 pass, 0 fail

| Check | Proof | Result |
| --- | --- | --- |
| C1 | `run regra / Passed RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_Aberto_SHALL_marcar_cancelado_e_recalcular_t` | pass |
| C1 | `run regra / Passed RN_ORD_012_WHEN_ultimo_item_e_cancelado_SHALL_recalcular_total_para_zero` | pass |
| C2 | `run regra / Passed RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_um_OrderItemCancelled_com_OrderId_ItemId_` | pass |
| C3 | `run regra / Passed RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_RuleId_RN_ORD_012_sem_alterar_o_pedido` | pass |
| C4 | `run regra / Passed RN_ORD_012_SHALL_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes` | pass |
| C5 | `run regra / Passed RN_ORD_012_IF_item_nao_pertence_ao_pedido_THEN_SHALL_recusar_sem_alterar_o_pedido` | pass |
| C6 | `run regra / Passed RN_ORD_012_WHILE_pedido_Aberto_SHALL_ser_elegivel_para_cancelamento_de_item` | pass |
| C6 | `run regra / Passed RN_ORD_012_WHILE_pedido_Faturado_SHALL_nao_ser_elegivel_para_cancelamento_de_item` | pass |
| C6 | `run regra / Passed RN_ORD_012_WHILE_pedido_Cancelado_SHALL_nao_ser_elegivel_para_cancelamento_de_item` | pass |
| C7 | `run regra / Passed RN_ORD_012_WHEN_handler_recebe_comando_SHALL_orquestrar_persistir_e_devolver_novo_total_e_e` | pass |
| Build | `dotnet build Orders.slnx` | pass |
| Build | `dotnet format Orders.slnx --verify-no-changes` | pass |

## Output

`Run regra` - exit 0

```
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_WHEN_handler_recebe_comando_SHALL_orquestrar_persistir_e_devolver_novo_total_e_eventos [9 ms]
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_WHILE_pedido_Aberto_SHALL_ser_elegivel_para_cancelamento_de_item [< 1 ms]
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_IF_item_nao_pertence_ao_pedido_THEN_SHALL_recusar_sem_alterar_o_pedido [3 ms]
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_WHEN_cliente_cancela_item_de_pedido_Aberto_SHALL_marcar_cancelado_e_recalcular_total [< 1 ms]
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_IF_pedido_inexistente_THEN_handler_SHALL_lancar_KeyNotFoundException [4 ms]
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_IF_pedido_faturado_THEN_SHALL_recusar_com_RuleId_RN_ORD_012_sem_alterar_o_pedido [< 1 ms]
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_WHEN_cliente_cancela_item_SHALL_emitir_um_OrderItemCancelled_com_OrderId_ItemId_e_NewTotal [< 1 ms]
[xUnit.net 00:00:00.37]   Finished:    Orders.Tests
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_SHALL_ser_idempotente_ao_cancelar_o_mesmo_item_duas_vezes [< 1 ms]
  Passed Orders.Tests.RN_ORD_012_CancelamentoParcialTests.RN_ORD_012_WHILE_pedido_Faturado_SHALL_nao_ser_elegivel_para_cancelamento_de_item [< 1 ms]

Test Run Successful.
Total tests: 11
     Passed: 11
 Total time: 1.0247 Seconds
```
