# STATE

## Decisions

### AD-001

- **Decision**: Eventos publicados são objetos imutáveis com `type`, `version` e `occurredAt`, definidos em `src/domain/cliente/events/` e catalogados em `src/contracts/asyncapi.yaml`; alterar campo existente = nova versão (`cliente-atualizado.v2.ts`), nunca edição in-place.
- **Reason**: O evento é contrato consumido por outro serviço (CRM); compatibilidade retroativa é regra do kit (`rules/contracts.md`).
- **Trade-off**: Campos novos exigem versionamento explícito mesmo quando "só mais um campo".
- **Scope**: `src/domain/cliente/events/**`, `src/contracts/asyncapi.yaml`, qualquer feature que publique evento
- **Date**: 2026-08-30
- **Status**: active

### AD-002

- **Decision**: Elegibilidade de um evento para alterar o cadastro é expressa por uma specification no domínio (`src/domain/cliente/specifications/`), reutilizável por entidade e handler; o handler só orquestra.
- **Reason**: ADR-0003/ADR-0004 (regra vive no domínio; Application só orquestra) — imposto pelo teste de arquitetura.
- **Trade-off**: Um arquivo a mais por predicado.
- **Scope**: `src/domain/cliente/specifications/**`, `src/application/**`
- **Date**: 2026-08-30
- **Status**: active

### AD-003

- **Decision**: Persistência e fila são adaptadores em memória (`src/infrastructure/memory/`) atrás das portas do domínio, com a mesma semântica que o livro ensina: gravação condicional por versão, FIFO por grupo com deduplicação, redelivery e DLQ após 5 recebimentos.
- **Reason**: O laboratório roda com `npm install && npm test`, sem nuvem nem contêiner; o serviço real usa banco e fila gerenciados com as mesmas quatro propriedades.
- **Trade-off**: Nada persiste entre execuções; concorrência real entre processos não é exercitada.
- **Scope**: `src/infrastructure/memory/**`, `src/infrastructure/config/factories.ts`
- **Date**: 2026-08-30
- **Status**: active

## Handoff

- **Feature**: nenhuma em curso — próximo card: `docs/cards/ENR-042.md` (RN-ENR-004, feature `001-merge-por-unidade`)
- **Phase / Task**: esqueleto pronto (guardas RN-ENR-001/002/003, gravação RN-ENR-005, contrato, worker, legado + characterization, arquitetura)
- **Completed**: —
- **In-progress** (file:line): none
- **Next step**: `card-intake` do ENR-042 (briefing já em `docs/cards/`) → `specify feature 001-merge-por-unidade`
- **Blockers**: none
- **Uncommitted files**: none
- **Branch**: main
