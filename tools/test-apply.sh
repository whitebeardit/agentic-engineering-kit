#!/usr/bin/env bash
# Testes do instalador (bash puro, em diretórios temporários): o que o apply.sh entrega e o que ele imprime.
# Nasceu na v0.5.4 com #16 (as lições do método entregues como rule sem `paths`) e #17 (próximos passos em linhas curtas);
# #27 acrescentou o settings.json por perfil; #10, os casos de escrita segura e o --check.
# Uso: bash tools/test-apply.sh   (exit 0 = tudo ok)
set -u
KIT=$(cd "$(dirname "$0")/.." && pwd)
APPLY="$KIT/apply.sh"
ok=0; fail=0
passa() { ok=$((ok+1)); }
falha() { fail=$((fail+1)); echo "  ✗ $1"; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT

# --- #16: lições do método entregues e carregadas sem paths ---
mkdir -p "$T/claude" "$T/cursor"
out=$(bash "$APPLY" "$T/claude" --claude 2>&1); st=$?
[ "$st" -eq 0 ] && passa || falha "apply.sh --claude saiu com $st"
[ -f "$T/claude/.claude/rules/licoes-do-metodo.md" ] && passa || falha "#16: .claude/rules/licoes-do-metodo.md não foi entregue"
head -1 "$T/claude/.claude/rules/licoes-do-metodo.md" 2>/dev/null | grep -q '^---$' && falha "#16: a rule das lições tem frontmatter (com paths ela não carrega em toda sessão)" || passa
bash "$APPLY" "$T/cursor" --cursor >/dev/null 2>&1
grep -q '^alwaysApply: true$' "$T/cursor/.cursor/rules/licoes-do-metodo.mdc" 2>/dev/null && passa || falha "#16: .cursor/rules/licoes-do-metodo.mdc sem alwaysApply: true"

# --- #17: próximos passos em linhas curtas, com a regra (negar antes) nos dois harnesses ---
fim=$(printf '%s\n' "$out" | tail -4)
[ "$(printf '%s\n' "$fim" | head -1)" = "próximos passos:" ] && passa || falha "#17: a saída não termina com o bloco 'próximos passos:' em linhas próprias"
printf '%s\n' "$fim" | grep -q "negado antes da escrita (Claude Code e Cursor)" && passa || falha "#17: o passo (3) não diz 'negado antes da escrita (Claude Code e Cursor)'"
longas=$(printf '%s\n' "$out" | awk 'length > 100' | grep -c . || true)
[ "$longas" -eq 0 ] && passa || falha "#17: $longas linha(s) da saída com mais de 100 colunas"

# --- #27: o perfil .NET recebe o settings.json sem npm/npx; o genérico continua com eles ---
mkdir -p "$T/dotnet" "$T/generico"
bash "$APPLY" "$T/dotnet" --claude --dotnet >/dev/null 2>&1
bash "$APPLY" "$T/generico" --claude >/dev/null 2>&1
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
# --- #12: a CLI do Tech Leads Club sempre com versão fixa (no apply.sh e nas mensagens do hook de versão) ---
soltas=$(grep -ho '@tech-leads-club/agent-skills[^ `]*' "$KIT/apply.sh" "$KIT/hooks/tlc-version.sh" "$KIT/README.md" "$KIT"/docs/*.md | grep -vc '@tech-leads-club/agent-skills@[0-9]' || true)
[ "$soltas" -eq 0 ] && passa || falha "#12: $soltas chamada(s) da CLI do Tech Leads Club sem versão"
# --- #10: escrita segura (os quatro experimentos da issue, na v0.5.2) e --check ---
# (a) .claude é link simbólico para fora do alvo → recusa, nada escrito nem fora nem dentro
mkdir -p "$T/fora" "$T/link"; ln -s "$T/fora" "$T/link/.claude"
bash "$APPLY" "$T/link" --claude >/dev/null 2>&1; st=$?
[ "$st" -ne 0 ] && passa || falha "#10a: apply.sh aceitou .claude simbólico (exit 0)"
[ -z "$(ls -A "$T/fora")" ] && passa || falha "#10a: escreveu fora do alvo: $(ls -A "$T/fora" | tr '\n' ' ')"
[ ! -e "$T/link/AGENTS.md" ] && passa || falha "#10a: criou arquivos antes de recusar (estado parcial)"
# (b) hook alheio com modo 0644 continua 0644; os hooks do kit saem executáveis
mkdir -p "$T/modo/.claude/hooks"; printf '#!/bin/sh\n' > "$T/modo/.claude/hooks/alheio.sh"; chmod 644 "$T/modo/.claude/hooks/alheio.sh"
bash "$APPLY" "$T/modo" --claude >/dev/null 2>&1
[ "$(stat -c %a "$T/modo/.claude/hooks/alheio.sh")" = "644" ] && passa || falha "#10b: mudou o modo de um hook que não é do kit"
[ -x "$T/modo/.claude/hooks/protect-paths.sh" ] && passa || falha "#10b: hook do kit criado sem permissão de execução"
# (c) CLAUDE.md como link quebrado → recusa antes da primeira escrita, sem estado parcial
mkdir -p "$T/quebrado"; ln -s "$T/nao-existe" "$T/quebrado/CLAUDE.md"
bash "$APPLY" "$T/quebrado" --claude >/dev/null 2>&1; st=$?
[ "$st" -ne 0 ] && [ ! -e "$T/quebrado/AGENTS.md" ] && passa || falha "#10c: link quebrado não foi recusado antes de escrever (exit $st)"
# (d) hook esvaziado: a segunda execução mantém, avisa que difere, e o --check o dá como divergente
mkdir -p "$T/vazio"; bash "$APPLY" "$T/vazio" --claude >/dev/null 2>&1; : > "$T/vazio/.claude/hooks/protect-paths.sh"
out2=$(bash "$APPLY" "$T/vazio" --claude 2>&1)
printf '%s' "$out2" | grep -q 'protect-paths.sh  (difere do kit' && passa || falha "#10d: segunda execução não avisou que o hook esvaziado difere do kit"
[ ! -s "$T/vazio/.claude/hooks/protect-paths.sh" ] && passa || falha "#10d: sobrescreveu o arquivo existente"
bash "$APPLY" "$T/vazio" --claude --check 2>&1 | grep -q 'divergente  .*protect-paths.sh' && passa || falha "#10d: --check não classificou o hook esvaziado como divergente"
printf '%s' "$out2" | grep 'AGENTS.md' | grep -q 'difere' && falha "#10: arquivo igual ao do kit marcado como diferente" || passa
# (e) --check num diretório vazio não escreve nada
mkdir -p "$T/check"; outc=$(bash "$APPLY" "$T/check" --claude --check 2>&1)
[ -z "$(ls -A "$T/check")" ] && passa || falha "#10e: --check escreveu no alvo"
printf '%s' "$outc" | grep -Eq 'check: [1-9][0-9]* novo\(s\), 0 igual\(is\), 0 divergente\(s\)' && passa || falha "#10e: resumo do --check inesperado"
echo "test-apply: $ok ok, $fail falha(s)"
[ "$fail" -eq 0 ]
