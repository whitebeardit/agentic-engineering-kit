#!/usr/bin/env bash
# Bloqueia segredos, migrations, artefatos gerados e baselines de characterization test (.verified.txt e snapshots do jest).
# Claude Code: PreToolUse (Edit|Write|MultiEdit) → exit 2 + stderr.  Cursor: beforeReadFile → JSON deny; afterFileEdit → reverte + avisa.
input=$(cat)
read -r kind f < <(printf '%s' "$input" | python3 -c '
import sys,json
d=json.load(sys.stdin)
if "tool_input" in d:
    t=d["tool_input"]; print("claude", t.get("file_path") or t.get("path") or "")
else:
    print("cursor-edit" if "edits" in d else "cursor", d.get("file_path") or "")' 2>/dev/null)
[ -z "$f" ] && exit 0
case "$f" in
  *.env|*.env.*|*/appsettings.*.json|*/secrets/*|*/Migrations/*|*/migrations/*|*/docs/generated/*|*.verified.txt|*/__snapshots__/*|*.snap) ;;
  *) exit 0 ;;
esac
reason="'$f' é segredo, migration, artefato gerado ou baseline de characterization test. Mudança aqui passa por humano em PR separado — veja AGENTS.md › Never."
case "$kind" in
  claude)      echo "BLOQUEADO (kit Whitebeard): $reason" >&2; exit 2 ;;
  cursor)      printf '{"permission":"deny","user_message":"kit: acesso negado a %s","agent_message":"BLOQUEADO (kit Whitebeard): %s"}\n' "$f" "$reason"; exit 0 ;;
  cursor-edit) if git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then git checkout -- "$f" 2>/dev/null; act="revertida"; else rm -f -- "$f"; act="removida"; fi
               printf '{"user_message":"kit: edição %s em %s","agent_message":"Edição %s (kit Whitebeard): %s"}\n' "$act" "$f" "$act" "$reason"; exit 0 ;;
esac
exit 0
