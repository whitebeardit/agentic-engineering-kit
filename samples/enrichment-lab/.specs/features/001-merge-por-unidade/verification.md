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
| C8 | `RN_ENR_004.merge-por-unidade.unit.test.ts` `RN_ENR_004_WHEN_cliente_reafirma_valor_de_provedor_SHALL_anotar_cliente_sem_emitir` e `clientes.get.int.test.ts` `should store a client reaffirmation with a new version and publish nothing` | yes - o de unidade afirma a anotação inteira (origem do cliente; instante do evento quando ele é mais novo e o gravado quando não é), `eventos: []` e o provedor mais novo sem efeito; o de integração afirma a gravação (`gravado`), a versão nova (`"v4"`), nenhuma publicação e o provedor seguinte em `sem-mudanca`. O outro lado da condição (evento de provedor não reanota) não está em teste nenhum: ver a última linha de `## Findings` |

## Findings

| Finding | Evidence | Fix | Closed |
| --- | --- | --- | --- |
| O `ruleId` `RN-ENR-004` da recusa por limiar não é afirmado por nenhum teste | Mutação M4 sobrevive: `cliente.entity.ts:54` com `'RN-ENR-003'` passa nos dois `Run` e na suíte inteira. `RN_ENR_004.merge-por-unidade.unit.test.ts:140` usa `toThrow(DomainRuleViolation)`; o `motivo` só é afirmado na specification (linha 18), não no erro lançado. O caminho do worker para esta regra (`descartado` + log com `ruleId`) também não tem teste | No teste `…_THEN_SHALL_lancar`, capturar o erro e afirmar `ruleId` `RN-ENR-004` e `motivo` `descartado-limiar`; opcionalmente um caso de integração com `LIMIAR_N` baixo afirmando `descartado` e a linha de log | `ae22d25` - C5 (`…_SHALL_lancar` afirma `ruleId` e `motivo`) |
| A fronteira "menos de N" do lado do evento pode deslocar em um sem teste vermelho | Mutação M3 sobrevive: `evento-elegivel-para-merge.ts:20` com `trazidas < limiarN - 1` passa nos dois `Run` e na suíte inteira. O teste `…_WHEN_evento_traz_exatamente_N_SHALL_aceitar` anuncia no comentário (linha 29) "N-1 → recusado", mas a segunda afirmação (linhas 37-39) usa cadastro com N-1 e evento de 1 unidade, que é outra fronteira | Afirmar que evento com N-1 unidades contra cadastro com N é recusado (`{ ok: false, motivo: 'descartado-limiar' }`) | `ae22d25` - C5 (`…_exatamente_N_SHALL_aceitar` recusa evento com N-1) |
| A decisão confirmada "o limiar não conta `apto`" não tem teste | Mutação M11 sobrevive: `cliente.entity.ts:72` devolvendo `this.unidades.size` passa nos dois `Run` e na suíte inteira. Nenhum teste de limiar usa cadastro com a unidade `apto` gravada | Afirmar que cadastro com N-1 unidades de dados mais `apto` aceita evento com menos de N (e que `quantidadeDeCampos` é N-1) | `ae22d25` - C5 (teste novo `…_SHALL_nao_contar_apto_no_limiar`) |
| O teste nomeado em C7 não afirma `occurredAt`, que o critério 7 fixa | Mutação M7 sobrevive aos dois `Run`: `cliente-atualizado.v1.ts:25` com `occurredAt: ''`. `RN_ENR_004…unit.test.ts:158-163` e `clientes.get.int.test.ts:50` não olham o campo. Só morre fora das provas, em `src/__tests__/unit/contratos/cliente-atualizado.asyncapi.unit.test.ts` (`should validate what the factory produces`), que o `npm run gate` roda | Afirmar `occurredAt` no teste de C7 (data ISO válida, ou instante injetado em `criarClienteAtualizadoV1`), ou nomear o teste de contrato como prova de C7 | `ae22d25` - C7 (o teste afirma `occurredAt` em ISO) |
| O teste de C1 não afirma "na versão 1" | `RN_ENR_004…unit.test.ts:53-63` não lê `r.eventos` nem versão; a versão 1 só aparece no teste de integração `should answer 200 with ETag = version after the worker ran`, que não é prova de C1. A anotação é afirmada em 1 das 7 unidades | Afirmar `r.eventos[0].versao` igual a 1 no teste de C1 (ou nomear o teste de integração como segunda prova) e a anotação de todas as unidades | `ae22d25` - C1 (o teste afirma versão 1 e a anotação de todas as unidades) |
| Valor confirmado pelo cliente é sobrescrito por provedor mais novo, e a spec não decide o caso | Exemplo próprio em `HEAD`: provedor grava `endereco.uf` = SP às 12:00; cliente manda SP às 13:00 (`changed = false`, a anotação continua `provedor:biro` 12:00); provedor manda RJ às 14:00 e sobrescreve. O critério 4 fala em "origem gravada" e o 6 em "estado idêntico", então o código segue a letra dos dois; a decisão registrada na spec diz que "declarado pelo cliente vale mais que comprado". O mesmo desenho deixa um evento das 13:00 sobrescrever um valor reafirmado às 14:00 (`merge.ts:37` não renova a anotação) | Decisão do PO; se o valor reafirmado pelo cliente deve ficar protegido, acrescentar critério novo à spec (ID novo, sem editar os aprovados) com check e teste, e tratar a troca de origem/instante da anotação | `022a0b8` - C8 (critério 8 / ING-08 acrescentado por decisão do PO; teste de unidade e de integração novos) |
| Segunda rodada (`ec6da04`): a reanotação do ING-08 pode valer também para evento de provedor sem teste vermelho | Mutação A5 sobrevive aos dois `Run` e à suíte inteira: `merge.ts:42` com `if (ehProvedor(atual.origem))` (sem o `!provedor &&`). Com ela, `provedor:outro` mandando às 13:00 o mesmo valor que `provedor:biro` gravou às 12:00 devolve `reanotado: true` e troca a anotação para `provedor:outro` 13:00; pelo worker isso grava e avança a versão, contra o critério 6 e fora do "evento de origem `cliente:*`" do critério 8. O teste de C6 (`…_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir`) só usa cliente sobre cliente; nenhum teste manda valor igual a partir de um provedor | No teste de C6 ou de C8, afirmar que evento de provedor com valor igual ao de unidade de provedor (e ao de unidade de cliente) devolve `{ changed: false, eventos: [] }` e deixa a anotação como estava | `72927ff` - C8 (teste novo `…_IF_provedor_traz_valor_igual_THEN_SHALL_nao_reanotar`; a mutação A5 repetida fica vermelha) |

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

## Segunda rodada (C8, em ec6da04)

**Veredito desta rodada**: FAIL - uma mutação sobrevive (A5), registrada como achado aberto em `## Findings`.

Escopo: só o check C8 (critério 8, ING-08) e a conferência de que os critérios 3, 4, 6 e 7 continuam valendo depois
de `022a0b8`. Verifier independente (autor != verificador). Lidos: `spec.md`, os `## Checks` e as linhas `Build`/`Run`
do `tasks.md`, o diff de `022a0b8` em `src/`, o código e os testes.

O código cumpre o critério 8 em todos os casos tentados, e os dois testes nomeados em C8 afirmam o que o critério
fixa. O que falta é um teste para o outro lado da condição: nada fica vermelho se a reanotação passar a valer também
para evento de provedor.

### O que os dois testes de C8 afirmam

| O que o critério 8 fixa | Onde é afirmado |
| --- | --- |
| a anotação passa para a origem do evento | unidade: `toEqual({ valor, instante, origem: 'cliente:app' })` |
| instante = o mais recente entre o gravado e o do evento | unidade: evento mais novo (13:00 sobre 12:00) dá 13:00; evento mais antigo (11:00 sobre 12:00) dá 12:00 |
| grava com versão nova | integração: `gravado` e ETag `"v4"` (a unidade não tem como afirmar: a versão é da gravação) |
| não emite evento | unidade: `eventos: []`; integração: `publicados` cresce só com o preenchimento anterior |
| provedor mais novo deixa de sobrescrever | unidade: `changed` falso e valor mantido; integração: `sem-mudanca` e `uf` = SP |

### Mutações

Feitas na cópia `scratchpad/verif3/copy` (fora da árvore, `node_modules` por link simbólico), uma por rodada, com o
arquivo restaurado entre as rodadas (conferido com `diff -r` ao fim). Em cada uma rodaram os dois `Run` do `tasks.md`.
As linhas são as de `ec6da04`.

| # | Regra | O que foi estragado | Arquivo e linha | Teste que morreu |
| --- | --- | --- | --- | --- |
| A1 | ING-08 | reanotação não sinalizada (`reanotado = false`) | `src/domain/cliente/service/merge.ts:48` | unit: `…_cliente_reafirma_valor_de_provedor_SHALL_anotar_cliente_sem_emitir`; int: `should store a client reaffirmation with a new version and publish nothing` |
| A2 | ING-08 | origem não trocada (`origem: atual.origem`) | `merge.ts:46` | unit e int: os mesmos dois de A1 |
| A3 | ING-08 | instante sempre o do evento | `merge.ts:45` | unit: `…_cliente_reafirma_…` (int verde) |
| A4 | ING-08 | instante sempre o gravado | `merge.ts:45` | unit: `…_cliente_reafirma_…` (int verde) |
| A5 | ING-08 com ING-06 | reanotação também para evento de provedor (`if (ehProvedor(atual.origem))`) | `merge.ts:42` | **sobreviveu** (unit e int verdes; suíte inteira também) |
| A6 | ING-08 com ING-06 | reanotação também sobre unidade de cliente (`if (!provedor)`) | `merge.ts:42` | unit: `…_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir`; int: `should publish one ClienteAtualizado v1…` e `should store a client reaffirmation…` |
| A7 | ING-08 | worker não grava na reanotação (`if (!changed) return 'sem-mudanca'`) | `src/infrastructure/messaging/worker.ts:102` | int: `should store a client reaffirmation…` (unit verde) |
| A8 | ING-08 | entidade devolve um `ClienteAtualizado` na reanotação | `src/domain/cliente/cliente.entity.ts:61` | unit: `…_cliente_reafirma_…`; int: `should store a client reaffirmation…` |
| A9 | ING-08 | entidade ignora `reanotado` e não aplica as unidades | `cliente.entity.ts:58` | unit e int: os mesmos dois de A1 |
| A10 | ING-08 com ING-07 | reanotação conta como mudança (`changed = true`) | `merge.ts:48` | unit e int: os mesmos dois de A1 |
| A11 | ING-08 | escolha do instante invertida | `merge.ts:45` | unit: `…_cliente_reafirma_…` (int verde) |
| A12 | ING-08 | worker publica um evento quando `reanotado` | `worker.ts:113` | int: `should store a client reaffirmation…` (unit verde) |
| A13 | ING-06 | `continue` do valor igual removido | `merge.ts:50` | unit: `…_estado_identico_…` e `…_cliente_reafirma_…`; int: `should store a client reaffirmation…` |
| R1 | ING-03 | `>` trocado por `>=` | `merge.ts:40` | unit: `…_IF_empate_ou_evento_anterior_THEN_SHALL_manter_o_gravado` |
| R2 | ING-04 | `podeSobrescrever = maisNovo` | `merge.ts:52` | unit: `…_SHALL_nao_sobrescrever_cliente` e `…_cliente_reafirma_…`; int: `should store a client reaffirmation…` |
| R3 | ING-07 | `this.versao + 1` trocado por `this.versao` | `cliente.entity.ts:64` | unit: `…_SHALL_emitir_um_ClienteAtualizado_v1` e `…_SHALL_criar_com_todas_as_unidades`; int: `should publish one ClienteAtualizado v1…` |
| R4 | ING-06/07 | worker grava sempre (retorno `sem-mudanca` desligado) | `worker.ts:102` | int: `should publish one ClienteAtualizado v1…` e `should store a client reaffirmation…` |
| R5 | ING-04 | condição de proveniência invertida (`provedor \|\| …`) | `merge.ts:52` | unit: `…_nao_sobrescrever_cliente`, `…_cliente_reafirma_…`, `…_estritamente_mais_novo_SHALL_sobrescrever`, `…_so_apto_muda_…`; int: `should store a client reaffirmation…` |

Dezoito mutações: treze miradas no critério 8 (A1 a A13), doze mortas e uma sobrevivente (A5); cinco nos critérios
3, 4, 6 e 7 (R1 a R5), todas mortas.

### Exemplos próprios

Rodados em `ec6da04` como teste descartável na cópia (apagado depois, não commitado).

| Regra | Valor tentado | Resultado |
| --- | --- | --- |
| ING-08 com ING-03/07 | um evento do cliente com três unidades de provedor: duas com valor igual, uma com valor novo e mais novo | as duas iguais passam para `cliente:app` com o instante do evento, a terceira é sobrescrita, `changed = true`, um evento - regra segura |
| ING-08 com ING-03 | o mesmo, com o evento mais antigo que o gravado | a de valor igual passa para o cliente e mantém o instante gravado; a de valor diferente fica com o provedor; `reanotado`, sem evento - regra segura |
| ING-06 | provedor manda valor igual ao de unidade de cliente, mais novo | `{ changed: false, eventos: [] }`, anotação intacta - regra segura |
| ING-06 | `provedor:outro` manda valor igual ao de `provedor:biro`, mais novo | `{ changed: false, eventos: [] }`, anotação intacta - regra segura em `ec6da04` (é o caso que A5 quebra sem teste vermelho) |
| ING-06 | `cliente:portal` manda valor igual ao de `cliente:app`, mais novo | `{ changed: false, eventos: [] }`, anotação intacta - regra segura |
| ING-08 | empate de instante escrito em outro fuso (`09:00:00-03:00` contra `12:00:00Z`) | origem passa para o cliente, instante gravado mantido - regra segura |
| ING-08 com `apto` | `apto: true` de provedor reafirmado pelo cliente junto com uma unidade de valor igual | `apto` e a unidade passam para o cliente, `reanotado`, sem evento - regra segura |
| ING-08 com ING-05 | cliente reafirma 1 unidade contra cadastro com N unidades de provedor; depois reafirma as N | o primeiro é recusado com `RN-ENR-004`/`descartado-limiar` e a anotação não muda; o segundo reanota as N - regra segura (o limiar vem antes do merge) |
| ING-08 pelo worker | provedor grava; cliente reafirma; cliente reafirma de novo (outro `eventId`); provedor mais novo com outro valor; cliente antigo com outro valor | `gravado` v1 com 1 publicação; `gravado` v2 sem publicação; `sem-mudanca`; `sem-mudanca`; `sem-mudanca`; versão 2 e 1 publicação ao fim - regra segura |
| ING-08 com RN-ENR-005 | conflito de escrita na gravação da reanotação (outro processo grava provedor RJ 14:00 entre a leitura e a escrita; o cliente reafirmava SP 13:00) | o worker relê e refaz o merge: `uf` fica RJ do provedor (valor diferente, evento mais antigo), `apto` igual é reanotado, `gravado` v3, sem publicação - regra segura |
| ING-08 com `apto` inferido (RN-ENR-006) | pelo worker, pessoa jurídica: provedor grava o cadastro completo (`apto` inferido `true`); cliente reafirma só a `uf` às 13:00 | a `uf` passa para o cliente, mas o `apto` inferido do evento parcial é `false`, mais novo, e sobrescreve o `true`: `changed = true`, versão 2 e um `ClienteAtualizado`. Segue a letra da spec (`apto` é unidade; edge case do `apto` diferente). Não é achado; fica registrado porque, por este caminho, a reafirmação do critério 8 chega ao consumidor como evento |

### Critérios 3, 4, 6 e 7 depois de `022a0b8`

- **3**: vale. R1 morre no teste do empate; a comparação de instante (`merge.ts:40`) não mudou.
- **4**: vale. R2 e R5 morrem; provedor mais novo não sobrescreve unidade de cliente, inclusive a que virou de cliente
  por reanotação (teste de C8 e exemplo pelo worker).
- **6**: vale no código de `ec6da04` (exemplos de valor igual por provedor e por cliente devolvem
  `{ changed: false, eventos: [] }` sem `reanotado`). A prova ficou mais estreita do que a condição nova: A5 sobrevive.
  A leitura de "estado" como valor mais anotação é a da linha de decisão acrescentada à spec em 2026-11-22.
- **7**: vale. R3 e R4 morrem; a reanotação não publica (A8, A10 e A12 morrem), e mudança de valor junto com
  reanotação no mesmo evento publica exatamente um.

### O que não foi verificado nesta rodada

- As provas não foram rodadas na árvore real nem `check_proofs.py`/`validate_verification.py`; `proofs.md` não foi
  conferido contra `ec6da04`. Os `Run` foram rodados só na cópia (verdes sem mutação).
- `npm run gate` (o `Build`) não foi rodado. Na cópia, `docs-gerados.unit.test.ts` falha já sem mutação, como na
  primeira rodada; o resto da suíte inteira passa (53 de 54).
- `design.md`, `validation.md` e a seção `## Handoff` do `tasks.md` não foram lidos.
- Os checks C1, C2 e C5 e os achados fechados em `ae22d25` não foram reconferidos.
- `docs/regras/enriquecimento.md` e `AGENTS.md`, também tocados por `022a0b8`, não foram lidos.
- Só o repositório em memória foi exercitado; não há outro adaptador de gravação neste laboratório.
