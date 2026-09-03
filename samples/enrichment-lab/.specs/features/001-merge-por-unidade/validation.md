# Aplicar evento ao cadastro com limiar de completude (ENR-042) Validation

**Date**: 2026-08-30
**Spec**: `.specs/features/001-merge-por-unidade/spec.md`
**Diff range**: `b08fe3f..c7de133` (branch `kit/v0.3`; commits `316c34a` T1, `2fb99d0` T2, `2cb0b89` T3, `f30876f` T4, `4ad0de0` T5, `cefd3c8`+`c7de133` T6)
**Verifier**: independent sub-agent (author ≠ verifier)
**Ambiente**: Node 22.22.2, `npm run gate` = `tsc --noEmit && eslint . && jest --ci`

Legenda de caminhos: `E` = `src/domain/cliente/cliente.entity.ts` · `M` = `src/domain/cliente/service/merge.ts` · `S` = `src/domain/cliente/specifications/evento-elegivel-para-merge.ts` · `W` = `src/infrastructure/messaging/worker.ts` · `TU` = `src/__tests__/unit/RN_ENR_004.merge-por-unidade.unit.test.ts` · `TI` = `src/__tests__/integration/clientes.get.int.test.ts`. Todos os `file:line` foram re-derivados pelo Verifier lendo os arquivos no HEAD do diff (`c7de133`), não copiados de tasks.md.

**Nota sobre HEAD durante a verificação**: enquanto este Verifier rodava, outro commit (`74c7c74`, "feat(kit): v0.3 — perfis node-ts e dotnet, hooks…") entrou no branch `kit/v0.3`. É trabalho concorrente de outro ator, inteiramente em ferramentas do kit (`hooks/`, `templates/`, `agents/`, `node-ts/`, `README.md`, `CHANGELOG.md`) — `git diff --stat HEAD -- samples/enrichment-lab/src samples/enrichment-lab/docs samples/enrichment-lab/.specs samples/enrichment-lab/AGENTS.md` está vazio, confirmando que nada deste commit toca a feature. Esta validação usa `c7de133` (o commit de T6) como referência de código.

---

## Task Completion

| Task                                                    | Status              | Commit                | Notes                                                                                                                                                                        |
| ------------------------------------------------------- | ------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1 — RN-ENR-004 em `docs/regras/enriquecimento.md`      | ✅ Done             | `316c34a`             | bloco EARS + `Confiança: inferred` antes de codar                                                                                                                            |
| T2 — evento `ClienteAtualizadoV1` + porta de publicação | ✅ Done             | `2fb99d0`             | `src/domain/cliente/events/cliente-atualizado.v1.ts`, `src/domain/cliente/messaging/publicador.port.ts`, `src/infrastructure/memory/publicador.memoria.ts`                   |
| T3 — specification `EventoElegivelParaMerge`            | ✅ Done             | `2cb0b89`             | 3 testes do limiar                                                                                                                                                           |
| T4 — `merge.ts` + `Cliente.aplicar`                     | ✅ Done             | `f30876f`             | `substituir` removido; 10 testes novos                                                                                                                                       |
| T5 — worker orquestra, grava e publica                  | ✅ Done             | `4ad0de0`             | 2 testes de integração novos                                                                                                                                                 |
| T6 — regra `verified`, AGENTS.md, STATE                 | ✅ Done (2 commits) | `cefd3c8` + `c7de133` | 1º commit só ajustou `tasks.md`; 2º completou `STATE.md`/`AGENTS.md`/`docs/regras`/`asyncapi.yaml`. Não é um commit atômico único por task (deviation menor, não bloqueante) |

Todas as 6 tarefas estão marcadas `✅ Done` em `tasks.md`, com `Done when` totalmente marcado (`[x]`) e commit correspondente em `git log --oneline b08fe3f..c7de133`. Nenhuma tarefa bloqueada ou parcial.

---

## Spec-Anchored Acceptance Criteria

### P1: Aplicar o evento ao cadastro sem apagar informação boa ⭐ MVP

Fixture comum: `eventoValido()` (`src/__tests__/helpers/eventos.ts:9-25`) — 7 unidades (`cadastro.nome`, `cadastro.canalEntrada`, `contato.email`, `contato.telefone`, `endereco.cep`, `endereco.cidade`, `endereco.uf`), origem `cliente:app`. `clienteComUnidades(n)` (`src/__tests__/helpers/clientes.ts:6-16`) gera cadastro sintético com `n` unidades `campo.ci`.

| Criterion (WHEN X THEN Y)                                                                                                   | Spec-defined outcome                                                                                                                                                 | `file:line` + assertion                                                                                                                                                                                                                                                                                                                                                                                                                                                | Result                                        |
| --------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| ING-01 · WHEN documento sem cadastro THEN criar com unidades do evento (instante/origem) e versão 1                         | `changed === true`; 7 unidades anotadas com `instante`/`origem` do evento; versão da gravação = 1                                                                    | `TU:53-63` - `expect(r.changed).toBe(true)` (`TU:56`), `expect(c.quantidadeDeCampos).toBe(7)` (`TU:57`), `expect(unidade(c,'contato.email')).toEqual({valor:'ana@exemplo.test',instante:T12,origem:'cliente:app'})` (`TU:58-62`) · versão 1 confirmada por integração `TI:15-22` (`expect(r.headers.etag).toBe('"v1"')`) · código `E:49-59`                                                                                                                            | ✅ PASS                                       |
| ING-02 · WHEN evento traz unidade ausente THEN preencher mesmo que `updatedAt` anterior                                     | `changed === true`; unidade nova presente mesmo vinda de evento mais antigo                                                                                          | `TU:64-74` - `expect(r.changed).toBe(true)` (`TU:71`), `expect(unidade(c,'endereco.cep')?.valor).toBe('01001000')` (`TU:72`), unidade antiga preservada (`TU:73`) · código `M:30-39` (ausente entra sem checar instante)                                                                                                                                                                                                                                               | ✅ PASS                                       |
| ING-03 · WHEN unidade já existe THEN sobrescreve só se estritamente mais novo; empate/anterior mantém                       | overwrite com `T13`; manutenção do valor `'Ana'` em empate (`T12`) e anterior (`T11`)                                                                                | `TU:75-88` - `expect(unidade(c,'cadastro.nome')).toEqual({valor:'Ana Maria',instante:T13,origem:'cliente:app'})` (`TU:83-87`) · `TU:89-105` - `expect(...changed).toBe(false)` (`TU:97`, `TU:103`), `expect(unidade(c,'cadastro.nome')?.valor).toBe('Ana')` (`TU:104`) · código `M:33` (`>` estrito)                                                                                                                                                                   | ✅ PASS (sensor MUT-B confirma discriminação) |
| ING-04 · IF origem `provedor:*` THEN só preenche lacuna ou sobrescreve unidade também `provedor:*`                          | provedor não sobrescreve `cliente:app` mesmo mais novo (`changed=false`, valor mantido); provedor sobrescreve provedor mais antigo                                   | `TU:106-116` - `expect(c.aplicar(provedor,N).changed).toBe(false)` (`TU:114`), `expect(unidade(c,'cadastro.nome')?.valor).toBe('Ana')` (`TU:115`) · `TU:117-136` - `expect(unidade(c,'endereco.uf')).toEqual({valor:'RJ',instante:T13,origem:'provedor:outro'})` (`TU:131-135`) · código `M:34` (`podeSobrescrever = maisNovo && (!provedor \|\| ehProvedor(atual.origem))`)                                                                                           | ✅ PASS                                       |
| ING-05 · IF cadastro com N+ unidades e evento traz menos de N THEN recusa `RN-ENR-004`/`descartado-limiar`, exceto provedor | `{ok:false, motivo:'descartado-limiar'}` a nível de specification; `DomainRuleViolation` com `ruleId` implícito `RN-ENR-004` a nível de entidade, sem avançar versão | `TU:12-19` - `expect(r).toEqual({ok:false,motivo:'descartado-limiar'})` (`TU:18`) · `TU:20-25` - provedor `{ok:true}` (`TU:24`) · `TU:137-145` - `expect(() => c.aplicar(...)).toThrow(DomainRuleViolation)` (`TU:140-142`), `expect(c.versao).toBe(antes)` (`TU:143`) · código `S:17-22`, `E:50-51` (`throw new DomainRuleViolation('RN-ENR-004', elegivel.motivo)`)                                                                                                  | ✅ PASS (sensor MUT-A confirma discriminação) |
| ING-06 · IF estado resultante idêntico THEN `changed=false`, não grava, não avança versão, não emite                        | `{changed:false, eventos:[]}`; anotação (`instante`) não renovada                                                                                                    | `TU:146-152` - `expect(r).toEqual({changed:false,eventos:[]})` (`TU:150`), `expect(unidade(c,'cadastro.nome')?.instante).toBe(T12)` (`TU:151`) · código `E:52-53` (`if (!changed) return {changed:false, eventos:[]}`), `M:35` (`igual(atual.valor, valor)` não conta como mudança)                                                                                                                                                                                    | ✅ PASS (sensor MUT-C confirma discriminação) |
| ING-07 · WHEN cadastro muda THEN emite exatamente um `ClienteAtualizado` v1; worker só orquestra                            | 1 evento com `type/version/documento/versao`; `apto` tratado como unidade; worker sem `if` de regra                                                                  | `TU:153-163` - `expect(r.eventos).toHaveLength(1)` (`TU:156`), `toMatchObject({type:'ClienteAtualizado',version:1,documento:CPF_VALIDO,versao:4})` (`TU:157-162`) · `TU:164-171` - `apto` muda sozinho e emite (`TU:168-170`) · integração `TI:41-53` - `s.publicador.publicados.map(...)` = `[[CPF,1],[CNPJ,1],[CNPJ,2]]` (`TI:49-53`), `sem-mudanca` no repost (`TI:54-57`) · leitura `W:90-114` (`gravarComRetry`: sem `if` de negócio, delega a `cliente.aplicar`) | ✅ PASS                                       |

**Independent Test da spec** (`spec.md:83`): evento A (12:00, doc novo) → versão 1 + 1 evento (`TI:15-22`); evento B (11:00, e-mail diferente + cep novo) → e-mail mantido, cep preenchido, versão 2, 1 evento (`TI:31-53`, ramo `maisAntigoComCep`); evento C de provedor (13:00, nome diferente) → nome mantido, `changed=false` (`TU:106-116`, equivalente unitário); evento D com 1 campo contra cadastro N≥11 → recusa `RN-ENR-004` (`TU:12-19`, `TU:137-145`).

**Status**: ✅ All 7/7 ACs covered com `file:line` e valor exato da spec. 0 spec-precision gaps.

---

## Discrimination Sensor

Executado em worktree git isolado (`git worktree add <scratch>/wt-sensor HEAD`, detached em `c7de133`), uma mutação por vez, revertida com `git checkout -- <arquivo>` dentro do worktree e confirmada limpa antes do `git worktree remove --force`. `node_modules` foi symlinkado no worktree (não copiado; removido antes da limpeza). Comando: `npm run test:regra` (`jest --ci -t 'RN_ENR_'`, 29 testes). `git stash` não foi usado.

| Mutation | File:line                                                            | Description                                                                               | Killed?                                                                                                                                                                                                            |
| -------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A        | `src/domain/cliente/specifications/evento-elegivel-para-merge.ts:19` | Limiar invertido: `trazidas < limiarN` → `trazidas > limiarN`                             | ✅ Killed — 2 testes falharam: `RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_recusar` (`TU:12`) e `RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_lancar` (`TU:137`)             |
| B        | `src/domain/cliente/service/merge.ts:33`                             | Empate sobrescreve: `instante(evento.updatedAt) > instante(atual.instante)` → `>=`        | ✅ Killed — 1 teste falhou: `RN_ENR_004_IF_empate_ou_evento_anterior_THEN_SHALL_manter_o_gravado` (`TU:89`), esperava `changed=false` e recebeu `true`                                                             |
| C        | `src/domain/cliente/cliente.entity.ts:53`                            | Anti-eco removido: linha `if (!changed) return { changed: false, eventos: [] };` deletada | ✅ Killed — 3 testes falharam, incluindo diretamente `RN_ENR_004_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir` (`TU:146`, esperava `{changed:false,eventos:[]}` e recebeu `changed:true` + 1 evento espúrio) |

**Sensor depth**: lightweight (3 mutações comportamentais no código novo de maior risco: limiar, empate, anti-eco)
**Result**: 3/3 killed - PASS ✅

**Isolamento**: baseline `git status --porcelain` na raiz do repo antes do sensor = vazio. Após cada reversão, o worktree ficou limpo (só o symlink `node_modules`, removido antes da remoção do worktree). Prova de não-vazamento: `git diff --stat HEAD -- samples/enrichment-lab/src samples/enrichment-lab/docs samples/enrichment-lab/.specs samples/enrichment-lab/AGENTS.md` vazio nas duas checagens (após o sensor e após a checagem de baseline "antes da feature" em `b08fe3f`) — os três arquivos mutados são idênticos ao HEAD. Durante a janela de verificação, um commit concorrente de outro ator (`74c7c74`, ferramentas do kit) entrou no branch, mas fora do escopo desta feature (ver nota no topo); o Verifier não reverteu esse trabalho alheio. Sensor considerado válido.

---

## Interactive UAT Results (if performed)

Não realizado — feature backend-only (domínio + worker in-memory, sem UI); checagens automatizadas são suficientes (`validate.md` §3).

---

## Code Quality

Arquivos do diff analisados (21, `b08fe3f..c7de133`): `cliente.entity.ts` (+57/-…), `events/cliente-atualizado.v1.ts` (novo, +25), `messaging/publicador.port.ts` (novo, +6), `service/merge.ts` (novo, +41), `specifications/evento-elegivel-para-merge.ts` (novo, +24), `infrastructure/messaging/worker.ts` (+27), `infrastructure/config/factories.ts` (+13/-…), `infrastructure/memory/publicador.memoria.ts` (novo, +15), `infrastructure/memory/cliente.memoria.ts` (+10/-…), testes, `docs/regras/enriquecimento.md`, `AGENTS.md`, `asyncapi.yaml`, `.specs/**`.

| Principle                                                  | Status                                                                                                                                                                                                                                                                                             |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Minimum code (no features beyond what was asked)           | ✅ — nenhum campo extra no evento além de `type/version/documento/versao/occurredAt`; nenhuma fila de saída real (porta + memória, conforme design)                                                                                                                                                |
| No abstractions for single-use code                        | ✅ — `EventoElegivelParaMerge` e `merge.ts` são as abstrações previstas em design.md, não extras                                                                                                                                                                                                   |
| No unnecessary flexibility                                 | ✅ — `criarClienteAtualizadoV1` aceita `agora: Date` opcional só para teste, sem clock injetável (padrão in-memory do laboratório)                                                                                                                                                                 |
| Surgical changes (only files required)                     | ✅ — `cliente.memoria.ts` (+10) e `factories.ts` (+13) só ganharam o publicador/limiarN; sem edição fora do escopo                                                                                                                                                                                 |
| Didn't "improve" unrelated code                            | ✅ — `guardas.ts`, `documento.ts`, RN-ENR-001/002/003/006 intactos (fora do diff)                                                                                                                                                                                                                  |
| Matches patterns                                           | ✅ — `DomainRuleViolation('RN-ENR-004', motivo)` (`E:51`) igual ao padrão das outras guardas em `guardas.ts`; testes com `RN_ENR_004_…`                                                                                                                                                            |
| Would senior engineer approve?                             | ✅ — worker só orquestra (`W:90-114`, sem `if` de negócio); `apto` tratado uniformemente como unidade (`E:63-65`, `M:27`); documento mascarado em todo log (`W:51` `mascarar(evento.documento)`, aplica a qualquer `DomainRuleViolation` capturada, inclusive RN-ENR-004, `W:69-79`)               |
| Tests map to ACs and are non-shallow (spot-check ING-05)   | ✅ — `TU:137-145` assere exceção + versão inalterada + `quantidadeDeCampos`, não só "lançou"                                                                                                                                                                                                       |
| Spec-anchored outcome check (asserted values match spec)   | ✅ — `instante`/`origem` exatos, `versao:4`, `motivo:'descartado-limiar'`, `changed`/`eventos`                                                                                                                                                                                                     |
| Per-layer Coverage Expectation met                         | ✅ — Domain 1:1 (13 testes RN_ENR_004: 3 limiar + 10 merge); Integration 2 novos (`TI`) cobrindo orquestração e publicação; Arquitetura 3 testes verdes (`npm run test:arquitetura`)                                                                                                               |
| Every test maps to a spec requirement — no unclaimed tests | ✅ — 13 testes RN_ENR_004 mapeiam 1:1 a ING-01..07 + 4 edge cases + boundary de ING-05                                                                                                                                                                                                             |
| Documented guidelines followed                             | ✅ — `AGENTS.md` § Testes (nome `RN_ENR_<n>_…`, camadas e comandos); `docs/regras/enriquecimento.md` (ordem fixa das guardas, `Confiança: verified`); ADR-0003/0004 impostos por `arquitetura.unit.test.ts` (3/3 verde); `Cliente.substituir` não existe mais (`grep -rn "substituir" src/` vazio) |

---

## Edge Cases

- [x] WHEN evento e unidade gravada têm o mesmo instante THEN mantém o gravado (boundary ING-03): `TU:89-97` (`T12` vs `T12`) — `changed=false`, valor `'Ana'` mantido
- [x] WHEN cadastro tem exatamente N unidades e evento traz exatamente N THEN aceita (boundary ING-05): `TU:26-40` — `comN` (N campos) contra `clienteComUnidades(N)` aceito (`TU:34-36`)
- [x] IF evento de provedor e unidade gravada de provedor com instante mais antigo THEN sobrescreve: `TU:117-136` — `p2` (provedor, T13) sobrescreve `p1` (provedor, T12) em `endereco.uf`
- [x] IF evento não traz unidade nova/mais nova mas traz `apto` diferente THEN trata `apto` como unidade e emite: `TU:164-171` — `changed=true`, `c.apto === true`, `snapshot()` não expõe `apto` (`E:72-76`)

---

## Gate Check

- **Gate command**: `npm run gate` = `tsc --noEmit && eslint . && jest --ci` (build gate, `tasks.md` › Gate Check Commands)
- **Exit codes**: `tsc --noEmit` = 0; `eslint .` = 0 erros (6 warnings em `legacy/calcula-apto.js` — rampa esperada, nunca erro, `AGENTS.md` linha 9/22); `jest --ci` = 0
- **Result**: Test Suites: 9 passed, 9 total. **Tests: 44 passed, 44 total.** Snapshots: 1 passed, 1 total.
- **Test count before feature** (`b08fe3f`, checado em worktree isolado): 30 (8 suites)
- **Test count after feature** (`c7de133`): 44 (9 suites)
- **Delta**: +14 (3 de T3 + 9 de T4 + 2 de T5 — bate com o previsto em `tasks.md`)
- **Test integrity**: nenhum teste removido ou enfraquecido; `RN_ENR_005.gravacao-condicional.unit.test.ts` só trocou `substituir` por `aplicar` (mesmo número de asserts, `+7/-` linhas de adaptação de chamada); `__snapshots__/` inalterado (Snapshots 1 passed)
- **Skipped tests**: none
- **Failures**: none
- **Arquitetura** (`npm run test:arquitetura`): 3/3 verde (`adr-0003-domain-puro`, `adr-0003-application-sem-infra`, `adr-0004-violation-so-no-domain` sem violações)
- **Integração** (`npm run test:int`): 2 suites, 11/11 verde

---

## Fix Plans (if issues found)

Nenhum gap bloqueante. Sem fix tasks.

**Observações não bloqueantes** (para o orquestrador, não exigem re-verificação):

1. T6 foi fechada em 2 commits (`cefd3c8` + `c7de133`) em vez de 1 commit atômico — o primeiro só reajustou `tasks.md`, o segundo completou `docs/regras`, `AGENTS.md`, `STATE.md` e `asyncapi.yaml`. Não afeta o resultado (ambos estão no diff range verificado), mas é um desvio da regra "um commit atômico por task" do `tlc-spec-driven`.
2. Durante esta verificação, um commit concorrente de outro ator (`74c7c74`) entrou no branch `kit/v0.3` — inteiramente em ferramentas do kit, fora do escopo de `samples/enrichment-lab`. Não bloqueante; registrado para rastreabilidade da janela de verificação (ver nota no topo do relatório).

---

## Requirement Traceability Update

Update spec.md requirement statuses:

| Requirement | Previous Status | New Status  |
| ----------- | --------------- | ----------- |
| ING-01      | In Tasks        | ✅ Verified |
| ING-02      | In Tasks        | ✅ Verified |
| ING-03      | In Tasks        | ✅ Verified |
| ING-04      | In Tasks        | ✅ Verified |
| ING-05      | In Tasks        | ✅ Verified |
| ING-06      | In Tasks        | ✅ Verified |
| ING-07      | In Tasks        | ✅ Verified |

Aplicado em `spec.md` › Requirement Traceability (Phase → Done, Status → ✅ Verified). Nenhum outro trecho da spec foi alterado.

---

## Summary

**Overall**: ✅ Ready — PASS

**Spec-anchored check**: 7/7 ACs matched spec outcome · 0 spec-precision gaps
**Sensor**: 3/3 mutations killed
**Gate**: 44 passed, 0 failed, 0 skipped (`tsc` exit 0, `eslint` exit 0, `jest --ci` exit 0)

**What works**: criação com versão 1 e unidades anotadas (`instante`/`origem`), preenchimento de lacuna mesmo de evento antigo, sobrescrita só estritamente mais nova com empate mantendo o gravado, provedor nunca sobrescreve cliente (só provedor sobre provedor), recusa por limiar com `RN-ENR-004` sem alterar nada, anti-eco (`changed=false`, nada grava/avança/emite), exatamente um `ClienteAtualizado` v1 por mudança real, worker que só orquestra (arquitetura 3/3 verde), `apto` tratado como unidade, documento mascarado em log.

**Issues found**: nenhum bloqueante. Notas: T6 em 2 commits (não atômico); commit concorrente de outro ator durante a janela de verificação, fora do escopo da feature.

**Next steps**: orquestrador fecha a feature (`validate_state.py` abaixo), commita `validation.md` + `spec.md` e atualiza `STATE.md` se necessário.

---

## Deterministic gate

`python3 <skill-dir>/scripts/validate_state.py --root ~/DEV/WHITEBEARD/agentic-engineering-kit/samples/enrichment-lab 001-merge-por-unidade` — saída colada na resposta ao usuário.
