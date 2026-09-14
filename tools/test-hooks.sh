#!/usr/bin/env bash
# Matriz de testes dos hooks (bash puro): superfície (Claude Code × Cursor) × bloqueia/passa × caminho relativo/absoluto
# × entrada inválida (JSON quebrado, vazio, sem python3). Fail-closed: o que o hook não entende, ele nega.
# Também prova o afterFileEdit (reverte) e que as cópias nos samples são idênticas a hooks/.
# Uso: bash tools/test-hooks.sh   (exit 0 = tudo ok)
set -u
KIT=$(cd "$(dirname "$0")/.." && pwd)
PP="$KIT/hooks/protect-paths.sh"; GB="$KIT/hooks/guard-bash.sh"
ok=0; fail=0
check() { # nome · esperado-exit · esperado-stdout(regex ou "") · script · json
  local nome=$1 exp=$2 rx=$3 script=$4 json=$5 out st
  out=$(printf '%s' "$json" | bash "$script" 2>/dev/null); st=$?
  if [ "$st" -eq "$exp" ] && { [ -z "$rx" ] || printf '%s' "$out" | grep -Eq "$rx"; }; then ok=$((ok+1)); else fail=$((fail+1)); echo "  ✗ $nome (exit $st, esperado $exp; stdout: ${out:0:80})"; fi
}
C='"session_id":"s","hook_event_name":"PreToolUse","cwd":"/repo"'
K='"conversation_id":"c","cursor_version":"1.0","hook_event_name":"preToolUse","workspace_roots":["/repo"]'
# --- protect-paths: Claude Code ---
check "claude Write .env (relativo)"            2 ''                       "$PP" "{$C,\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\".env\"}}"
check "claude Edit docs/generated (absoluto)"   2 ''                       "$PP" "{$C,\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"/repo/docs/generated/deps.md\"}}"
check "claude Write snapshot (relativo)"        2 ''                       "$PP" "{$C,\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"src/__tests__/__snapshots__/a.snap\"}}"
check "claude Write src livre"                  0 ''                       "$PP" "{$C,\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"src/a.ts\"}}"
# --- protect-paths: Cursor preToolUse / beforeReadFile ---
check "cursor preToolUse Write .env"            0 '"permission":"deny"'    "$PP" "{$K,\"tool_name\":\"Write\",\"tool_input\":{\"path\":\"/repo/.env\"}}"
check "cursor preToolUse Write migrations"      0 '"permission":"deny"'    "$PP" "{$K,\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"db/migrations/001.sql\"}}"
check "cursor preToolUse Write livre → allow"   0 '"permission":"allow"'   "$PP" "{$K,\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"src/a.ts\"}}"
check "cursor preToolUse Shell (sem caminho) → allow" 0 '"permission":"allow"' "$PP" "{$K,\"tool_name\":\"Shell\",\"tool_input\":{\"command\":\"ls\"}}"
check "cursor beforeReadFile secrets"           0 '"permission":"deny"'    "$PP" "{$K,\"hook_event_name\":\"beforeReadFile\",\"file_path\":\"/repo/config/secrets/x.json\"}"
check "cursor beforeReadFile livre → allow"     0 '"permission":"allow"'   "$PP" "{$K,\"hook_event_name\":\"beforeReadFile\",\"file_path\":\"/repo/README.md\"}"
# --- fail-closed ---
check "protect JSON inválido → nega"            2 '"permission":"deny"'    "$PP" '{isto não é json'
check "protect entrada vazia → nega"            2 '"permission":"deny"'    "$PP" ''
check "guard JSON inválido → nega"              2 '"permission":"deny"'    "$GB" 'nope'
out=$(printf '%s' "{$C,\"tool_input\":{\"file_path\":\".env\"}}" | PATH="$(mktemp -d)" /bin/bash "$PP" 2>/dev/null); st=$?
if [ "$st" -eq 2 ]; then ok=$((ok+1)); else fail=$((fail+1)); echo "  ✗ sem python3 → nega (exit $st)"; fi
# --- guard-bash ---
check "claude Bash git push --force"            2 ''                       "$GB" "{$C,\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push --force origin main\"}}"
check "claude Bash npm test → passa"            0 ''                       "$GB" "{$C,\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"npm test\"}}"
check "cursor preToolUse Shell jest -u → deny"  0 '"permission":"deny"'    "$GB" "{$K,\"tool_name\":\"Shell\",\"tool_input\":{\"command\":\"npx jest -u\"}}"
check "cursor beforeShellExecution --no-verify" 0 '"permission":"deny"'    "$GB" "{$K,\"hook_event_name\":\"beforeShellExecution\",\"command\":\"git commit --no-verify -m x\"}"
check "cursor beforeShellExecution livre"       0 '"permission":"allow"'   "$GB" "{$K,\"hook_event_name\":\"beforeShellExecution\",\"command\":\"npm run gate\"}"
# --- afterFileEdit reverte (repo temporário) ---
T=$(mktemp -d); ( cd "$T" && git init -q && git config user.email t@t && git config user.name t && printf 'A=1\n' > .env && git add .env && git commit -qm base && printf 'A=2\n' > .env
  printf '%s' "{$K,\"hook_event_name\":\"afterFileEdit\",\"file_path\":\"$T/.env\",\"edits\":[]}" | bash "$PP" >/dev/null 2>&1; git diff --quiet -- .env ); st=$?
if [ "$st" -eq 0 ]; then ok=$((ok+1)); else fail=$((fail+1)); echo "  ✗ afterFileEdit não reverteu .env"; fi
rm -rf "$T"
# --- cópias sincronizadas ---
for c in "$KIT"/samples/*/.claude/hooks "$KIT"/samples/*/.cursor/hooks; do
  # todo hook copiado que tem par em hooks/ (até a v0.5.6 só protect-paths e guard-bash eram comparados, e as cópias do
  # dotnet-format.sh e do tlc-version.sh no orders-sample tinham ficado para trás sem nenhum teste acusar)
  for f in "$c"/*.sh; do
    h=$(basename "$f"); [ -f "$KIT/hooks/$h" ] || continue
    if ! diff -q "$KIT/hooks/$h" "$f" >/dev/null; then fail=$((fail+1)); echo "  ✗ cópia divergente: ${f#$KIT/}"; else ok=$((ok+1)); fi
  done
done
# --- settings.json dos samples: os matchers de cada evento são os do template (#19: o matcher de edição mudou em três
# arquivos). Compara só os matchers: o comando pode mudar por perfil (o .NET formata com dotnet-format.sh). ---
for sj in "$KIT"/samples/*/.claude/settings.json; do
  if python3 -c 'import json,sys
m=lambda f: {ev: [h["matcher"] for h in hs] for ev, hs in json.load(open(f))["hooks"].items()}
sys.exit(0 if m(sys.argv[1]) == m(sys.argv[2]) else 1)' "$KIT/templates/.claude/settings.json" "$sj"; then ok=$((ok+1)); else fail=$((fail+1)); echo "  ✗ matchers divergentes do template: $sj"; fi
done
if grep -q '"MultiEdit"\|Edit|Write|MultiEdit' "$KIT"/templates/.claude/settings.json "$KIT"/samples/*/.claude/settings.json; then fail=$((fail+1)); echo "  ✗ matcher com MultiEdit"; else ok=$((ok+1)); fi
echo "test-hooks: $ok ok, $fail falha(s)"
[ "$fail" -eq 0 ]
