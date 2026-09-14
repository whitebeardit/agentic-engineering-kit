#!/usr/bin/env bash
# Testes herméticos de hooks/tlc-version.sh (issues #11 e #21): HOME, cache e curl simulados; nada toca a rede.
# Uso: bash tools/test-tlc-version.sh   (exit 0 = tudo ok)
set -u
KIT=$(cd "$(dirname "$0")/.." && pwd); H="${TLC_VERSION_HOOK:-$KIT/hooks/tlc-version.sh}"
ok=0; fail=0
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin" "$T/nocurl"
for b in bash sh grep sed sort tail head find date cat mkdir printf python3 dirname tr touch env; do p=$(command -v "$b") && ln -sf "$p" "$T/nocurl/$b"; done
cp -r "$T/nocurl/." "$T/bin/" 2>/dev/null
cat > "$T/bin/curl" <<'C'
#!/bin/sh
[ -n "${STUB_BODY:-}" ] && printf '%s\n' "$STUB_BODY"
exit "${STUB_RC:-0}"
C
chmod +x "$T/bin/curl"
skill() { mkdir -p "$(dirname "$1")"; printf -- '---\nname: tlc-spec-driven\nmetadata:\n  version: %s\n---\n' "$2" > "$1"; }
# caso · esperado: "" (silêncio) ou regex · ambiente em pares VAR=valor
caso() {
  local nome=$1 rx=$2; shift 2
  local h="$T/h-$ok-$fail"; rm -rf "$h"; mkdir -p "$h/data" "$h/proj"
  local path_bin="$T/bin" input='{"session_id":"s","hook_event_name":"SessionStart"}' root=""
  local envs=()
  for kv in "$@"; do case "$kv" in
    NOCURL=1) path_bin="$T/nocurl";;
    CURSOR=1) input='{"conversation_id":"c","cursor_version":"1.0","workspace_roots":["/r"]}';;
    ROOT=*) root="${kv#ROOT=}";;
    *) envs+=("$kv");; esac; done
  out=$(cd "$h/proj" && env -i HOME="$h" PATH="$path_bin" CLAUDE_PLUGIN_DATA="$h/data" CLAUDE_PLUGIN_ROOT="$root" "${envs[@]}" bash -c "$(declare -f skill); $PRE; printf '%s' '$input' | bash '$H'" 2>&1)
  if { [ -z "$rx" ] && [ -z "$out" ]; } || { [ -n "$rx" ] && printf '%s' "$out" | grep -Eq "$rx"; }; then ok=$((ok+1)); else fail=$((fail+1)); echo "  ✗ $nome → saída: ${out:0:160}"; fi
}
C1='$HOME/.claude/plugins/cache/cercando-a-ia/tlc/abc/SKILL.md'
W1='$HOME/.claude/plugins/cache/whitebeard-kit/tlc/abc/SKILL.md'
PRE="skill $C1 3.3.0"; caso "atual → silêncio" "" STUB_BODY="version: 3.3.0"
PRE="skill $C1 3.4.0"; caso "local mais nova → silêncio (antes: 'atualize')" "" STUB_BODY="version: 3.3.0"
PRE="skill $C1 3.10.0"; caso "3.10.0 > 3.9.0 (ordem numérica, não texto) → silêncio" "" STUB_BODY="version: 3.9.0"
PRE="skill $C1 3.2.9"; caso "desatualizado, catálogo cercando-a-ia" 'desatualizado: local 3\.2\.9 < upstream 3\.3\.0.*tlc@cercando-a-ia' STUB_BODY="version: 3.3.0"
PRE="skill $W1 3.2.9"; caso "desatualizado, catálogo whitebeard-kit" 'tlc@whitebeard-kit' STUB_BODY="version: 3.3.0"
PRE="true"; caso "ausente, catálogo pelo CLAUDE_PLUGIN_ROOT" 'ausente.*kit@cercando-a-ia' STUB_BODY="version: 3.3.0" ROOT="/x/.claude/plugins/cache/cercando-a-ia/kit/0.2.0"
PRE="true"; caso "ausente sem catálogo conhecido → instrução neutra" 'kit@<o catálogo por onde você instalou o kit>' STUB_BODY="version: 3.3.0"
PRE="skill $C1 3.3.0; skill $W1 3.3.0"; caso "duplicado" 'duplicado nesta plataforma \(2 cópias' STUB_BODY="version: 3.3.0"
PRE="skill $C1 3.3.0"; caso "sem rede e sem cache → não verificado" 'não verificado: sem resposta do upstream \(curl 6\)' STUB_RC=6
PRE="skill $C1 3.3.0"; caso "timeout → não verificado" 'curl 28' STUB_RC=28
PRE="skill $C1 3.3.0"; caso "curl ausente → não verificado" 'curl não encontrado' NOCURL=1
PRE="skill $C1 3.3.0; printf 3.3.0 > \$CLAUDE_PLUGIN_DATA/tlc-upstream-version; touch -d '3 days ago' \$CLAUDE_PLUGIN_DATA/tlc-upstream-version"
caso "cache vencido + sem rede → não verificado com a data" 'última verificação em [0-9]{4}-[0-9]{2}-[0-9]{2}.*cache vencido' STUB_RC=6
PRE="skill $C1 3.3.0"; caso "upstream 404 → caminho mudou" 'mudou o path' STUB_RC=22
PRE="skill $C1 abc"; caso "versão não comparável" 'não comparável' STUB_BODY="version: 3.3.0"
PRE="mkdir -p .cursor/skills/tlc-spec-driven; skill .cursor/skills/tlc-spec-driven/SKILL.md 3.2.0"; caso "Cursor desatualizado → JSON additional_context" '^\{"additional_context": ".*desatualizado' STUB_BODY="version: 3.3.0" CURSOR=1
echo "test-tlc-version: $ok ok, $fail falha(s)"
[ "$fail" -eq 0 ]
