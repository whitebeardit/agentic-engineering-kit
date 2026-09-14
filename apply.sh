#!/usr/bin/env bash
# apply.sh — implanta o que é ENFORCEMENT do kit num repositório, sem sobrescrever o que já existe.
# Skills, agentes e MCP vêm do plugin (Claude: kit@whitebeard-kit · Cursor: plugin kit) — use --standalone para copiá-los.
#
# uso: apply.sh /caminho/do/repo [--claude] [--cursor] [--standalone] [--with-tlc] [--dotnet] [--node-ts] [--root] [--check] [--diff]
#   --claude      (default) AGENTS.md, CLAUDE.md, .claude/settings.json (permissões + hooks), .claude/hooks, .claude/rules, DoR, ADR template
#   --cursor      AGENTS.md, .cursor/hooks.json, .cursor/hooks, .cursor/rules (*.mdc), .cursorignore
#   --standalone  também copia skills/ e agents/ para .claude/ e/ou .cursor/ (para quem não usa marketplace)
#   --with-tlc    instala o tlc-spec-driven ORIGINAL (Claude: marketplace do kit · Cursor: CLI do Tech Leads Club) — nunca copiado
#   --dotnet      Directory.Build.props, .editorconfig, nuget.config, exemplo de teste de arquitetura (perfil .NET)
#   --node-ts     tsconfig, eslint (rampa), dependency-cruiser, jest, prettier — exemplos em docs/node-ts/ (perfil Node/TypeScript)
#   --root        usa AGENTS.root.md (workspace pai) em vez de AGENTS.md (serviço)
#   --check       não escreve nada: compara cada arquivo com o do kit e classifica novo · igual · divergente
#   --diff        como --check, e mostra a diferença dos divergentes
#
# Escrita segura (issue #10, v0.5.4): o script primeiro planeja todos os destinos e confere cada um antes da primeira
# escrita — recusa destino que é link simbólico (quebrado ou não) e ancestral que é link dentro do alvo, e nesse caso
# não escreve nada. Nunca sobrescreve: o que existe é mantido, com aviso quando difere do kit. `chmod +x` só nos hooks
# que criou nesta execução. Até a v0.5.3 ele seguia `.claude` simbólico para fora do alvo, mudava o modo de hooks
# alheios, falhava no meio sem dizer o que criou e dizia `= mantido` sobre um hook de 0 bytes.
set -euo pipefail
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:?informe o caminho do repositório}"; shift || true
CLAUDE=0; CURSOR=0; STANDALONE=0; WITH_TLC=0; DOTNET=0; NODETS=0; ROOT=0; CHECK=0; DIFF=0
for a in "$@"; do case "$a" in
  --claude) CLAUDE=1;; --cursor) CURSOR=1;; --standalone) STANDALONE=1;; --with-tlc) WITH_TLC=1;; --dotnet) DOTNET=1;; --node-ts) NODETS=1;; --root) ROOT=1;; --check) CHECK=1;; --diff) CHECK=1; DIFF=1;;
  *) echo "flag desconhecida: $a" >&2; exit 1;; esac; done
[ $CLAUDE -eq 0 ] && [ $CURSOR -eq 0 ] && CLAUDE=1
[ -d "$TARGET" ] || { echo "diretório não existe: $TARGET" >&2; exit 1; }
# As conferências usam o caminho resolvido; a saída mostra o caminho como foi passado (`./AGENTS.md` para `.`). A v0.5.4
# imprimia o absoluto resolvido — efeito colateral da conferência de links (#10) que tornava a saída diferente em cada máquina.
TARGET_ARG="${TARGET%/}"; [ -n "$TARGET_ARG" ] || TARGET_ARG="/"
TARGET="$(cd "$TARGET" && pwd -P)"
mostra() { printf '%s' "$TARGET_ARG${1#"$TARGET"}"; }
SRCS=(); DSTS=()
copy() { SRCS+=("$1"); DSTS+=("$2"); }   # planeja; a escrita vem depois do preflight
# destino seguro: nem ele nem um ancestral dentro do alvo é link simbólico
inseguro() {
  local d="$1" p
  [ -L "$d" ] && { echo "destino é link simbólico: $d"; return 0; }
  p="$(dirname "$d")"
  while [ "$p" != "$TARGET" ] && [ "${#p}" -gt "${#TARGET}" ]; do
    [ -L "$p" ] && { echo "ancestral é link simbólico: $p (destino $d)"; return 0; }
    p="$(dirname "$p")"
  done
  return 1
}
executar() {
  local i n=${#DSTS[@]} src dst criados=() ruins=() motivo
  if [ $CHECK -eq 1 ]; then
    local novo=0 igual=0 div=0
    for ((i=0; i<n; i++)); do src=${SRCS[$i]}; dst=${DSTS[$i]}
      if [ ! -e "$dst" ] && [ ! -L "$dst" ]; then echo "  novo        $(mostra "$dst")"; novo=$((novo+1))
      elif cmp -s "$src" "$dst"; then echo "  igual       $(mostra "$dst")"; igual=$((igual+1))
      else echo "  divergente  $(mostra "$dst")"; div=$((div+1)); [ $DIFF -eq 1 ] && diff -u "$dst" "$src" | sed 's/^/      /'; fi
    done
    echo "check: $novo novo(s), $igual igual(is), $div divergente(s) — nada foi escrito"
    exit 0
  fi
  for ((i=0; i<n; i++)); do motivo=$(inseguro "${DSTS[$i]}") && ruins+=("$motivo"); done
  if [ ${#ruins[@]} -gt 0 ]; then
    echo "recusado — nada foi escrito:" >&2; printf '  ! %s\n' "${ruins[@]}" >&2; exit 1
  fi
  trap 'echo "falhou no meio; criados até aqui: ${criados[*]:-nenhum}" >&2' ERR
  for ((i=0; i<n; i++)); do src=${SRCS[$i]}; dst=${DSTS[$i]}
    if [ -e "$dst" ]; then
      if cmp -s "$src" "$dst"; then echo "  = mantido   $(mostra "$dst")"; else echo "  = mantido   $(mostra "$dst")  (difere do kit: apply.sh --check)"; fi
    else mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"; criados+=("$dst"); echo "  + criado    $(mostra "$dst")"; fi
  done
  trap - ERR
  for dst in "${criados[@]}"; do case "$dst" in */.claude/hooks/*.sh|*/.cursor/hooks/*.sh) chmod +x "$dst";; esac; done
}

echo "kit → $TARGET_ARG"
# comum: contexto canônico + docs
if [ $ROOT -eq 1 ]; then copy "$KIT/templates/AGENTS.root.md" "$TARGET/AGENTS.md"; else copy "$KIT/templates/AGENTS.md" "$TARGET/AGENTS.md"; fi
copy "$KIT/docs/definition-of-ready.md" "$TARGET/docs/definition-of-ready.md"
copy "$KIT/docs/adr/0000-template.md" "$TARGET/docs/adr/0000-template.md"
copy "$KIT/templates/debug-prod.md" "$TARGET/docs/debug-prod.md"

if [ $CLAUDE -eq 1 ]; then
  copy "$KIT/templates/CLAUDE.md" "$TARGET/CLAUDE.md"
  # perfil .NET sem Node: o settings.json sem as permissões npm/npx que o projeto não usa (issue #27)
  SETTINGS="$KIT/templates/.claude/settings.json"; [ $DOTNET -eq 1 ] && [ $NODETS -eq 0 ] && SETTINGS="$KIT/templates/.claude/settings.dotnet.json"
  copy "$SETTINGS" "$TARGET/.claude/settings.json"
  for f in protect-paths.sh guard-bash.sh format.sh dotnet-format.sh; do copy "$KIT/hooks/$f" "$TARGET/.claude/hooks/$f"; done
  for f in "$KIT"/rules/*.md; do copy "$f" "$TARGET/.claude/rules/$(basename "$f")"; done
  if [ $STANDALONE -eq 1 ]; then
    for d in "$KIT"/skills/*/; do n=$(basename "$d"); copy "$d/SKILL.md" "$TARGET/.claude/skills/$n/SKILL.md"; done
    for f in "$KIT"/agents/*.md; do copy "$f" "$TARGET/.claude/agents/$(basename "$f")"; done
    copy "$KIT/hooks/tlc-version.sh" "$TARGET/.claude/hooks/tlc-version.sh"
    echo "  ! standalone: adicione ao .claude/settings.json o hook SessionStart → .claude/hooks/tlc-version.sh (ver hooks/hooks.json do kit)"
  fi
fi

if [ $CURSOR -eq 1 ]; then
  copy "$KIT/templates/.cursor/hooks.json" "$TARGET/.cursor/hooks.json"
  for f in protect-paths.sh guard-bash.sh format.sh dotnet-format.sh tlc-version.sh; do copy "$KIT/hooks/$f" "$TARGET/.cursor/hooks/$f"; done
  for f in "$KIT"/cursor/rules/*.mdc; do copy "$f" "$TARGET/.cursor/rules/$(basename "$f")"; done
  copy "$KIT/templates/.cursorignore" "$TARGET/.cursorignore"
  if [ $STANDALONE -eq 1 ]; then
    for d in "$KIT"/skills/*/; do n=$(basename "$d"); copy "$d/SKILL.md" "$TARGET/.cursor/skills/$n/SKILL.md"; done
    for f in "$KIT"/agents/*.md; do copy "$f" "$TARGET/.cursor/agents/$(basename "$f")"; done
  fi
fi

if [ $DOTNET -eq 1 ]; then
  copy "$KIT/dotnet/Directory.Build.props" "$TARGET/Directory.Build.props"
  copy "$KIT/dotnet/.editorconfig" "$TARGET/.editorconfig"
  copy "$KIT/dotnet/nuget.config" "$TARGET/nuget.config"
  copy "$KIT/dotnet/ArchitectureTests.example.cs" "$TARGET/docs/ArchitectureTests.example.cs"
fi

if [ $NODETS -eq 1 ]; then
  for f in "$KIT"/node-ts/*; do copy "$f" "$TARGET/docs/node-ts/$(basename "$f")"; done
  echo "  ! node-ts: exemplos em docs/node-ts/ — adapte e mova para a raiz (tsconfig, eslint com rampa, dependency-cruiser, jest, prettier)"
fi

executar

if [ $WITH_TLC -eq 1 ]; then
  echo
  if [ $CLAUDE -eq 1 ]; then
    if command -v claude >/dev/null 2>&1; then
      (cd "$TARGET" && claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git 2>/dev/null || true; claude plugin install kit@whitebeard-kit) || echo "  ! instale manualmente: claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git && claude plugin install kit@whitebeard-kit"
    else echo "  ! claude não encontrado. Depois: claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git && claude plugin install kit@whitebeard-kit"; fi
    echo "  atualizar: claude plugin update tlc@whitebeard-kit   (ative auto-update em /plugin › Marketplaces)"
  fi
  if [ $CURSOR -eq 1 ]; then
    # CLI do Tech Leads Club com versão fixa (issue #12): sem versão, o npx instalava a que estivesse no registro no dia.
    # Integridade: o npm confere o hash do pacote contra o registro; atualizar a versão aqui é um commit deliberado.
    if command -v npx >/dev/null 2>&1; then npx -y @tech-leads-club/agent-skills@1.4.10 install -s tlc-spec-driven -a cursor -g || echo "  ! falhou; rode: npx -y @tech-leads-club/agent-skills@1.4.10 install -s tlc-spec-driven -a cursor -g"
    else echo "  ! npx não encontrado. Depois: npx -y @tech-leads-club/agent-skills@1.4.10 install -s tlc-spec-driven -a cursor -g"; fi
    echo "  atualizar: npx -y @tech-leads-club/agent-skills@1.4.10 update -s tlc-spec-driven"
  fi
  echo "  tlc-spec-driven © Tech Leads Club (CC-BY-4.0) — sempre o original do GitHub deles; ver NOTICE.md"
fi
echo
echo "próximos passos:"
echo "  (1) preencha AGENTS.md (comandos com custo, gotchas, Never, matriz de testes)"
echo "  (2) abra o agente e rode /context"
echo "  (3) tente editar .env — deve ser negado antes da escrita (Claude Code e Cursor)"
