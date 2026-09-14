# Changelog

## kit--v0.5.7 — 2026-09-14

Fecha as cinco issues que ficaram abertas depois da Onda 1 das revisões do livro *Cercando a IA*. Esta versão **altera um
hook, dois agentes, o template raiz e o exemplo .NET** — quem aplicou o kit por `apply.sh` confere com
`apply.sh <repo> --check` e leva por PR; quem usa o plugin, por `claude plugin update`.

- **#30 Hook de versão do tlc.** Só HTTP 404 vira "o caminho do upstream mudou"; 403 (limite do GitHub), 429 e 5xx viram
  "não verificado", com a data da última verificação. Até a v0.5.6 o `curl -f` transformava qualquer HTTP ≥ 400 em
  "mudou o path". `tools/test-tlc-version.sh` com 18 casos; o hook da v0.5.6 reprova 3.
- **#13 `impact-analyzer` sem fonte fora do alcance.** O mapa transversal entra no pedido: o agente não tem ferramenta de
  MCP nem acesso ao vault, e o mapa que não veio vai para "O que não encontrei". Para cruzar repositórios, a sessão começa
  com `--add-dir` para cada irmão. O `contract-reviewer` e o `templates/AGENTS.root.md` deixam de mandar consultar o vault.
- **#14 Ordem entre serviços nos dois sentidos.** `templates/AGENTS.root.md` separa a ordem de acrescentar (contrato →
  produtor → consumidor → legado) da inversa (retirar, ou consumidor novo que lê dado antigo: consumidores primeiro), com a
  regra "sobe primeiro quem pode mudar sem quebrar quem ainda não mudou" e a exceção do legado fonte de verdade. Na
  Etiqueta, a evidência colada libera o próximo repositório a **começar**; **implantar** depende do check verde. Gate novo
  `tools/check-agentes.py` para #13 e #14 (com `--selftest`; os arquivos da v0.5.6 dão 12 erros): confere o que os
  arquivos declaram e prometem, não o comportamento do modelo.
- **#28 Formatação .NET conferida.** `hooks/dotnet-format.sh` diz que é melhor esforço e escreve a falha no stderr
  (continua saindo 0); o gate do `orders-sample` e o `tools/test-dotnet.sh` rodam `dotnet format --verify-no-changes`
  (um `.cs` desindentado reprova); o `AGENTS.md` do exemplo escreve a fronteira de confiança do `dotnet format`.
  `tools/test-hooks.sh` compara todas as cópias de hooks dos samples com `hooks/` — antes, só duas; as cópias do
  `dotnet-format.sh` e do `tlc-version.sh` no `orders-sample` estavam desatualizadas e foram sincronizadas.
- **#29 Contrato .NET sem gate, dito na tabela.** A célula .NET de "Contrato como código" em `docs/perfil-node-ts.md` diz
  "política, sem gate"; o comentário do `.editorconfig` que afirmava, sem fonte, que mascaramento de erro "é o que mais
  cresce com IA" passa a dizer só o que o grupo cobre.

## kit--v0.5.6 — 2026-09-14

Correção de release: **os manifestos do plugin passam a dizer a versão da tag**. As tags `kit--v0.5.4` e `kit--v0.5.5`
saíram com `"version": "0.5.3"` em `.claude-plugin/plugin.json` e `.cursor-plugin/plugin.json`, e `claude plugin details`
mostrava 0.5.3 para quem instalava a versão nova; o conteúdo das duas tags é o do CHANGELOG delas. Novo gate no CI,
`tools/check-versao.py` (com `--selftest`): a versão dos dois manifestos é a da primeira entrada deste CHANGELOG e, num
run de tag, a da tag. Achado na revisão do bump do livro *Cercando a IA*.

## kit--v0.5.5 — 2026-09-13

Correção da v0.5.4: **a saída do `apply.sh` volta a mostrar os caminhos como você os passou** (`kit → .` e
`+ criado    ./AGENTS.md` para `apply.sh .`). A v0.5.4 resolvia o alvo para conferir links simbólicos (#10) e passou a
imprimir o caminho absoluto resolvido, diferente em cada máquina; as conferências continuam no caminho resolvido.
`tools/test-apply.sh` confere a forma da saída, e o `apply.sh` da v0.5.4 reprova o caso novo. Achado pela recaptura da
árvore de referência do livro *Cercando a IA*, cuja asserção comparou o que o instalador disse ter criado com a listagem.

## kit--v0.5.4 — 2026-09-13

Fecha a Onda 1 das revisões externas contra-verificadas do livro *Cercando a IA*: catorze issues. Esta versão **altera o
instalador, hooks, uma rule e o perfil .NET** — quem aplicou o kit por `apply.sh` confere as mudanças com
`apply.sh <repo> --check` (novidade desta versão) e as leva por PR; quem usa o plugin, por `claude plugin update`.

- **#10 Instalador que confere antes de escrever.** `apply.sh` planeja todos os destinos e recusa link simbólico no
  destino ou num ancestral dentro do alvo — e aí não escreve nada; `chmod +x` só nos hooks que criou; o que existe é
  mantido, com aviso quando difere do kit; em falha no meio, lista o que criou. `--check` e `--diff` são novos.
- **#11 e #21 Hook de versão do tlc.** Versões ordenadas por campo (3.10.0 > 3.9.0; local mais nova fica quieta);
  estados ausente, duplicado, desatualizado, não comparável e não verificado (sem rede, timeout, sem `curl`), com a data
  da última verificação; o comando de conserto cita o catálogo por onde o kit foi instalado, não `@whitebeard-kit` fixo.
- **#12 CLI do Tech Leads Club com versão fixa** (`@tech-leads-club/agent-skills@1.4.10`) no instalador, no hook e nos docs.
- **#15 Roteiro.** A fase 4 ganha critério de saída; "DORA 5 + rework" diz a edição das métricas e qual retrabalho.
- **#16 Lições do método em toda sessão.** `rules/licoes-do-metodo.md`, sem `paths`, carrega sempre no Claude Code;
  `tools/build-cursor.py` gera `alwaysApply: true` para rule sem `paths`.
- **#17 Próximos passos do instalador** em linhas curtas: "negado antes da escrita (Claude Code e Cursor)".
- **#18 `debug-prod.md`**: o `-01` do `traceparent` **pede** a exportação; a cadeia instrumentada que respeita a flag a obtém.
- **#19 Matcher de edição** `Edit|Write|NotebookEdit` no template e nos samples (o `MultiEdit` não consta na referência de
  hooks, e o `NotebookEdit` ficava fora da proteção de caminhos); `cursor-paridade` diz o que passa por `Bash`.
- **#20 `test-designer`** não promete hook que não existe.
- **#22 `AGENTS.md` do laboratório Node**: o *Never* cita as catracas reais e onde roda o `check-documentos`.
- **#25 Rampa .NET.** `AnalysisLevel=latest` nos dois `Directory.Build.props`: o valor composto `latest-Recommended` tinha
  precedência sobre `AnalysisMode` e o legado compilava em Recommended.
- **#26 Exemplo .NET reproduzível**: versões exatas, `packages.lock.json` versionado, `global.json` (SDK 10.0.103,
  `latestPatch`), versão no exemplo de ArchUnitNET e job .NET no CI.
- **#27 Permissões por perfil**: `apply.sh --dotnet` entrega `settings.dotnet.json`, sem npm/npx.
- **Testes novos no CI**: `tools/test-apply.sh` (instalador, 23 casos), `tools/test-tlc-version.sh` (hook de versão, 15
  casos herméticos) e `tools/test-dotnet.sh` (restore bloqueado, build, testes, globalconfig efetivo por projeto); cada um
  provado com mutante — o `apply.sh` da v0.5.3 reprova 13 casos, o hook da v0.5.3 reprova 11, e o `latest-Recommended`
  reprova a rampa.

## kit--v0.5.3 — 2026-09-13

Correção pequena, antes das demais issues abertas, que passam para a v0.5.4: **as rules do Cursor voltam a carregar**. Quem usa
o plugin do Cursor ou aplicou `apply.sh --cursor` recebe a mudança atualizando; no Claude Code nada muda.

- **#24 Rules do Cursor.** `tools/build-cursor.py` punha o carimbo "gerado por" na linha 1, antes do `---`; o Cursor não
  lia o frontmatter e ignorava as duas rules por caminho (`contracts`, `legacy`) — no plugin do Cursor, no
  `apply.sh --cursor` e nos dois laboratórios. O carimbo vai para dentro do frontmatter como comentário YAML;
  `--check` reprova qualquer `.mdc` que não abra com `---`, e `--selftest` prova a regra com um mutante no CI. Testado
  no `cursor-agent` 2026.06.19: com o carimbo antes, a rule não carrega; na forma nova, carrega.
- **#23 `.env` no `.gitignore`.** A raiz e `samples/orders-sample` passam a ignorar `.env` e `.env.*` (mantendo
  `.env.example`), como o laboratório Node já fazia.

## kit--v0.5.2 — 2026-09-09

Esta versão **altera hooks, rule e skill existentes** — quem aplicou o kit por `apply.sh` recebe as mudanças por PR;
quem usa o plugin, por `claude plugin update`. Nove issues, todas nascidas das revisões externas contra-verificadas
do livro *Cercando a IA*, e um CI mínimo.

- **#1 Hooks fail-closed nos dois harnesses.** `protect-paths.sh` e `guard-bash.sh` negam o que não entendem (JSON
  inválido, vazio, sem `python3`); o Cursor bloqueia a escrita **antes** com `preToolUse` + `failClosed: true`
  (doc lida em 09/09/2026); `afterFileEdit` vira defesa em profundidade; `case "/$f"` casa caminho relativo;
  `tools/test-hooks.sh` prova a matriz (28 casos) e a sincronia das cópias nos samples.
- **#2 Fonte na skill.** `regras-de-negocio` cita Böckeler (Thoughtworks, ago/2026) com a frase literal;
  `docs/referencias.md` nasce no kit; definição única de `inferred`.
- **#3 Casa GERADO produzida.** `npm run generate` escreve `docs/generated/{deps,endpoints,eventos}.md` no
  laboratório (determinístico); `--check` dentro do gate reprova gerado desatualizado; `docs/generated` sai do
  `.cursorignore` (o `impact-analyzer` lê; o hook impede a edição).
- **#4 Contratos.** Ordem por tipo de mudança (acrescentar / retirar / exigir campo novo — expand/contract) na rule e
  nos agentes; testes "campo a mais na resposta → 500" e evento `ClienteAtualizado` contra o AsyncAPI; `default:` →
  `Erro` no `service.yaml`; `js-yaml` declarado.
- **#5 Laboratório.** Rampa do ESLint com dono (papel) e marco absoluto; casos de limite do legado com oráculo
  explícito (sem baseline novo); nota de onde o hook do baseline vale; nota da semente do Faker.
- **#6 DoR com dono por campo.** O porteiro para só por campo do PO; campo do agente entra marcado `inferido`;
  briefings com a coluna Dono; `Confirmed?` da spec do laboratório com quem e quando.
- **#7 Smoke test dos validadores do tlc.** `tools/test-validadores.sh` fixa o estado documentado
  (`docs/tlc-adaptacao.md`): o gate de spec não lê critério (upstream #162) e a dependência inexistente reprova.
- **#8 Agentes.** "Só lê" pela permissão do harness, não pela lista de `tools`; base do diff como parâmetro;
  `oasdiff --fail-on ERR`; 180 dias como padrão do kit.
- **#9 Documento válido fora de artefato de exibição.** `tools/check-documentos.py` (CI) + regra no README e no
  `AGENTS.md` do laboratório; `ERRATA.md` registra o histórico.
- **CI** (`.github/workflows/ci.yml`): `build-cursor.py --check`, `test-hooks.sh`, `check-documentos.py`,
  `test-validadores.sh` (com checkout do tlc) e o gate do laboratório com `generate:check`.

### Antes da tag, já em `main`

- **`ERRATA.md` (09/09/2026)**: página de errata do kit, com a primeira entrada — o documento com dígitos válidos
  na fixture do `trace-finder`, presente nas tags `kit--v0.4.0` a `kit--v0.5.1`. O histórico não foi reescrito; a
  entrada diz o que fazer para quem clonou antes.

- **Correção de exposição de dado (09/09/2026)**: `docs/observability-fixtures/runs/trace-finder.md` usava, como
  exemplo da guarda de LGPD, um número de onze dígitos que **passa** na validação de CPF — num repositório público.
  Trocado por `12345678901`, que reprova na validação: a guarda dispara por formato, então a demonstração continua
  idêntica e o exemplo não pode ser o documento de ninguém. O `CPF_VALIDO` dos testes do laboratório continua válido
  (a RN-ENR-001 valida o documento e o caminho feliz precisa disso), com o comentário dizendo por que ele existe e por
  que não sai de lá. `agents/trace-finder.md`: a guarda passa a se descrever como arame de tropeço por formato, não
  como definição de dado pessoal — ela não pega documento pontuado, e-mail nem telefone, e pode recusar id técnico.
  Achado na revisão externa contra-verificada do cap. 12 do livro; o livro segue fixado em `kit--v0.5.1` e não muda.

## kit--v0.5.1 — 2026-09-03
- **`LICENSE`** (MIT): o manifesto e o catálogo do livro declaravam MIT desde a v0.2, mas o arquivo não existia. Entra em nome da Whitebeard.
- Repositório **público** a partir desta versão. Varredura do histórico inteiro antes de abrir: zero termo da blocklist do livro, zero segredo, zero host/ARN/conta real; quatro arquivos com caminho absoluto da máquina do autor viraram `~/`.
- Manifesto do Cursor sobe de 0.4.0 (estava parado) para 0.5.1, igual ao do Claude. Nenhum template, hook, agente ou skill foi alterado: a versão só acrescenta.

## kit--v0.5.0 — 2026-08-31
- **`docs/licoes-do-metodo.md`**: seis regras nascidas de defeitos reais no segundo repositório onde o kit foi aplicado — afirmação de mecanismo só com `arquivo:linha`; falha de acesso não é evidência de ausência; confiança baixa não recebe aspas; contagem sobre si mesmo se reconta no artefato construído; chave de sanitização sem fronteira de palavra esconde vazamento; e um limiar de forma mede o que é entregue, não o que é escrito. Cada regra traz o defeito de origem e como verificar.
- Manifesto 0.5.0. Nenhum template, hook ou agente existente foi alterado: a versão só acrescenta.

## kit--v0.4.0 — 2026-08-30
- **Sub-agentes de observabilidade (só leitura)**: `trace-finder` (busca canônica por traceId/cid/eventId — logs primeiro, `trace_flags` antes de culpar retenção, guarda de LGPD, replay com `-01` e `eventId` novo), `telemetry-cost-auditor` (custo e ruído com evidência medida; cortes por custo × ruído; nunca `AlwaysOn` global) e `alert-auditor` (alarme existe, mede o certo e **alguém confirmou receber**; pontos cegos em scripts de verificação e docs de infra).
- **`templates/debug-prod.md`**: primeiro movimento por sintoma, coordenadas, trace sob demanda e verdades operacionais — copiado por `apply.sh` para `docs/debug-prod.md`; o `trace-finder` o lê antes de procurar.
- **`docs/observability-fixtures/`**: fixtures sintéticas na forma das saídas reais (logs com `eventName`/`trace_flags`, inventário de séries, alarmes com assinaturas) e, em `runs/`, a saída real de cada agente rodando sobre elas.
- Manifestos 0.4.0 (keyword `observability`); `templates/{AGENTS,CLAUDE}.md` citam os agentes e o `debug-prod.md`.


## kit--v0.3.4 — 2026-08-30
- enrichment-lab: `max-len` 88 também nos `.js/.cjs/.mjs`; comentário do sequenciador reembrulhado.

## kit--v0.3.3 — 2026-08-30
- enrichment-lab: `jest/sequencer-reverso.cjs` + `npm run test:reverso` (roda os arquivos de teste ao contrário para expor dependência de ordem).

## kit--v0.3.2 — 2026-08-30
- enrichment-lab: `max-len` 88 colunas no lint (comentários inclusive; imports e strings isentos); comentários e nomes de teste longos reembrulhados. Nada funcional muda.

## kit--v0.3.1 — 2026-08-30
- fix(enrichment-lab): `npm run build` copia `legacy/*.js` para `dist/` (o `npm run dev` quebrava).

## kit--v0.3.0 — 2026-08-30
- **Novo laboratório `samples/enrichment-lab`** (Node 22 / TypeScript): serviço de enriquecimento de cadastro em miniatura, sintético — contrato em duas camadas (OpenAPI `validateResponses` + JSON Schema 2020-12 + AsyncAPI), fila FIFO em processo com dedup e DLQ, worker com guardas (RN-ENR-001..006), merge por unidade (feature 001 pelo tlc-spec-driven, Verifier com mutantes), legado `legacy/calcula-apto.js` com characterization por snapshot, arquitetura por ADR com dependency-cruiser, rampa de severidade no eslint. Gate `npm run gate` ≈ 9 s, 44 testes.
- **Perfis por stack**: `node-ts/` (`apply.sh --node-ts`) ao lado de `dotnet/`; `templates/AGENTS.md` agnóstico + `templates/profiles/{node-ts,dotnet}.md`; `docs/perfil-node-ts.md` (tabela dos cinco mecanismos nas duas stacks).
- **Hooks**: `format.sh` (despacha por extensão: dotnet format · prettier + eslint); `protect-paths.sh` também bloqueia `__snapshots__/*.snap`; `guard-bash.sh` também bloqueia `jest -u`/`--updateSnapshot`, `npm run baseline`, `npm publish`, `npm version`.
- **Agentes**: `code-reviewer` (agnóstico, com perfil .NET e Node/TS); `dotnet-reviewer` mantido por compatibilidade; `test-designer` cita snapshot + faker.
- **Rules/skills**: globs Node (`**/legacy/**`, `**/contracts/**`, `**/events/**`, `**/*.schema.json`, `src/domain/**`).
- Manifestos 0.3.0 (keywords `node`, `typescript`). `samples/orders-sample` inalterado; em `tools/gen-ebook.py` só o intervalo do `git log` foi fixado em `545d58a..kit--v0.2.0` (antes `..HEAD`, que passaria a listar commits do enrichment-lab) — no HTML do e-book só mudam as linhas de globs novas das rules/skill embutidas (5 linhas).

## kit--v0.2.0 — 2026-08-29
- Plugin Claude Code + Cursor com o tlc-spec-driven como dependência; `samples/orders-sample` (.NET) e e-book "Engenharia com Agentes em .NET".
