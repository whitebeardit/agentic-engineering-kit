# Aplicar evento ao cadastro com limiar de completude (ENR-042) Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for how to execute.

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Design**: `.specs/features/001-merge-por-unidade/design.md`
**Status**: Done — aguardando Verifier

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: `AGENTS.md` (seção "Testes", tabela por camada + gates), `docs/regras/enriquecimento.md`, `docs/adr/0003`, `docs/adr/0004`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Domain (`Cliente.aplicar`, specification, `merge.ts`, evento) | unit | 1:1 com cada cláusula EARS (ING-01..06); nome `RN_ENR_004_…`; edge cases listados na spec | `src/__tests__/unit/RN_ENR_004.merge-por-unidade.unit.test.ts` | `npm run test:regra` |
| Infrastructure (worker) + HTTP | integration (supertest, app real, memória) | orquestra, não decide (ING-07): carrega, delega, grava, publica um evento | `src/__tests__/integration/clientes.get.int.test.ts` | `npm run test:int` |
| Arquitetura (ADR-0003/0004) | dependency-cruiser em jest | regra de camada continua imposta; application/interfaces não importam `DomainRuleViolation` | `src/__tests__/unit/arquitetura.unit.test.ts` | `npm run test:arquitetura` |
| Docs (`docs/regras/enriquecimento.md`) | none | gate de tipos e lint | - | `npm run typecheck && npm run lint` |

## Gate Check Commands

> Generated from codebase - confirm before Execute.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After tasks with unit tests only | `npm run test:regra` |
| Full | After tasks with e2e/integration tests | `npm test` |
| Build | After phase completion or config/entity-only tasks | `npm run gate` |

---

## Execution Plan

Phases are ordered and run sequentially - each phase completes before the next begins, and tasks within a phase execute in order.

### Phase 1: Domínio

Regra escrita primeiro (skill `regras-de-negocio`), depois contrato, elegibilidade e o comportamento da entidade.

```
T1 → T2 → T3 → T4
```

### Phase 2: Worker e fechamento

Orquestração sem regra; regra marcada como verificada. (T5 depende de T4, último da fase 1.)

```
T4 → T5 → T6
```

---

## Task Breakdown

### T1: Registrar RN-ENR-004 em docs/regras/enriquecimento.md

**What**: Substituir o bloco "Pendente" por `RN-ENR-004 — Aplicar evento ao cadastro (merge por unidade)` em EARS, com Código/Teste previstos e `Confiança: inferred`, antes de codar (skill `regras-de-negocio`)
**Where**: `docs/regras/enriquecimento.md`
**Depends on**: None
**Reuses**: formato dos blocos RN-ENR-001..006
**Requirement**: ING-01, ING-02, ING-03, ING-04, ING-05, ING-06, ING-07
**Tools**:
- MCP: NONE
- Skill: `regras-de-negocio`
**Done when**:
- [x] Bloco com as cláusulas WHEN/IF da spec, `Código:` e `Teste:` apontando para os arquivos que T2–T5 criarão, `Confiança: inferred`
- [x] Build gate passes: `npm run gate` exit 0
**Tests**: none
**Gate**: build
**Status**: ✅ Done

---

### T2: Contrato — evento ClienteAtualizado v1 e porta de publicação

**What**: `src/domain/cliente/events/cliente-atualizado.v1.ts` (objeto imutável `type`/`version: 1`/`documento`/`versao`/`occurredAt` + `criarClienteAtualizadoV1`), `src/domain/cliente/messaging/publicador.port.ts`, `src/infrastructure/memory/publicador.memoria.ts`; `asyncapi.yaml` já descreve o v1 — conferir que bate
**Where**: `src/domain/cliente/events/`, `src/domain/cliente/messaging/`, `src/infrastructure/memory/`
**Depends on**: T1
**Reuses**: `FilaMemoria` como modelo de adaptador em memória; `rules/contracts.md`
**Requirement**: ING-07
**Tools**:
- MCP: NONE
**Done when**:
- [x] Evento e porta compilam; adaptador guarda os eventos e tem `limpar()`
- [x] Build gate passes: `npm run gate` exit 0
**Tests**: none (coberto por T4/T5)
**Gate**: build
**Status**: ✅ Done

---

### T3: Specification EventoElegivelParaMerge (ING-05)

**What**: `src/domain/cliente/specifications/evento-elegivel-para-merge.ts` com `estaSatisfeitaPor(cliente, evento, limiarN)`; testes `RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_recusar…` e `…_IF_origem_provedor_THEN_limiar_nao_se_aplica`, `…_WHEN_evento_traz_exatamente_N_SHALL_aceitar` (boundary)
**Where**: `src/domain/cliente/specifications/`, `src/__tests__/unit/RN_ENR_004.merge-por-unidade.unit.test.ts`
**Depends on**: T2
**Reuses**: `ehProvedor`, `achatar`, `Cliente.quantidadeDeCampos`
**Requirement**: ING-05
**Tools**:
- MCP: NONE
**Done when**:
- [x] 3 testes verdes com o ID da regra no nome
- [x] Quick gate passes: `npm run test:regra` exit 0
**Tests**: unit (3)
**Gate**: quick
**Status**: ✅ Done

---

### T4: Merge por unidade e Cliente.aplicar (ING-01..04, ING-06, ING-07 no domínio)

**What**: `src/domain/cliente/service/merge.ts` (`mesclar`), `Cliente.aplicar(evento, limiarN)` devolvendo `{ changed, eventos }` e lançando `DomainRuleViolation('RN-ENR-004','descartado-limiar')` quando a specification falha; remover `Cliente.substituir`; testes 1:1: criar (ING-01), preencher lacuna de evento antigo (ING-02), sobrescrever só mais novo + empate mantém (ING-03, 2 testes), provedor não sobrescreve cliente + provedor sobrescreve provedor antigo (ING-04, 2 testes), anti-eco (ING-06), um evento por mudança + `apto` como unidade (ING-07, 2 testes)
**Where**: `src/domain/cliente/service/merge.ts`, `src/domain/cliente/cliente.entity.ts`, `src/__tests__/unit/RN_ENR_004.merge-por-unidade.unit.test.ts`
**Depends on**: T3
**Reuses**: `Unidade`, `achatar`, `ehProvedor`, `criarClienteAtualizadoV1`
**Requirement**: ING-01, ING-02, ING-03, ING-04, ING-06, ING-07
**Tools**:
- MCP: NONE
**Done when**:
- [x] `substituir` não existe mais; os testes RN_ENR_005 que o usavam passam a usar `aplicar`
- [x] Quick gate passes: `npm run test:regra` exit 0 (≥ 12 testes RN_ENR_004)
**Tests**: unit (9 novos)
**Gate**: quick
**Status**: ✅ Done

---

### T5: Worker orquestra, grava e publica (ING-07)

**What**: `EventoIngestaoWorker` recebe `limiarN` e `PublicadorDeEventos`; `gravarComRetry` usa `aplicar`; `changed = false` → resultado `'sem-mudanca'`, registra processado, ack, sem gravar; `changed = true` → grava condicionalmente e publica cada evento; fábrica injeta `env.limiarN` e `PublicadorMemoria`; teste de integração: dois eventos → versão 2, um `ClienteAtualizado` por mudança, evento repetido → `sem-mudanca` sem evento
**Where**: `src/infrastructure/messaging/worker.ts`, `src/infrastructure/config/factories.ts`, `src/__tests__/integration/clientes.get.int.test.ts`
**Depends on**: T4
**Reuses**: `PublicadorMemoria`, `servicosDeTeste`
**Requirement**: ING-07
**Tools**:
- MCP: NONE
**Done when**:
- [x] Worker sem regra de negócio (só orquestra); teste de integração observa 2 eventos publicados e o `sem-mudanca`
- [x] Full gate passes: `npm test` exit 0
**Tests**: integration (2 novos)
**Gate**: full
**Status**: ✅ Done

---

### T6: Regra verificada, AGENTS.md e STATE

**What**: `docs/regras/enriquecimento.md` RN-ENR-004 → `Confiança: verified` com os nomes reais dos testes; `AGENTS.md` (contagem de testes; ordem das guardas sem "pendente"); `.specs/STATE.md` Handoff; `asyncapi.yaml` sem "pendente"
**Where**: `docs/regras/enriquecimento.md`, `AGENTS.md`, `.specs/STATE.md`, `src/contracts/asyncapi.yaml`
**Depends on**: T5
**Reuses**: —
**Requirement**: ING-01, ING-02, ING-03, ING-04, ING-05, ING-06, ING-07
**Tools**:
- MCP: NONE
**Done when**:
- [x] Bloco `verified`; contagens batem com `npm test`
- [x] Build gate passes: `npm run gate` exit 0
**Tests**: none
**Gate**: build
**Status**: ✅ Done
