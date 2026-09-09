# Errata — kit de engenharia com agentes

Correções a material já publicado neste repositório, na ordem em que foram confirmadas. Uma entrada entra aqui quando
o defeito já está corrigido no `main` mas continua presente em tags publicadas ou no histórico — ou seja, quando quem
clonou antes ainda tem o problema em mãos. Cada linha diz o que estava lá, o que passou a valer e o que fazer se você
tiver a versão antiga.

## 2026-09-09 — documento com dígitos válidos em artefato de exibição

**Onde**: `docs/observability-fixtures/runs/trace-finder.md` (a demonstração da guarda de LGPD do `trace-finder`), nas
tags `kit--v0.4.0` a `kit--v0.5.1` e nos commits correspondentes.

**O que estava publicado**: o exemplo usava um número de onze dígitos que **passa** no algoritmo dos dígitos
verificadores de CPF. Ele é o valor de teste mais difundido do desenvolvimento brasileiro — aparece em geradores e
tutoriais de validação —, e ainda assim um número que passa na validação pode, em princípio, pertencer a alguém.
Chamá-lo de sintético não prova o contrário.

**O que passou a valer** (commit `b0937d0`, `main`): o exemplo usa um número que **reprova** na validação. A guarda
dispara por formato — onze ou catorze dígitos —, então a demonstração é idêntica e o exemplo não pode ser o documento
de uma pessoa. No mesmo commit, `agents/trace-finder.md` deixou de descrever a guarda como definição de dado pessoal:
ela é um arame de tropeço por formato, que não pega documento pontuado, e-mail nem telefone, e pode recusar um
identificador técnico numérico.

**Regra que fica**: nenhum artefato de exibição do kit — fixture, captura, documentação, material do e-book — usa
documento que passe na validação. Onde a validade é necessária para exercitar uma regra de negócio, como no teste da
RN-ENR-001 do laboratório, o valor fica em `samples/enrichment-lab/src/__tests__/helpers/` e não é reaproveitado fora
dali.

**Se você clonou uma tag anterior**: nada quebra e nada precisa ser refeito. Se for reaproveitar a fixture como
exemplo próprio, troque o número por um que reprove na validação. O histórico não foi reescrito: reescrevê-lo
invalidaria todos os clones existentes, e a exposição marginal não justifica.

**Rastro**: issue #9 deste repositório (varredura e gate que impedem a reincidência) e o registro AD-036 no repositório
do livro *Cercando a IA*, que achou o defeito ao contra-verificar a revisão externa do capítulo 12.
