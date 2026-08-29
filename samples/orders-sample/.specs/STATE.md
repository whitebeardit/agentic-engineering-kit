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
- **Phase / Task**: Tasks aprovadas; Execute não iniciado
- **Completed**: none
- **In-progress** (file:line): none
- **Next step**: Executar T1 (bloco RN-ORD-012 em docs/regras/pedidos.md) com gate build
- **Blockers**: none
- **Uncommitted files**: .specs/** (spec, tasks, STATE, lessons)
- **Branch**: tlc/001
