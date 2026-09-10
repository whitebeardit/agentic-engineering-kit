#!/usr/bin/env bash
# Bloqueia comandos irreversíveis ou que burlam gates.
#   Claude Code  PreToolUse (Bash)          → exit 2 + stderr
#   Cursor       preToolUse (Shell)         → {"permission":"deny"} (registre com failClosed: true)
#   Cursor       beforeShellExecution       → {"permission":"deny"}
# Fail-closed: entrada ilegível (JSON inválido, vazio, sem python3) NEGA.
input=$(cat)
parsed=$(printf '%s' "$input" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(3)
ev = d.get("hook_event_name", "")
cursor = "cursor_version" in d or ev in ("preToolUse", "beforeShellExecution")
t = d.get("tool_input") or {}
cmd = (t.get("command") if isinstance(t, dict) else None) or d.get("command") or ""
print(("cursor" if cursor else "claude") + "\t" + cmd.replace("\n", " "))
' 2>/dev/null) || parsed=""
if [ -z "$parsed" ]; then
  echo "BLOQUEADO (kit Whitebeard): o hook não conseguiu ler a entrada (JSON inválido, vazio ou sem python3) — fail-closed." >&2
  printf '{"permission":"deny","user_message":"kit: hook sem entrada legível — negado por construção","agent_message":"BLOQUEADO (kit Whitebeard): entrada do hook ilegível; fail-closed. Peça a um humano para conferir o hook."}\n'
  exit 2
fi
kind=${parsed%%$'\t'*}
cmd=${parsed#*$'\t'}
allow() { [ "$kind" = cursor ] && printf '{"permission":"allow"}\n'; exit 0; }
[ -z "$cmd" ] && allow
why=""
case "$cmd" in
  *"git push"*"--force"*|*"git push -f"*)                         why="push forçado" ;;
  *"--no-verify"*)                                                why="--no-verify pula os hooks de commit" ;;
  *"dotnet ef database update"*|*"dotnet ef migrations remove"*)  why="migration aplicada/removida pelo agente" ;;
  *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf \$HOME"*)                    why="remoção destrutiva" ;;
  *"git checkout -- ."*|*"git reset --hard"*)                     why="descarte de trabalho não commitado" ;;
  *"jest -u"*|*"jest --ci -u"*|*"--updateSnapshot"*|*"npm run baseline"*) why="baseline de characterization test só humano aprova (npm run baseline, no terminal)" ;;
  *"npm publish"*|*"npm version"*)                                why="publicação/versionamento é do humano" ;;
esac
[ -z "$why" ] && allow
reason="$why — veja AGENTS.md › Never. Se for realmente necessário, um humano executa."
if [ "$kind" = claude ]; then echo "BLOQUEADO (kit Whitebeard): $reason" >&2; exit 2
else printf '{"permission":"deny","user_message":"kit: comando bloqueado (%s)","agent_message":"BLOQUEADO (kit Whitebeard): %s"}\n' "$why" "$reason"; exit 0; fi
