#!/usr/bin/env bash
# Bloqueia segredos, migrations, artefatos gerados e baselines de characterization test (.verified.txt e snapshots do jest).
#   Claude Code  PreToolUse (Edit|Write|MultiEdit)  → exit 2 + stderr (antes de escrever)
#   Cursor       preToolUse (Write|Edit|Read…)      → {"permission":"deny"} (antes de escrever; registre com failClosed: true)
#   Cursor       beforeReadFile                     → {"permission":"deny"}
#   Cursor       afterFileEdit                      → reverte + avisa (defesa em profundidade; não bloqueia)
# Fail-closed: entrada que o hook não entende (JSON inválido, vazio, sem python3) NEGA — um hook que deixa passar o que
# não entende é placa, não catraca (livro *Cercando a IA*, cap. 4; lição L-025).
input=$(cat)
parsed=$(printf '%s' "$input" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(3)
ev = d.get("hook_event_name", "")
cursor = "cursor_version" in d or ev in ("preToolUse", "beforeReadFile", "afterFileEdit")
t = d.get("tool_input") or {}
def caminho(*fontes):
    for f in fontes:
        for k in ("file_path", "path", "filePath", "target_file", "notebook_path"):
            v = f.get(k) if isinstance(f, dict) else None
            if v: return v
    return ""
if cursor:
    if ev == "afterFileEdit" or "edits" in d: kind = "cursor-edit"
    elif ev == "beforeReadFile": kind = "cursor-read"
    else: kind = "cursor-pre"
    print(kind + "\t" + caminho(t, d))
else:
    print("claude\t" + caminho(t, d))
' 2>/dev/null) || parsed=""
if [ -z "$parsed" ]; then
  echo "BLOQUEADO (kit Whitebeard): o hook não conseguiu ler a entrada (JSON inválido, vazio ou sem python3) — fail-closed." >&2
  printf '{"permission":"deny","user_message":"kit: hook sem entrada legível — negado por construção","agent_message":"BLOQUEADO (kit Whitebeard): entrada do hook ilegível; fail-closed. Peça a um humano para conferir o hook."}\n'
  exit 2
fi
kind=${parsed%%$'\t'*}
f=${parsed#*$'\t'}
allow() { case "$kind" in cursor-*) printf '{"permission":"allow"}\n';; esac; exit 0; }
[ -z "$f" ] && allow
case "/$f" in
  *.env|*.env.*|*/appsettings.*.json|*/secrets/*|*/Migrations/*|*/migrations/*|*/docs/generated/*|*.verified.txt|*/__snapshots__/*|*.snap) ;;
  *) allow ;;
esac
reason="'$f' é segredo, migration, artefato gerado ou baseline de characterization test. Mudança aqui passa por humano em PR separado — veja AGENTS.md › Never."
case "$kind" in
  claude)
    echo "BLOQUEADO (kit Whitebeard): $reason" >&2; exit 2 ;;
  cursor-pre|cursor-read)
    printf '{"permission":"deny","user_message":"kit: acesso negado a %s","agent_message":"BLOQUEADO (kit Whitebeard): %s"}\n' "$f" "$reason"; exit 0 ;;
  cursor-edit)
    if git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then git checkout -- "$f" 2>/dev/null; act="revertida"; else rm -f -- "$f"; act="removida"; fi
    printf '{"user_message":"kit: edição %s em %s","agent_message":"Edição %s (kit Whitebeard): %s"}\n' "$act" "$f" "$act" "$reason"; exit 0 ;;
esac
exit 0
