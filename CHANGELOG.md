# Changelog

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
