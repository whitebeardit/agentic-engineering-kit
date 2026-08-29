#!/usr/bin/env bash
# SessionStart (Claude e Cursor): AVISA — nunca instala — se o tlc-spec-driven está ausente, desatualizado ou duplicado.
# O tlc é sempre o original de github.com/tech-leads-club/agent-skills (CC-BY-4.0); atualização: `claude plugin update tlc@whitebeard-kit`.
input=$(cat 2>/dev/null)
is_cursor=0; printf '%s' "$input" | grep -q -E '"cursor_version"|"workspace_roots"|"conversation_id"' && is_cursor=1
UP="https://raw.githubusercontent.com/tech-leads-club/agent-skills/main/packages/skills-catalog/skills/%28development%29/tlc-spec-driven/SKILL.md"
CACHE_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/whitebeard-kit}"; mkdir -p "$CACHE_DIR" 2>/dev/null
CACHE="$CACHE_DIR/tlc-upstream-version"
ver_of() { grep -m1 -E '^\s*version:\s*' "$1" 2>/dev/null | sed -E 's/^\s*version:\s*//; s/\s.*$//'; }
# 1) cópias locais da PLATAFORMA atual (Claude: projeto, cache do plugin, global · Cursor: projeto, global)
found=(); vers=()
if [ $is_cursor -eq 1 ]; then cands=("$PWD/.cursor/skills/tlc-spec-driven/SKILL.md" "$HOME/.cursor/skills/tlc-spec-driven/SKILL.md")
else cands=("$PWD/.claude/skills/tlc-spec-driven/SKILL.md" "$HOME"/.claude/plugins/cache/*/tlc/*/SKILL.md "$HOME"/.claude/plugins/cache/*/tlc/SKILL.md "$HOME/.claude/skills/tlc-spec-driven/SKILL.md"); fi
for f in "${cands[@]}"; do [ -f "$f" ] && { found+=("$f"); vers+=("$(ver_of "$f")"); }; done
# 2) upstream (1x por 24h, 3s de timeout; sem rede → silêncio)
upstream=""
if [ -f "$CACHE" ] && [ -z "$(find "$CACHE" -mmin +1440 2>/dev/null)" ]; then upstream=$(cat "$CACHE")
else
  if command -v curl >/dev/null 2>&1; then
    body=$(curl -fsSL -m 3 "$UP" 2>/dev/null); rc=$?
    if [ $rc -eq 0 ]; then upstream=$(printf '%s' "$body" | grep -m1 -E '^\s*version:' | sed -E 's/^\s*version:\s*//; s/\s.*$//'); printf '%s' "$upstream" > "$CACHE"
    elif [ $rc -eq 22 ]; then upstream="404"; fi
  fi
fi
msg=""
if [ ${#found[@]} -eq 0 ]; then
  msg="tlc-spec-driven não encontrado. Instale: claude plugin install kit@whitebeard-kit (Claude) ou npx -y @tech-leads-club/agent-skills install -s tlc-spec-driven -a cursor -g (Cursor)."
else
  local_v="${vers[0]}"
  if [ ${#found[@]} -gt 1 ]; then msg="tlc-spec-driven duplicado nesta plataforma (${#found[@]} cópias: ${found[*]}). Mantenha uma só (Claude: a do plugin tlc@whitebeard-kit; Cursor: a global da CLI do TLC). "; fi
  if [ "$upstream" = "404" ]; then msg="${msg}Upstream do tlc não encontrado no caminho conhecido — o repositório Tech Leads Club mudou o path; atualize .claude-plugin/marketplace.json do kit."
  elif [ -n "$upstream" ] && [ -n "$local_v" ] && [ "$upstream" != "$local_v" ]; then msg="${msg}tlc-spec-driven local $local_v ≠ upstream $upstream. Atualize: claude plugin update tlc@whitebeard-kit (Cursor: npx -y @tech-leads-club/agent-skills update -s tlc-spec-driven)."; fi
fi
[ -z "$msg" ] && exit 0
if [ $is_cursor -eq 1 ]; then printf '{"additional_context": %s}\n' "$(printf '%s' "$msg" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')"
else printf '[kit] %s\n' "$msg"; fi
exit 0
