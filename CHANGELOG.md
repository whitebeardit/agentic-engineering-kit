# Changelog

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
