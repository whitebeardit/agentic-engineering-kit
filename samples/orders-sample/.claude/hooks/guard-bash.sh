#!/usr/bin/env bash
# PreToolUse (Bash): bloqueia comandos irreversíveis ou que burlam gates. exit 2 = bloqueia e explica ao agente.
input=$(cat)
cmd=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
[ -z "$cmd" ] && exit 0
block() { echo "BLOQUEADO (kit Whitebeard): $1 — veja CLAUDE.md > Never. Se for realmente necessário, um humano executa." >&2; exit 2; }
case "$cmd" in
  *"git push"*"--force"*|*"git push -f"*)              block "push forçado" ;;
  *"--no-verify"*)                                     block "--no-verify pula os hooks de commit" ;;
  *"dotnet ef database update"*|*"dotnet ef migrations remove"*) block "migration aplicada/removida pelo agente" ;;
  *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf \$HOME"*)         block "remoção destrutiva" ;;
  *"git checkout -- ."*|*"git reset --hard"*)          block "descarte de trabalho não commitado" ;;
esac
exit 0
