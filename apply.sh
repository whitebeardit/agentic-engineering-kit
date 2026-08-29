#!/usr/bin/env bash
# apply.sh — implanta o que é ENFORCEMENT do kit num repositório, sem sobrescrever o que já existe.
# Skills, agentes e MCP vêm do plugin (Claude: kit@whitebeard-kit · Cursor: plugin kit) — use --standalone para copiá-los.
#
# uso: apply.sh /caminho/do/repo [--claude] [--cursor] [--standalone] [--with-tlc] [--dotnet] [--root]
#   --claude      (default) AGENTS.md, CLAUDE.md, .claude/settings.json (permissões + hooks), .claude/hooks, .claude/rules, DoR, ADR template
#   --cursor      AGENTS.md, .cursor/hooks.json, .cursor/hooks, .cursor/rules (*.mdc), .cursorignore
#   --standalone  também copia skills/ e agents/ para .claude/ e/ou .cursor/ (para quem não usa marketplace)
#   --with-tlc    instala o tlc-spec-driven ORIGINAL (Claude: marketplace do kit · Cursor: CLI do Tech Leads Club) — nunca copiado
#   --dotnet      Directory.Build.props, .editorconfig, nuget.config, exemplo de teste de arquitetura
#   --root        usa AGENTS.root.md (workspace pai) em vez de AGENTS.md (serviço)
set -euo pipefail
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:?informe o caminho do repositório}"; shift || true
CLAUDE=0; CURSOR=0; STANDALONE=0; WITH_TLC=0; DOTNET=0; ROOT=0
for a in "$@"; do case "$a" in
  --claude) CLAUDE=1;; --cursor) CURSOR=1;; --standalone) STANDALONE=1;; --with-tlc) WITH_TLC=1;; --dotnet) DOTNET=1;; --root) ROOT=1;;
  *) echo "flag desconhecida: $a" >&2; exit 1;; esac; done
[ $CLAUDE -eq 0 ] && [ $CURSOR -eq 0 ] && CLAUDE=1
[ -d "$TARGET" ] || { echo "diretório não existe: $TARGET" >&2; exit 1; }
copy() { if [ -e "$2" ]; then echo "  = mantido   $2"; else mkdir -p "$(dirname "$2")"; cp "$1" "$2"; echo "  + criado    $2"; fi; }

echo "kit → $TARGET"
# comum: contexto canônico + docs
if [ $ROOT -eq 1 ]; then copy "$KIT/templates/AGENTS.root.md" "$TARGET/AGENTS.md"; else copy "$KIT/templates/AGENTS.md" "$TARGET/AGENTS.md"; fi
copy "$KIT/docs/definition-of-ready.md" "$TARGET/docs/definition-of-ready.md"
copy "$KIT/docs/adr/0000-template.md" "$TARGET/docs/adr/0000-template.md"

if [ $CLAUDE -eq 1 ]; then
  copy "$KIT/templates/CLAUDE.md" "$TARGET/CLAUDE.md"
  copy "$KIT/templates/.claude/settings.json" "$TARGET/.claude/settings.json"
  for f in protect-paths.sh guard-bash.sh dotnet-format.sh; do copy "$KIT/hooks/$f" "$TARGET/.claude/hooks/$f"; done
  for f in "$KIT"/rules/*.md; do copy "$f" "$TARGET/.claude/rules/$(basename "$f")"; done
  chmod +x "$TARGET"/.claude/hooks/*.sh
  if [ $STANDALONE -eq 1 ]; then
    for d in "$KIT"/skills/*/; do n=$(basename "$d"); copy "$d/SKILL.md" "$TARGET/.claude/skills/$n/SKILL.md"; done
    for f in "$KIT"/agents/*.md; do copy "$f" "$TARGET/.claude/agents/$(basename "$f")"; done
    copy "$KIT/hooks/tlc-version.sh" "$TARGET/.claude/hooks/tlc-version.sh"
    echo "  ! standalone: adicione ao .claude/settings.json o hook SessionStart → .claude/hooks/tlc-version.sh (ver hooks/hooks.json do kit)"
  fi
fi

if [ $CURSOR -eq 1 ]; then
  copy "$KIT/templates/.cursor/hooks.json" "$TARGET/.cursor/hooks.json"
  for f in protect-paths.sh guard-bash.sh dotnet-format.sh tlc-version.sh; do copy "$KIT/hooks/$f" "$TARGET/.cursor/hooks/$f"; done
  for f in "$KIT"/cursor/rules/*.mdc; do copy "$f" "$TARGET/.cursor/rules/$(basename "$f")"; done
  copy "$KIT/templates/.cursorignore" "$TARGET/.cursorignore"
  chmod +x "$TARGET"/.cursor/hooks/*.sh
  if [ $STANDALONE -eq 1 ]; then
    for d in "$KIT"/skills/*/; do n=$(basename "$d"); copy "$d/SKILL.md" "$TARGET/.cursor/skills/$n/SKILL.md"; done
    for f in "$KIT"/agents/*.md; do copy "$f" "$TARGET/.cursor/agents/$(basename "$f")"; done
  fi
fi

if [ $DOTNET -eq 1 ]; then
  copy "$KIT/dotnet/Directory.Build.props" "$TARGET/Directory.Build.props"
  copy "$KIT/dotnet/.editorconfig" "$TARGET/.editorconfig"
  copy "$KIT/dotnet/nuget.config" "$TARGET/nuget.config"
  copy "$KIT/dotnet/ArchitectureTests.example.cs" "$TARGET/docs/ArchitectureTests.example.cs"
fi

if [ $WITH_TLC -eq 1 ]; then
  echo
  if [ $CLAUDE -eq 1 ]; then
    if command -v claude >/dev/null 2>&1; then
      (cd "$TARGET" && claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git 2>/dev/null || true; claude plugin install kit@whitebeard-kit) || echo "  ! instale manualmente: claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git && claude plugin install kit@whitebeard-kit"
    else echo "  ! claude não encontrado. Depois: claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git && claude plugin install kit@whitebeard-kit"; fi
    echo "  atualizar: claude plugin update tlc@whitebeard-kit   (ative auto-update em /plugin › Marketplaces)"
  fi
  if [ $CURSOR -eq 1 ]; then
    if command -v npx >/dev/null 2>&1; then npx -y @tech-leads-club/agent-skills install -s tlc-spec-driven -a cursor -g || echo "  ! falhou; rode: npx -y @tech-leads-club/agent-skills install -s tlc-spec-driven -a cursor -g"
    else echo "  ! npx não encontrado. Depois: npx -y @tech-leads-club/agent-skills install -s tlc-spec-driven -a cursor -g"; fi
    echo "  atualizar: npx -y @tech-leads-club/agent-skills update -s tlc-spec-driven"
  fi
  echo "  tlc-spec-driven © Tech Leads Club (CC-BY-4.0) — sempre o original do GitHub deles; ver NOTICE.md"
fi
echo
echo "próximos passos: (1) preencha AGENTS.md (comandos com custo, gotchas, Never, matriz de testes); (2) abra o agente e rode /context; (3) tente editar .env — deve ser bloqueado (Claude) ou revertido (Cursor)."
