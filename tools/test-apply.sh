#!/usr/bin/env bash
# Testes do instalador (bash puro, em diretórios temporários): o que o apply.sh entrega e o que ele imprime.
# Nasceu na v0.5.4 com #16 (as lições do método entregues como rule sem `paths`) e #17 (próximos passos em linhas curtas);
# #27 acrescentou o settings.json por perfil; #10 acrescenta os casos de escrita segura.
# Uso: bash tools/test-apply.sh   (exit 0 = tudo ok)
set -u
KIT=$(cd "$(dirname "$0")/.." && pwd)
ok=0; fail=0
passa() { ok=$((ok+1)); }
falha() { fail=$((fail+1)); echo "  ✗ $1"; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT

# --- #16: lições do método entregues e carregadas sem paths ---
mkdir -p "$T/claude" "$T/cursor"
out=$(bash "$KIT/apply.sh" "$T/claude" --claude 2>&1); st=$?
[ "$st" -eq 0 ] && passa || falha "apply.sh --claude saiu com $st"
[ -f "$T/claude/.claude/rules/licoes-do-metodo.md" ] && passa || falha "#16: .claude/rules/licoes-do-metodo.md não foi entregue"
head -1 "$T/claude/.claude/rules/licoes-do-metodo.md" 2>/dev/null | grep -q '^---$' && falha "#16: a rule das lições tem frontmatter (com paths ela não carrega em toda sessão)" || passa
bash "$KIT/apply.sh" "$T/cursor" --cursor >/dev/null 2>&1
grep -q '^alwaysApply: true$' "$T/cursor/.cursor/rules/licoes-do-metodo.mdc" 2>/dev/null && passa || falha "#16: .cursor/rules/licoes-do-metodo.mdc sem alwaysApply: true"

# --- #17: próximos passos em linhas curtas, com a regra (negar antes) nos dois harnesses ---
fim=$(printf '%s\n' "$out" | tail -4)
[ "$(printf '%s\n' "$fim" | head -1)" = "próximos passos:" ] && passa || falha "#17: a saída não termina com o bloco 'próximos passos:' em linhas próprias"
printf '%s\n' "$fim" | grep -q "negado antes da escrita (Claude Code e Cursor)" && passa || falha "#17: o passo (3) não diz 'negado antes da escrita (Claude Code e Cursor)'"
longas=$(printf '%s\n' "$out" | awk 'length > 100' | grep -c . || true)
[ "$longas" -eq 0 ] && passa || falha "#17: $longas linha(s) da saída com mais de 100 colunas"

# --- #27: o perfil .NET recebe o settings.json sem npm/npx; o genérico continua com eles ---
mkdir -p "$T/dotnet" "$T/generico"
bash "$KIT/apply.sh" "$T/dotnet" --claude --dotnet >/dev/null 2>&1
bash "$KIT/apply.sh" "$T/generico" --claude >/dev/null 2>&1
eco() { python3 -c 'import json,sys; a=json.load(open(sys.argv[1]))["permissions"]["allow"]; print(sum(x.startswith(("Bash(npm","Bash(npx")) for x in a))' "$1" 2>/dev/null || echo erro; }
[ "$(eco "$T/dotnet/.claude/settings.json")" = "0" ] && passa || falha "#27: apply.sh --dotnet entregou permissões npm/npx"
[ "$(eco "$T/generico/.claude/settings.json")" != "0" ] && passa || falha "#27: o settings.json genérico perdeu as permissões npm/npx"
# o template .NET não deriva: é o genérico sem npm/npx, e é o que o exemplo .NET usa
python3 - "$KIT" <<'PY' && passa || falha "#27: templates/.claude/settings.dotnet.json derivou do genérico ou do exemplo .NET"
import json, sys
k = sys.argv[1]
g = json.load(open(f"{k}/templates/.claude/settings.json")); d = json.load(open(f"{k}/templates/.claude/settings.dotnet.json"))
s = json.load(open(f"{k}/samples/orders-sample/.claude/settings.json"))
esperado = [a for a in g["permissions"]["allow"] if not a.startswith(("Bash(npm", "Bash(npx"))]
ok = (d["permissions"]["allow"] == esperado and d["permissions"]["deny"] == g["permissions"]["deny"] and d["hooks"] == g["hooks"]
      and s["permissions"]["allow"] == esperado)
sys.exit(0 if ok else 1)
PY
echo "test-apply: $ok ok, $fail falha(s)"
[ "$fail" -eq 0 ]
