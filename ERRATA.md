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

## 2026-09-13 — rules do Cursor que o Cursor não carregava

**Onde**: `cursor/rules/contracts.mdc` e `cursor/rules/legacy.mdc` (entregues pelo plugin do Cursor e pelo `apply.sh
--cursor`), nas tags `kit--v0.2.0` a `kit--v0.5.2`; e as cópias em `samples/enrichment-lab/.cursor/rules/` (desde `kit--v0.3.0`) e
`samples/orders-sample/.cursor/rules/` (desde `kit--v0.2.0`).

**O que estava publicado**: o carimbo `<!-- gerado por tools/build-cursor.py … -->` na linha 1, antes do `---` do
frontmatter. Com ele, o Cursor não lê o frontmatter e não aplica a rule — nem por `globs`, nem com `alwaysApply: true`.
Testado no `cursor-agent` 2026.06.19, em repositórios temporários idênticos exceto por essa linha: com o carimbo, a rule
não carregou em nenhuma das duas rodadas; sem ele, carregou nas duas.

**O que passou a valer** (tag `kit--v0.5.3`): o carimbo é um comentário YAML dentro do frontmatter; `tools/build-cursor.py
--check` reprova qualquer `.mdc` do repositório que não abra com `---`, e `--selftest` prova a regra com um mutante no CI.

**Se você clonou uma tag anterior**: no Cursor, as duas rules por caminho não estavam ativas. Atualize o kit para a
`kit--v0.5.3` (plugin ou `apply.sh --cursor`), ou mova a primeira linha de cada `.mdc` para dentro do frontmatter, como
`# …`. No Claude Code nada muda: as rules dele são `rules/*.md` com `paths:`, sem o carimbo.

**Rastro**: issue #24 deste repositório, apontada pelo check CTX-04 de um scanner de harness (`harness-score` 1.6.5) e
confirmada no Cursor pelo repositório do livro *Cercando a IA* (AD-045).

## 2026-09-13 — quatro defeitos de comportamento corrigidos na v0.5.4

**Onde e o que estava publicado** (medido com `git show <tag>:<arquivo>` em cada tag):

- **Rampa .NET que não acontecia** — `dotnet/Directory.Build.props` e `samples/orders-sample/Directory.Build.props`, tags
  `kit--v0.2.0` a `kit--v0.5.3`: `AnalysisLevel=latest-Recommended` tem precedência sobre `AnalysisMode` ("if you specify
  both properties, AnalysisLevel takes precedence over AnalysisMode", doc `msbuild-props`); um projeto com
  `AnalysisMode=Minimum` compilava com o conjunto Recommended (SDK 10.0.103, `dotnet build -v:diag`). Issue #25.
- **`NotebookEdit` fora da proteção de caminhos** — `templates/.claude/settings.json` e as cópias dos samples, tags
  `kit--v0.2.0` a `kit--v0.5.3`: o matcher `Edit|Write|MultiEdit` casa nomes exatos, e o `NotebookEdit` escreve arquivo.
  Issue #19.
- **Instalador que escrevia por link simbólico** — `apply.sh`, tags `kit--v0.2.0` a `kit--v0.5.3`: com `.claude` simbólico
  para fora do alvo, escrevia fora dele; mudava o modo de hooks alheios; falhava no meio sem dizer o que criou. Issue #10.
- **Permissões npm/npx no perfil .NET** — `apply.sh --dotnet`, tags `kit--v0.3.0` a `kit--v0.5.3`: entregava o
  `settings.json` genérico, com sete permissões de Node que um projeto .NET não usa. Issue #27.

**O que passou a valer** (tag `kit--v0.5.4`): ver o CHANGELOG; cada conserto tem teste no CI.

**Se você aplicou uma tag anterior**: rode `apply.sh <repo> --dotnet --check` (ou com os perfis que usou) para ver o que
difere e leve por PR: no `Directory.Build.props`, troque `latest-Recommended` por `latest`; no `.claude/settings.json`,
troque `MultiEdit` por `NotebookEdit` nos dois matchers e, num projeto só .NET, retire as permissões `npm`/`npx`. Se o
alvo tinha algum link simbólico em `.claude/`, `.cursor/` ou `docs/`, confira se arquivos do kit foram parar fora dele.

**Rastro**: issues #10, #19, #25 e #27 deste repositório; AD-046 e AD-047 no repositório do livro *Cercando a IA*.

## 2026-09-14 — alcance dos agentes, ordem entre serviços e mensagens corrigidos na v0.5.7

**Onde e o que estava publicado**:

- **Fonte que o agente não alcança** — `agents/impact-analyzer.md` (tags `kit--v0.2.0` a `kit--v0.5.6`) e `templates/AGENTS.root.md` (tags
  `kit--v0.2.0` a `kit--v0.5.6`): o agente listava "mapa transversal no vault (via MCP, se disponível)" com `tools: Read, Grep, Glob`, que não
  inclui ferramenta de MCP, e o template mandava consultar o vault via MCP. A fonte nunca era consultada, e o agente
  seguia sem dizer. Issue #13.
- **Ordem entre serviços de um sentido só** — `templates/AGENTS.root.md`, tags `kit--v0.2.0` a `kit--v0.5.6`: dava contrato → produtor →
  consumidor → legado como a ordem padrão, e ela só vale para acrescentar; para retirar, ou quando o consumidor novo lê
  dado antigo, a ordem inverte. Issue #14.
- **"O caminho mudou" para qualquer erro HTTP** — `hooks/tlc-version.sh`, tags `kit--v0.2.0` a `kit--v0.5.6`: com `curl -f`, um 403 de limite do
  GitHub, um 429 ou um 5xx passageiro recebia a mensagem de que o repositório Tech Leads Club tinha mudado o caminho.
  Issue #30.
- **Formatação .NET que falhava em silêncio** — `hooks/dotnet-format.sh`, tags `kit--v0.2.0` a `kit--v0.5.6`: a falha do `dotnet format` era
  descartada, e nenhum gate conferia a formatação. No `orders-sample`, a cópia `.claude/hooks/dotnet-format.sh` era a do
  primeiro commit do kit (comentário com `MultiEdit`), e a `.cursor/hooks/tlc-version.sh` tinha ficado como no commit da v0.2
  (`c486c61`), comparando versão como texto — ela não está registrada no `.cursor/hooks.json` do exemplo e não rodava. Issue #28.
- **Afirmação sem fonte** — `dotnet/.editorconfig` e `samples/orders-sample/.editorconfig`, tags `kit--v0.2.0` a `kit--v0.5.6`: o comentário
  "Mascaramento de erro — o que mais cresce com IA", sem medição que o sustente. Issue #29.

**O que passou a valer** (tag `kit--v0.5.7`): ver o CHANGELOG; #13, #14, #28 e #30 com gate no CI.

**Se você aplicou uma tag anterior**: no `AGENTS.md` raiz, troque a seção "Ordem padrão entre serviços" e a linha do mapa
transversal pelas do template novo; no perfil .NET, rode `apply.sh <repo> --dotnet --check` para ver o `dotnet-format.sh`
que difere e acrescente `dotnet format <sln> --verify-no-changes` ao gate. Quem usa o plugin recebe os agentes e o hook
de versão com `claude plugin update`. Nos pedidos ao `impact-analyzer`, cole o trecho do mapa transversal e inicie a
sessão com `--add-dir` para os repositórios irmãos.

**Rastro**: issues #13, #14, #28, #29 e #30 deste repositório; revisões do livro *Cercando a IA* (cap. 14, apêndice F e
bump de 14/09/2026).
