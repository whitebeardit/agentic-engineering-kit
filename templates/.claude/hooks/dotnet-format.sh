#!/usr/bin/env bash
# PostToolUse (Edit|Write|MultiEdit): formata só o .cs tocado, no projeto dono dele. Nunca falha o turno.
input=$(cat)
f=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)
case "$f" in *.cs) ;; *) exit 0 ;; esac
command -v dotnet >/dev/null 2>&1 || exit 0
dir=$(dirname "$f")
while [ "$dir" != "/" ] && ! ls "$dir"/*.csproj >/dev/null 2>&1; do dir=$(dirname "$dir"); done
[ "$dir" = "/" ] && exit 0
proj=$(ls "$dir"/*.csproj | head -1)
dotnet format "$proj" --include "$f" --no-restore >/dev/null 2>&1 || true
exit 0
