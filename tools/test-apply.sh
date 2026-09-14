#!/usr/bin/env bash
# Testes do instalador (bash puro, em diretórios temporários): o que o apply.sh entrega e o que ele imprime.
# Nasceu na v0.5.4 com #16 (as lições do método entregues como rule sem `paths`) e #17 (próximos passos em linhas curtas);
# as issues do instalador (#10, #27) acrescentam casos aqui.
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

echo "test-apply: $ok ok, $fail falha(s)"
[ "$fail" -eq 0 ]
