#!/usr/bin/env bash
# Formata só o .cs tocado, no projeto dono dele. Claude: PostToolUse (Edit|Write|NotebookEdit). Cursor: afterFileEdit.
# MELHOR ESFORÇO, não verificação: sem SDK, sem projeto ou com o formatador falhando, sai 0 e o turno segue — quem
# confere formatação é o gate (`dotnet format <sln> --verify-no-changes`). Falha do formatador vai para o stderr.
# Fronteira de confiança: o `dotnet format` pode restaurar, compilar e rodar analisadores do projeto — só em código
# confiável; em repositório de terceiros, desligue este hook. Até a v0.5.6 a falha era descartada em silêncio (#28).
input=$(cat)
f=$(printf '%s' "$input" | python3 -c 'import sys,json; d=json.load(sys.stdin); print((d.get("tool_input") or d).get("file_path",""))' 2>/dev/null)
case "$f" in *.cs) ;; *) exit 0 ;; esac
command -v dotnet >/dev/null 2>&1 || exit 0
dir=$(dirname "$f")
while [ "$dir" != "/" ] && ! ls "$dir"/*.csproj >/dev/null 2>&1; do dir=$(dirname "$dir"); done
[ "$dir" = "/" ] && exit 0
proj=$(ls "$dir"/*.csproj | head -1)
dotnet format "$proj" --include "$f" --no-restore >/dev/null 2>&1 || echo "[kit] dotnet format falhou em $f (melhor esforço; o gate confere a formatação)" >&2
exit 0
