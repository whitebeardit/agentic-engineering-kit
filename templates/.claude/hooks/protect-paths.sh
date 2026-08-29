#!/usr/bin/env bash
# PreToolUse (Edit|Write|MultiEdit): bloqueia segredos, migrations e artefatos gerados. exit 2 = bloqueia e explica ao agente.
input=$(cat)
f=$(printf '%s' "$input" | python3 -c 'import sys,json
d=json.load(sys.stdin); t=d.get("tool_input",{}); print(t.get("file_path") or t.get("path") or "")' 2>/dev/null)
[ -z "$f" ] && exit 0
case "$f" in
  *.env|*.env.*|*/appsettings.*.json|*/secrets/*|*/Migrations/*|*/migrations/*|*/docs/generated/*|*.verified.txt)
    echo "BLOQUEADO (kit Whitebeard): '$f' é segredo, migration, artefato gerado ou baseline de characterization test. Mudança aqui passa por humano em PR separado — veja CLAUDE.md > Never." >&2
    exit 2 ;;
esac
exit 0
