#!/usr/bin/env bash
# PostToolUse (Edit|Write|MultiEdit) / Cursor afterFileEdit: formata o arquivo tocado conforme a extensão.
# .cs → dotnet format (projeto do arquivo) · .ts/.js/.json/.md/.yaml → prettier (+ eslint --fix em código). Nunca trava (exit 0).
input=$(cat)
f=$(printf '%s' "$input" | python3 -c '
import sys,json
d=json.load(sys.stdin)
t=d.get("tool_input",{})
print(t.get("file_path") or t.get("path") or d.get("file_path") or "")' 2>/dev/null)
[ -z "$f" ] || [ ! -f "$f" ] && exit 0
case "$f" in
  *.cs)
    printf '%s' "$input" | bash "$(dirname "${BASH_SOURCE[0]}")/dotnet-format.sh"; exit 0 ;;
  *.ts|*.tsx|*.js|*.mjs|*.cjs|*.json|*.md|*.yaml|*.yml)
    command -v npx >/dev/null 2>&1 || exit 0
    npx --no-install prettier --log-level silent --write "$f" >/dev/null 2>&1 || true
    case "$f" in *.ts|*.tsx|*.js|*.mjs|*.cjs) npx --no-install eslint --fix "$f" >/dev/null 2>&1 || true ;; esac ;;
esac
exit 0
