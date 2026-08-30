#!/usr/bin/env bash
# PostToolUse (Edit|Write|MultiEdit): formata o arquivo tocado. Nunca trava (exit 0 sempre).
input=$(cat)
f=$(printf '%s' "$input" | python3 -c 'import sys,json; d=json.load(sys.stdin); t=d.get("tool_input",{}); print(t.get("file_path") or t.get("path") or "")' 2>/dev/null)
[ -z "$f" ] && exit 0
case "$f" in
  *.ts|*.js|*.mjs|*.cjs|*.json|*.md|*.yaml|*.yml) ;;
  *) exit 0 ;;
esac
[ -f "$f" ] || exit 0
npx --no-install prettier --log-level silent --write "$f" >/dev/null 2>&1 || true
case "$f" in *.ts|*.js|*.mjs|*.cjs) npx --no-install eslint --fix "$f" >/dev/null 2>&1 || true ;; esac
exit 0
