#!/usr/bin/env bash
# SessionStart (Claude e Cursor): AVISA — nunca instala — quando o tlc-spec-driven está ausente, desatualizado, duplicado,
# com versão que não dá para comparar, ou quando não foi possível verificar. Fica quieto quando a cópia local está em dia
# ou é mais nova que a do upstream. O tlc é sempre o original de github.com/tech-leads-club/agent-skills (CC-BY-4.0).
#
# Até a v0.5.3 (issues #11 e #21): comparava texto com `!=` (uma local MAIS NOVA virava "atualize"), ficava quieto sem
# rede (quieto parecia atualizado), não dizia de quando era o cache, e fixava o catálogo `@whitebeard-kit` nas mensagens —
# quem instalou pelo catálogo do livro (`cercando-a-ia`) recebia um comando de outro catálogo. Testes em
# tools/test-tlc-version.sh (HOME, cache e curl simulados).
input=$(cat 2>/dev/null)
is_cursor=0; printf '%s' "$input" | grep -q -E '"cursor_version"|"workspace_roots"|"conversation_id"' && is_cursor=1
UP="https://raw.githubusercontent.com/tech-leads-club/agent-skills/main/packages/skills-catalog/skills/%28development%29/tlc-spec-driven/SKILL.md"
CACHE_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/whitebeard-kit}"; mkdir -p "$CACHE_DIR" 2>/dev/null
CACHE="$CACHE_DIR/tlc-upstream-version"; TTL_MIN=1440
ver_of() { grep -m1 -E '^\s*version:\s*' "$1" 2>/dev/null | sed -E 's/^\s*version:\s*//; s/["'"'"']//g; s/\s.*$//'; }
semver() { printf '%s' "$1" | grep -Eq '^[0-9]+(\.[0-9]+){0,2}$'; }
# maior(a, b) → imprime a maior; ordenação numérica por campo (3.10.0 > 3.9.0), não por texto
maior() { printf '%s\n%s\n' "$1" "$2" | sort -t. -k1,1n -k2,2n -k3,3n | tail -1; }

# 1) cópias locais da PLATAFORMA atual (Claude: projeto, cache do plugin, global · Cursor: projeto, global)
found=(); vers=()
if [ $is_cursor -eq 1 ]; then cands=("$PWD/.cursor/skills/tlc-spec-driven/SKILL.md" "$HOME/.cursor/skills/tlc-spec-driven/SKILL.md")
else cands=("$PWD/.claude/skills/tlc-spec-driven/SKILL.md" "$HOME"/.claude/plugins/cache/*/tlc/*/SKILL.md "$HOME"/.claude/plugins/cache/*/tlc/SKILL.md "$HOME/.claude/skills/tlc-spec-driven/SKILL.md"); fi
for f in "${cands[@]}"; do [ -f "$f" ] && { found+=("$f"); vers+=("$(ver_of "$f")"); }; done

# 2) catálogo de origem, para o comando de conserto: o do próprio kit (CLAUDE_PLUGIN_ROOT), senão o do cache do tlc
catalogo=""
case "${CLAUDE_PLUGIN_ROOT:-}" in */plugins/cache/*/kit/*) catalogo=$(printf '%s' "$CLAUDE_PLUGIN_ROOT" | sed -E 's#.*/plugins/cache/([^/]+)/kit/.*#\1#');; esac
if [ -z "$catalogo" ]; then for f in "${found[@]}"; do case "$f" in */plugins/cache/*/tlc/*) catalogo=$(printf '%s' "$f" | sed -E 's#.*/plugins/cache/([^/]+)/tlc/.*#\1#'); break;; esac; done; fi
cat_txt=${catalogo:-"<o catálogo por onde você instalou o kit>"}

# 3) upstream (1x por 24h, 3s de timeout). Sem rede, sem curl ou com timeout: "não verificado", com a data do cache.
upstream=""; verificado=""; nao_verificado=""
cache_data() { date -r "$CACHE" '+%Y-%m-%d %H:%M' 2>/dev/null; }
if [ -f "$CACHE" ] && [ -z "$(find "$CACHE" -mmin +$TTL_MIN 2>/dev/null)" ]; then upstream=$(cat "$CACHE"); verificado=$(cache_data)
elif command -v curl >/dev/null 2>&1; then
  body=$(curl -fsSL -m 3 "$UP" 2>/dev/null); rc=$?
  if [ $rc -eq 0 ]; then upstream=$(printf '%s' "$body" | grep -m1 -E '^\s*version:' | sed -E 's/^\s*version:\s*//; s/["'"'"']//g; s/\s.*$//'); printf '%s' "$upstream" > "$CACHE"; verificado=$(cache_data)
  elif [ $rc -eq 22 ]; then upstream="404"
  else nao_verificado="sem resposta do upstream (curl $rc)"; fi
else nao_verificado="curl não encontrado"; fi
if [ -n "$nao_verificado" ] && [ -f "$CACHE" ]; then upstream=$(cat "$CACHE"); verificado="$(cache_data), cache vencido"; fi

msg=""
if [ ${#found[@]} -eq 0 ]; then
  msg="tlc-spec-driven ausente. Instale: claude plugin install kit@$cat_txt (Claude) ou npx -y @tech-leads-club/agent-skills@1.4.10 install -s tlc-spec-driven -a cursor -g (Cursor)."
else
  local_v="${vers[0]}"
  if [ ${#found[@]} -gt 1 ]; then msg="tlc-spec-driven duplicado nesta plataforma (${#found[@]} cópias: ${found[*]}). Mantenha uma só (Claude: a do plugin tlc@$cat_txt; Cursor: a global da CLI do TLC). "; fi
  if [ "$upstream" = "404" ]; then msg="${msg}Upstream do tlc não encontrado no caminho conhecido — o repositório Tech Leads Club mudou o path; atualize .claude-plugin/marketplace.json do kit."
  elif [ -n "$nao_verificado" ] && [ -z "$upstream" ]; then msg="${msg}tlc-spec-driven local $local_v não verificado: $nao_verificado e nenhum cache anterior."
  elif [ -n "$upstream" ] && [ -n "$local_v" ]; then
    if ! semver "$local_v" || ! semver "$upstream"; then msg="${msg}tlc-spec-driven: versão não comparável (local '$local_v', upstream '$upstream')."
    elif [ "$local_v" != "$upstream" ] && [ "$(maior "$local_v" "$upstream")" = "$upstream" ]; then
      msg="${msg}tlc-spec-driven desatualizado: local $local_v < upstream $upstream (verificado em $verificado). Atualize: claude plugin update tlc@$cat_txt (Cursor: npx -y @tech-leads-club/agent-skills@1.4.10 update -s tlc-spec-driven)."
    elif [ -n "$nao_verificado" ]; then msg="${msg}tlc-spec-driven local $local_v não verificado agora ($nao_verificado); última verificação em $verificado dizia upstream $upstream."
    fi
  fi
fi
[ -z "$msg" ] && exit 0
if [ $is_cursor -eq 1 ]; then printf '{"additional_context": %s}\n' "$(printf '%s' "$msg" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
else printf '[kit] %s\n' "$msg"; fi
exit 0
