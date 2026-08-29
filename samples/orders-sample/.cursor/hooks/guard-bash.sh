#!/usr/bin/env bash
# Bloqueia comandos irreversíveis ou que burlam gates. Claude Code: PreToolUse (Bash) → exit 2. Cursor: beforeShellExecution → JSON deny.
input=$(cat)
read -r kind cmd < <(printf '%s' "$input" | python3 -c '
import sys,json
d=json.load(sys.stdin)
if "tool_input" in d: print("claude", d["tool_input"].get("command","").replace("\n"," "))
else: print("cursor", d.get("command","").replace("\n"," "))' 2>/dev/null)
[ -z "$cmd" ] && exit 0
why=""
case "$cmd" in
  *"git push"*"--force"*|*"git push -f"*)                         why="push forçado" ;;
  *"--no-verify"*)                                                why="--no-verify pula os hooks de commit" ;;
  *"dotnet ef database update"*|*"dotnet ef migrations remove"*)  why="migration aplicada/removida pelo agente" ;;
  *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf \$HOME"*)                    why="remoção destrutiva" ;;
  *"git checkout -- ."*|*"git reset --hard"*)                     why="descarte de trabalho não commitado" ;;
esac
[ -z "$why" ] && exit 0
reason="$why — veja AGENTS.md › Never. Se for realmente necessário, um humano executa."
if [ "$kind" = "claude" ]; then echo "BLOQUEADO (kit Whitebeard): $reason" >&2; exit 2
else printf '{"permission":"deny","user_message":"kit: comando bloqueado (%s)","agent_message":"BLOQUEADO (kit Whitebeard): %s"}\n' "$why" "$reason"; exit 0; fi
