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

- **Feature**: 001-merge-por-unidade / `.specs/features/001-merge-por-unidade`
- **Phase / Task**: Concluída — migrada para o tlc 4.1.0 em 2026-11-22: `check_proofs.py` 17/17 em `1f534ae` e `validate_verification.py` com 0 erros. O Verifier deu FAIL nas duas rodadas (13 mutações com 4 vivas; depois 18 com 1 viva) e os 7 achados estão fechados por commit: 6 de teste e 1 de regra, o ING-08, decidido pelo PO (T7). Antes, na 3.3.0: Verifier PASS (`validation.md`: 7/7 ACs, gate 44/44, sensor 3/3 mortos)
- **Completed**: T1, T2, T3, T4, T5, T6, T7
- **In-progress** (file:line): none
- **Lições**: cinco candidatas (L-002 a L-006), gravadas por `lessons.py` em 2026-11-22 a partir dos sete achados do `verification.md`; a L-001 de agosto saiu do arquivo na mesma escrita, por ter mais de 45 dias sem reincidir
- **Next step**: próxima feature candidata: 002 — consulta ao provedor quando o documento não existe (hybrid miss: 200/202/404 com cache negativo), ou consumidor do `ClienteAtualizado` no repo do CRM (fora deste repo)
- **Blockers**: none
- **Uncommitted files**: none após o commit de validação
- **Branch**: kit/v0.3 → main (kit--v0.3.0)
