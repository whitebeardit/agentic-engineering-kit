# STATE

## Decisions

### AD-001
- **Decision**: Eventos de domínio públicos são `record` imutáveis com `OccurredAt`, definidos em `Orders.Domain/Events`; alterar campo existente = nova versão do evento, nunca mudança in-place.
- **Reason**: O evento é contrato consumido por outro serviço (ERP); compatibilidade retroativa é regra do kit (`rules/contracts.md`).
- **Trade-off**: Campos novos exigem versionamento explícito mesmo quando "só mais um campo".
- **Scope**: `src/Orders.Domain/Events/**`, qualquer feature que publique evento
- **Date**: 2026-08-29
- **Status**: active

### AD-002
- **Decision**: Elegibilidade de operações sobre o pedido é expressa por `ISpecification<Order>` no domínio (ex.: `PedidoElegivelParaCancelamento`), reutilizável por comandos e consultas; nunca por `if` de status em Application.
- **Reason**: ADR-0003/ADR-0004 (regra vive no domínio; Application só orquestra) — imposto por `ArchitectureTests`.
- **Trade-off**: Uma classe a mais por predicado.
- **Scope**: `src/Orders.Domain/Specifications/**`, handlers em `Orders.Application`
- **Date**: 2026-08-29
- **Status**: active

## Handoff

- **Feature**: 001-cancelamento-parcial / `.specs/features/001-cancelamento-parcial`
- **Phase / Task**: Done — Verifier PASS (validation.md: 7/7 ACs, gate 14/14, sensor 3/3 mortos); validate_state.py exit 0
- **Completed**: T1, T2, T3, T4, T5, T6
- **In-progress** (file:line): none
- **Next step**: Merge de tlc/001 em main; próxima feature: 002 — consumidor do evento no repo do ERP (fora deste repo), ou `Order.Cancel()` com o teste WHILE_pedido_Cancelado
- **Blockers**: none
- **Uncommitted files**: none após o commit de validação
- **Branch**: tlc/001
