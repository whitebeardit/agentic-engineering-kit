#!/usr/bin/env bash
# apply.sh — implanta o kit num repositório sem sobrescrever o que já existe.
# uso: apply.sh /caminho/do/repo [--dotnet] [--root]
#   --dotnet  copia Directory.Build.props, .editorconfig e o exemplo de teste de arquitetura
#   --root    usa CLAUDE.root.md (workspace pai) em vez de CLAUDE.service.md
set -euo pipefail
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:?informe o caminho do repositório}"; shift || true
DOTNET=0; ROOT=0
for a in "$@"; do case "$a" in --dotnet) DOTNET=1;; --root) ROOT=1;; esac; done
[ -d "$TARGET" ] || { echo "diretório não existe: $TARGET" >&2; exit 1; }

copy() { # copy <origem> <destino>
  if [ -e "$2" ]; then echo "  = mantido   $2"; else mkdir -p "$(dirname "$2")"; cp "$1" "$2"; echo "  + criado    $2"; fi
}

echo "kit → $TARGET"
if [ "$ROOT" = 1 ]; then copy "$KIT/templates/CLAUDE.root.md" "$TARGET/CLAUDE.md"
else copy "$KIT/templates/CLAUDE.service.md" "$TARGET/CLAUDE.md"; fi
copy "$KIT/templates/.claude/settings.json" "$TARGET/.claude/settings.json"
for f in "$KIT"/templates/.claude/hooks/*.sh; do copy "$f" "$TARGET/.claude/hooks/$(basename "$f")"; done
chmod +x "$TARGET"/.claude/hooks/*.sh
for f in "$KIT"/templates/.claude/rules/*.md; do copy "$f" "$TARGET/.claude/rules/$(basename "$f")"; done
for f in "$KIT"/templates/.claude/agents/*.md; do copy "$f" "$TARGET/.claude/agents/$(basename "$f")"; done
for d in "$KIT"/templates/.claude/skills/*/; do n=$(basename "$d"); copy "$d/SKILL.md" "$TARGET/.claude/skills/$n/SKILL.md"; done
copy "$KIT/docs/definition-of-ready.md" "$TARGET/docs/definition-of-ready.md"
copy "$KIT/docs/adr/0000-template.md" "$TARGET/docs/adr/0000-template.md"
mkdir -p "$TARGET/specs"; copy "$KIT/docs/spec-template/README.md" "$TARGET/specs/README.md"
if [ "$DOTNET" = 1 ]; then
  copy "$KIT/dotnet/Directory.Build.props" "$TARGET/Directory.Build.props"
  copy "$KIT/dotnet/.editorconfig" "$TARGET/.editorconfig"
  copy "$KIT/dotnet/nuget.config" "$TARGET/nuget.config"
  copy "$KIT/dotnet/ArchitectureTests.example.cs" "$TARGET/docs/ArchitectureTests.example.cs"
fi
echo
echo "próximos passos: (1) preencha CLAUDE.md (comandos, custos, Never); (2) claude → /context; (3) tente editar .env — deve ser bloqueado."
