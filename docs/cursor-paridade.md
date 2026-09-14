# Paridade Claude Code × Cursor no kit

O mesmo repositório serve os dois: `.claude-plugin/` e `.cursor-plugin/` apontam para as mesmas `skills/`, `agents/` e `.mcp.json`.
O que difere é o formato de rules e de hooks — e o que o Cursor não consegue impor.

| Capacidade | Claude Code | Cursor | Fallback no Cursor |
|---|---|---|---|
| Contexto canônico | `CLAUDE.md` = `@AGENTS.md` | `AGENTS.md` (nativo, aninhado) | — |
| Skills (`card-intake`, `run-and-test`, `regras-de-negocio`) | plugin `/kit:…` ou `.claude/skills` | plugin ou `.cursor/skills` (Agent Skills, `paths`) | — |
| Agentes | `agents/*.md` (subagentes) | `agents/*.md` | comportamento de delegação pode diferir; conteúdo é o mesmo |
| Rules por caminho | `rules/*.md` (`paths:`) | `cursor/rules/*.mdc` (`globs:`), geradas por `tools/build-cursor.py` | — |
| tlc-spec-driven | plugin `tlc@whitebeard-kit` (git-subdir → repo TLC) | `npx -y @tech-leads-club/agent-skills@1.4.10 install -s tlc-spec-driven -a cursor -g` | — |
| Aviso de versão do tlc | hook `SessionStart` | hook `sessionStart` (mesmo script) | — |
| Bloquear comando perigoso | `PreToolUse` Bash → exit 2 | `beforeShellExecution` → `{"permission":"deny"}` | — |
| Bloquear **escrita** em segredo/migration/baseline | `PreToolUse` Edit\|Write\|NotebookEdit → exit 2 (antes de escrever) | `preToolUse` (matcher `Write\|Edit\|…`) → `{"permission":"deny"}`, **antes** de escrever — doc do Cursor lida em 2026-09-09 (o evento genérico `preToolUse` não existia na leitura de 30/08) | `afterFileEdit` reverte e registra (defesa em profundidade, não mais o único mecanismo) |
| Allowlist de comandos (`permissions.allow`) | `.claude/settings.json` | sem equivalente | `beforeShellExecution` bloqueia a lista negra; o resto passa pelo prompt de aprovação do Cursor |
| Formatar `.cs` tocado | `PostToolUse` | `afterFileEdit` | — |
| Managed settings / hooks gerenciados (fase 5) | sim | Team/Enterprise hooks (cloud) | — |
| Entrada que o hook não entende (JSON inválido, vazio, sem `python3`) | exit 2 (nega) | `"failClosed": true` no `hooks.json` → nega; sem ele o padrão do Cursor é **fail-open** | — |

O matcher de edição do Claude Code é por nome exato: `Edit|Write|NotebookEdit` (até a v0.5.3 o kit escrevia `MultiEdit`, que a referência de hooks não lista, e deixava o `NotebookEdit` fora — issue #19). O que o agente escreve por `Bash` (`echo > arquivo`, `sed -i`) não passa pelo `protect-paths.sh`: passa pelo `guard-bash.sh`, que só nega os comandos da lista dele.


Regra prática: **os dois hooks negam antes de agir e negam o que não entendem** (fail-closed — `tools/test-hooks.sh` prova a
matriz). O `afterFileEdit` que reverte ficou como defesa em profundidade, não como a regra: era o fallback enquanto o
Cursor não tinha hook pré-escrita (leitura de 30/08/2026). O PR continua sendo o gate.

**Codex, Copilot e o shell**: não há hook. O que vale ali é o que roda no CI (`tools/test-hooks.sh`, o gate do
laboratório, `build-cursor.py --check`) e a revisão do PR — `samples/enrichment-lab/AGENTS.md › Gotchas` diz isso onde
o agente lê.
