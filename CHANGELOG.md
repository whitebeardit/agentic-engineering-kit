# Changelog

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
