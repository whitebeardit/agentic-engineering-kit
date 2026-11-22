# Aplicar evento ao cadastro com limiar de completude (ENR-042) verification

**Verdict**: FAIL
**Proofs**: `proofs.md` at ccf3980
**Verifier**: independent sub-agent (author != verifier)

O código cumpre o que os sete critérios pedem nos casos que a spec e os checks nomeiam, e as provas não foram rodadas
de novo. O veredito é FAIL porque quatro mutações sobrevivem aos comandos `Run`, dois testes afirmam menos do que o
critério fixa, e um exemplo próprio mostra um caso que a spec não decide e em que o valor declarado pelo cliente é
perdido.

## Checks

| Check | Test | Holds |
| --- | --- | --- |
| C1 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_WHEN_documento_sem_cadastro_SHALL_criar_com_todas_as_unidades` | no - afirma `changed`, a contagem 7 e a anotação de uma unidade; nunca afirma a versão 1 (nem `r.eventos[0].versao`, nem a gravação) |
| C2 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_WHEN_unidade_ausente_SHALL_preencher_mesmo_de_evento_antigo` | yes |
| C3 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_WHEN_evento_estritamente_mais_novo_SHALL_sobrescrever` e `RN_ENR_004_IF_empate_ou_evento_anterior_THEN_SHALL_manter_o_gravado` | yes |
| C4 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_IF_origem_provedor_THEN_SHALL_nao_sobrescrever_cliente` e `RN_ENR_004_IF_origem_provedor_THEN_SHALL_preencher_lacuna_e_provedor` | yes |
| C5 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_lancar`, `RN_ENR_004_WHEN_evento_traz_exatamente_N_SHALL_aceitar` e `RN_ENR_004_IF_origem_provedor_THEN_limiar_nao_se_aplica` | no - `toThrow(DomainRuleViolation)` não afirma `ruleId` nem `motivo`; a fronteira só é provada com evento de 1 unidade, nunca N-1 |
| C6 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir` | yes |
| C7 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_WHEN_cadastro_muda_SHALL_emitir_um_ClienteAtualizado_v1` e `clientes.get.int.test.ts` `should publish one ClienteAtualizado v1 per real change, none otherwise` | no - `toMatchObject` e o `map` do teste de integração deixam `occurredAt` de fora; o resto (um evento, `versao` nova, nenhum quando nada muda) segura |

## Findings

| Finding | Evidence | Fix | Closed |
| --- | --- | --- | --- |
| O `ruleId` `RN-ENR-004` da recusa por limiar não é afirmado por nenhum teste | Mutação M4 sobrevive: `cliente.entity.ts:54` com `'RN-ENR-003'` passa nos dois `Run` e na suíte inteira. `RN_ENR_004.merge-por-unidade.unit.test.ts:140` usa `toThrow(DomainRuleViolation)`; o `motivo` só é afirmado na specification (linha 18), não no erro lançado. O caminho do worker para esta regra (`descartado` + log com `ruleId`) também não tem teste | No teste `…_THEN_SHALL_lancar`, capturar o erro e afirmar `ruleId` `RN-ENR-004` e `motivo` `descartado-limiar`; opcionalmente um caso de integração com `LIMIAR_N` baixo afirmando `descartado` e a linha de log | `ae22d25` - C5 (`…_SHALL_lancar` afirma `ruleId` e `motivo`) |
| A fronteira "menos de N" do lado do evento pode deslocar em um sem teste vermelho | Mutação M3 sobrevive: `evento-elegivel-para-merge.ts:20` com `trazidas < limiarN - 1` passa nos dois `Run` e na suíte inteira. O teste `…_WHEN_evento_traz_exatamente_N_SHALL_aceitar` anuncia no comentário (linha 29) "N-1 → recusado", mas a segunda afirmação (linhas 37-39) usa cadastro com N-1 e evento de 1 unidade, que é outra fronteira | Afirmar que evento com N-1 unidades contra cadastro com N é recusado (`{ ok: false, motivo: 'descartado-limiar' }`) | `ae22d25` - C5 (`…_exatamente_N_SHALL_aceitar` recusa evento com N-1) |
| A decisão confirmada "o limiar não conta `apto`" não tem teste | Mutação M11 sobrevive: `cliente.entity.ts:72` devolvendo `this.unidades.size` passa nos dois `Run` e na suíte inteira. Nenhum teste de limiar usa cadastro com a unidade `apto` gravada | Afirmar que cadastro com N-1 unidades de dados mais `apto` aceita evento com menos de N (e que `quantidadeDeCampos` é N-1) | `ae22d25` - C5 (teste novo `…_SHALL_nao_contar_apto_no_limiar`) |
| O teste nomeado em C7 não afirma `occurredAt`, que o critério 7 fixa | Mutação M7 sobrevive aos dois `Run`: `cliente-atualizado.v1.ts:25` com `occurredAt: ''`. `RN_ENR_004…unit.test.ts:158-163` e `clientes.get.int.test.ts:50` não olham o campo. Só morre fora das provas, em `src/__tests__/unit/contratos/cliente-atualizado.asyncapi.unit.test.ts` (`should validate what the factory produces`), que o `npm run gate` roda | Afirmar `occurredAt` no teste de C7 (data ISO válida, ou instante injetado em `criarClienteAtualizadoV1`), ou nomear o teste de contrato como prova de C7 | `ae22d25` - C7 (o teste afirma `occurredAt` em ISO) |
| O teste de C1 não afirma "na versão 1" | `RN_ENR_004…unit.test.ts:53-63` não lê `r.eventos` nem versão; a versão 1 só aparece no teste de integração `should answer 200 with ETag = version after the worker ran`, que não é prova de C1. A anotação é afirmada em 1 das 7 unidades | Afirmar `r.eventos[0].versao` igual a 1 no teste de C1 (ou nomear o teste de integração como segunda prova) e a anotação de todas as unidades | `ae22d25` - C1 (o teste afirma versão 1 e a anotação de todas as unidades) |
| Valor confirmado pelo cliente é sobrescrito por provedor mais novo, e a spec não decide o caso | Exemplo próprio em `HEAD`: provedor grava `endereco.uf` = SP às 12:00; cliente manda SP às 13:00 (`changed = false`, a anotação continua `provedor:biro` 12:00); provedor manda RJ às 14:00 e sobrescreve. O critério 4 fala em "origem gravada" e o 6 em "estado idêntico", então o código segue a letra dos dois; a decisão registrada na spec diz que "declarado pelo cliente vale mais que comprado". O mesmo desenho deixa um evento das 13:00 sobrescrever um valor reafirmado às 14:00 (`merge.ts:37` não renova a anotação) | Decisão do PO; se o valor reafirmado pelo cliente deve ficar protegido, acrescentar critério novo à spec (ID novo, sem editar os aprovados) com check e teste, e tratar a troca de origem/instante da anotação | `022a0b8` - C8 (critério 8 / ING-08 acrescentado por decisão do PO; teste de unidade e de integração novos) |

## Mutations

Feitas numa cópia da pasta do projeto fora da árvore (scratchpad da sessão), uma por rodada, com o arquivo restaurado
entre as rodadas. Comandos rodados em cada uma, os dois `Run` do `tasks.md`:
`npx jest --ci --verbose --reporters=default --selectProjects unit -t 'RN_ENR_004'` (unit) e
`npx jest --ci --verbose --reporters=default --selectProjects int` (int).

| # | Regra | O que foi estragado | Arquivo e linha | Teste que morreu |
| --- | --- | --- | --- | --- |
| M1 | ING-03 | `>` trocado por `>=` na comparação de instante | `src/domain/cliente/service/merge.ts:35` | unit: `RN_ENR_004_IF_empate_ou_evento_anterior_THEN_SHALL_manter_o_gravado` |
| M2 | ING-04 | condição de proveniência removida (`podeSobrescrever = maisNovo`) | `src/domain/cliente/service/merge.ts:36` | unit: `RN_ENR_004_IF_origem_provedor_THEN_SHALL_nao_sobrescrever_cliente` |
| M3 | ING-05 | `trazidas < limiarN` trocado por `trazidas < limiarN - 1` | `src/domain/cliente/specifications/evento-elegivel-para-merge.ts:20` | **sobreviveu** (unit e int verdes) |
| M4 | ING-05 | `ruleId` lançado trocado para `'RN-ENR-003'` | `src/domain/cliente/cliente.entity.ts:54` | **sobreviveu** (unit e int verdes) |
| M5 | ING-06 | removido `\|\| igual(atual.valor, valor)` | `src/domain/cliente/service/merge.ts:37` | unit: `RN_ENR_004_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir` |
| M6 | ING-07 | `this.versao + 1` trocado por `this.versao` no evento | `src/domain/cliente/cliente.entity.ts:61` | unit: `RN_ENR_004_WHEN_cadastro_muda_SHALL_emitir_um_ClienteAtualizado_v1`; int: `should publish one ClienteAtualizado v1 per real change, none otherwise` |
| M7 | ING-07 | `occurredAt` devolvido como `''` | `src/domain/cliente/events/cliente-atualizado.v1.ts:25` | **sobreviveu** aos dois `Run`; morre só na suíte inteira (teste de contrato AsyncAPI) |
| M8 | ING-06/07 | removido `if (!changed) return 'sem-mudanca'` no worker | `src/infrastructure/messaging/worker.ts:101` | int: `should publish one ClienteAtualizado v1 per real change, none otherwise` |
| M9 | ING-05 | removida a isenção de provedor | `src/domain/cliente/specifications/evento-elegivel-para-merge.ts:18` | unit: `RN_ENR_004_IF_origem_provedor_THEN_limiar_nao_se_aplica` |
| M10 | ING-05 | `quantidadeDeCampos >= limiarN` trocado por `>` | `src/domain/cliente/specifications/evento-elegivel-para-merge.ts:20` | unit: `…_THEN_SHALL_recusar` e `…_THEN_SHALL_lancar` |
| M11 | ING-05 | `quantidadeDeCampos` passa a contar `apto` | `src/domain/cliente/cliente.entity.ts:72` | **sobreviveu** (unit e int verdes) |
| M12 | ING-03/04/06 | ramo da unidade já gravada desligado (todo evento sobrescreve) | `src/domain/cliente/service/merge.ts:34` | unit: `…_SHALL_manter_o_gravado`, `…_SHALL_nao_sobrescrever_cliente`, `…_SHALL_nao_mudar_nem_emitir`; int: `should publish one ClienteAtualizado v1…` |
| M13 | ING-01 | `instante` da anotação trocado pelo relógio (`new Date()`) | `src/domain/cliente/service/merge.ts:39` | unit: `…_SHALL_criar_com_todas_as_unidades` e mais quatro |

Nove mortas, quatro sobreviventes (M3, M4, M7, M11); cada sobrevivente é uma linha em `## Findings`.

## Exemplos próprios

Rodados em `HEAD` como testes descartáveis na cópia, não commitados.

| Regra | Valor tentado | Resultado |
| --- | --- | --- |
| ING-03 | empate escrito em outro fuso (`09:00:00-03:00` contra `12:00:00Z`); evento 1 ms mais novo | mantém o gravado; sobrescreve - regra segura |
| ING-05 | evento com N-1 contra cadastro com N; cadastro com N-1 dados mais `apto`; cadastro com N+5 e evento com N-1 mais `apto`; pelo worker com `LIMIAR_N=7` | recusa com `RN-ENR-004`/`descartado-limiar`; aceita; recusa; `descartado`, log com `ruleId`, versão e eventos intactos - regra segura |
| ING-04 com ING-06 | cliente reafirma o valor de uma unidade de provedor, depois provedor mais novo muda | provedor sobrescreve - achado (última linha de `## Findings`) |
| ING-06 | evento sem nenhuma unidade | `changed = false`, sem evento - regra segura |
| ING-01 | 5000 unidades em documento novo | um evento com `versao` 1, todas anotadas - regra segura |

## O que não foi verificado

- As provas não foram rodadas de novo na árvore real; valem as de `proofs.md`.
- `design.md`, `validation.md` e a seção `## Handoff` do `tasks.md` não foram lidos.
- Concorrência (RN-ENR-005, releitura com merge refeito) e a camada de arquitetura da matriz não têm check nesta
  feature e não foram exercitadas.
- Na cópia, `docs-gerados.unit.test.ts` falha já sem mutação (`docs/generated/deps.md` desatualizado, efeito da cópia
  com `node_modules` por link simbólico); por isso a suíte inteira só serviu para conferir os sobreviventes.
- `proofs.md` registra `Tree: clean`, mas `git status` mostra `tasks.md` modificado (uma linha, dentro do Handoff) e
  `proofs.md` sem commit; o gate exige árvore limpa.
