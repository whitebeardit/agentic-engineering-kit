#!/usr/bin/env bash
# Smoke test dos validadores do tlc-spec-driven que o kit instala como dependência (AD-032 do livro: não fixar,
# registrar). Roda validate_spec.py e validate_tasks.py contra a spec e as tasks do laboratório e contra mutantes
# deliberados, e compara com o ESTADO DOCUMENTADO em docs/tlc-adaptacao.md:
#   - spec íntegra → 0                                  (esperado)
#   - spec com critério 1 trocado por prosa vaga → 0     (esperado HOJE: o gate não lê critério — upstream #162 aberta)
#   - tasks íntegras → 0                                 (esperado)
#   - tasks com "Depends on: T99" → ≠ 0                  (esperado: a checagem de dependência funciona)
# Qualquer desvio do documentado sai 1 — inclusive o upstream corrigir o #162: aí é hora de atualizar a doc.
# Onde estão os scripts: $TLC_DIR, ou o cache de plugins do Claude Code, ou um checkout em .tlc/ (CI).
set -u
KIT=$(cd "$(dirname "$0")/.." && pwd)
SPEC="$KIT/samples/enrichment-lab/.specs/features/001-merge-por-unidade/spec.md"
TASKS="$KIT/samples/enrichment-lab/.specs/features/001-merge-por-unidade/tasks.md"
dir=${TLC_DIR:-}
if [ -z "$dir" ]; then
  for c in "$HOME"/.claude/plugins/cache/*/tlc/*/scripts "$KIT"/.tlc/packages/skills-catalog/skills/*/tlc-spec-driven/scripts; do
    [ -f "$c/validate_spec.py" ] && { dir=$c; break; }
  done
fi
[ -f "${dir:-/nonexistent}/validate_spec.py" ] || { echo "test-validadores: scripts do tlc não encontrados (defina TLC_DIR)"; exit 1; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
ok=0; fail=0
esperado() { # nome · esperado(0|nonzero) · exit real
  if { [ "$2" = 0 ] && [ "$3" -eq 0 ]; } || { [ "$2" = nonzero ] && [ "$3" -ne 0 ]; }; then ok=$((ok+1)); else fail=$((fail+1)); echo "  ✗ $1: exit $3, esperado $2"; fi
}
python3 "$dir/validate_spec.py" "$SPEC" >/dev/null 2>&1; esperado "spec íntegra" 0 $?
python3 - "$SPEC" "$T/spec-mutante.md" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
m, n = re.subn(r"^(\s*1\.\s+).*$", r"\1O sistema deve fazer a coisa certa quando der.", s, count=1, flags=re.M)
assert n == 1, "não achei o critério 1"
open(sys.argv[2], "w", encoding="utf-8").write(m)
PY
python3 "$dir/validate_spec.py" "$T/spec-mutante.md" >/dev/null 2>&1; st=$?
esperado "spec com critério vago — documentado: passa (upstream #162)" 0 $st
[ "$st" -ne 0 ] && echo "  ! o gate de spec passou a reprovar critério vago: atualize docs/tlc-adaptacao.md (e comemore)"
python3 "$dir/validate_tasks.py" "$TASKS" >/dev/null 2>&1; esperado "tasks íntegras" 0 $?
python3 - "$TASKS" "$T/tasks-mutante.md" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
m, n = re.subn(r"^(\*{0,2}Depends on\*{0,2}\s*:\s*).*$", r"\1T99", s, count=1, flags=re.M)
if n == 0:
    m, n = re.subn(r"^(### T1\b[^\n]*\n)", r"\1**Depends on**: T99\n", s, count=1, flags=re.M)
assert n == 1, "não achei onde inserir a dependência"
open(sys.argv[2], "w", encoding="utf-8").write(m)
PY
python3 "$dir/validate_tasks.py" "$T/tasks-mutante.md" >/dev/null 2>&1; esperado "tasks com dependência inexistente → reprova" nonzero $?
echo "test-validadores: $ok ok, $fail falha(s) · scripts: $dir"
[ "$fail" -eq 0 ]
