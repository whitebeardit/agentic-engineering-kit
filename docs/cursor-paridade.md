# Paridade Claude Code × Cursor no kit

O mesmo repositório serve os dois: `.claude-plugin/` e `.cursor-plugin/` apontam para as mesmas `skills/`, `agents/` e `.mcp.json`.
O que difere é o formato de rules e de hooks — e o que o Cursor não consegue impor.

| Capacidade | Claude Code | Cursor | Fallback no Cursor |
|---|---|---|---|
| Contexto canônico | `CLAUDE.md` = `@AGENTS.md` | `AGENTS.md` (nativo, aninhado) | — |
| Skills (`card-intake`, `run-and-test`, `regras-de-negocio`) | plugin `/kit:…` ou `.claude/skills` | plugin ou `.cursor/skills` (Agent Skills, `paths`) | — |
| Agentes | `agents/*.md` (subagentes) | `agents/*.md` | comportamento de delegação pode diferir; conteúdo é o mesmo |
| Rules por caminho | `rules/*.md` (`paths:`) | `cursor/rules/*.mdc` (`globs:`), geradas por `tools/build-cursor.py` | — |
| tlc-spec-driven | plugin `tlc@whitebeard-kit` (git-subdir → repo TLC) | `npx -y @tech-leads-club/agent-skills install -s tlc-spec-driven -a cursor -g` | — |
| Aviso de versão do tlc | hook `SessionStart` | hook `sessionStart` (mesmo script) | — |
| Bloquear comando perigoso | `PreToolUse` Bash → exit 2 | `beforeShellExecution` → `{"permission":"deny"}` | — |
| Bloquear **escrita** em segredo/migration/baseline | `PreToolUse` Edit\|Write → exit 2 (antes de escrever) | **não existe hook pré-escrita** | `beforeReadFile` nega ler segredos + `.cursorignore`; `afterFileEdit` **reverte** o arquivo (`git checkout --` / remove) e avisa o agente; garantia final = CODEOWNERS + branch protection |
| Allowlist de comandos (`permissions.allow`) | `.claude/settings.json` | sem equivalente | `beforeShellExecution` bloqueia a lista negra; o resto passa pelo prompt de aprovação do Cursor |
| Formatar `.cs` tocado | `PostToolUse` | `afterFileEdit` | — |
| Managed settings / hooks gerenciados (fase 5) | sim | Team/Enterprise hooks (cloud) | — |

Regra prática: **no Cursor, o que não dá para impedir, dá para desfazer e registrar** — e o PR continua sendo o gate.
