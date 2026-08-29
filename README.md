# Whitebeard · Agentic Engineering Kit

Como a Whitebeard desenvolve software com agentes de IA — e como implanta e ensina isso em clientes (.NET, legado,
microserviços, cards no Jira ou ClickUp). É o lado executável do roteiro em 7 fases
(vault: `30-Areas/Whitebeard/agentes-ia/processo-engenharia-com-agentes.md`;
página: https://claude.ai/code/artifact/e53c902f-b3b0-4334-b3f8-cc52c73f26bb).

O motor da fase 3 (card → spec → tasks → execute → verificação) é o **tlc-spec-driven** do Tech Leads Club
(CC-BY-4.0). O kit **não o copia**: instala sempre o original do GitHub deles, na versão mais nova, e fornece o que ele
espera encontrar no repo (`AGENTS.md`, regras, matriz de testes) mais o que ele não cobre (intake, agentes, enforcement).
Atribuição em `NOTICE.md`.

## Três usos, um kit

| Uso | Como |
|---|---|
| **Operação própria** | Whitebeard instala o plugin e aplica o kit nos seus repos; toda lição vira template aqui |
| **Serviço (implantação)** | `apply.sh` em cada repo do cliente + fases 0→3 do roteiro em ~8 semanas; 4→6 como advisory recorrente |
| **Formação** | cada fase tem checklist e critério de saída; o time do cliente executa, a Whitebeard revisa |

## Instalação

**Claude Code** (plugin + marketplace neste repo; instala o tlc como dependência):
```bash
claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git
claude plugin install kit@whitebeard-kit          # instala kit e tlc@whitebeard-kit
claude plugin update tlc@whitebeard-kit           # ou ative auto-update em /plugin › Marketplaces
```
**Cursor** (plugin neste repo; tlc pela CLI oficial do Tech Leads Club):
```bash
npx -y @tech-leads-club/agent-skills install -s tlc-spec-driven -a cursor -g
```
**No repositório** (enforcement: contexto canônico, permissões, hooks, rules, perfil .NET):
```bash
git clone git@github.com:whitebeardit/agentic-engineering-kit.git ~/DEV/WHITEBEARD/agentic-engineering-kit
~/DEV/WHITEBEARD/agentic-engineering-kit/apply.sh /caminho/do/repo --claude --cursor --with-tlc --dotnet
```
`--standalone` copia skills e agentes para `.claude/`/`.cursor/` de quem não usa marketplace (nomes sem o prefixo `kit:`).

## Princípios (o kit existe para impor estes, não para descrevê-los)

1. IA é amplificador: fundação (VCS, testes, lotes pequenos) antes do agente.
2. Contexto mínimo e concreto: `AGENTS.md` com comandos, custos e gotchas — nunca prosa de arquitetura.
3. Enforcement mecânico > texto: o que importa é hook, analyzer ou CI.
4. Spec antes do código; gate humano entre "o quê" e "como" (tlc-spec-driven).
5. Autor ≠ verificador; evidência ou zero (Verifier do tlc).
6. Cada erro do agente vira artefato (lição do tlc → hook, teste, rule).
7. Segurança na borda: least agency, segredos fora do contexto, conteúdo externo = input não confiável.

## Mapa

```
.claude-plugin/                   plugin.json (kit, depende de tlc) · marketplace.json (kit + tlc via git-subdir do repo TLC)
.cursor-plugin/                   plugin.json · marketplace.json (Cursor)
skills/                           card-intake · run-and-test · regras-de-negocio        (Claude e Cursor)
agents/                           impact-analyzer · legacy-navigator · test-designer · dotnet-reviewer · contract-reviewer
hooks/                            hooks.json (SessionStart: aviso de versão do tlc) · protect-paths · guard-bash · dotnet-format · tlc-version
rules/                            contracts.md · legacy.md (Claude, paths:)     cursor/rules/*.mdc (gerados por tools/build-cursor.py)
.mcp.json                         atlassian + clickup (OAuth por usuário)
templates/                        AGENTS.md · AGENTS.root.md · CLAUDE.md (@AGENTS.md) · .claude/settings.json · .cursor/hooks.json · .cursorignore
dotnet/                           Directory.Build.props (rampa para legado) · .editorconfig · nuget.config · ArchitectureTests.example.cs
docs/                             definition-of-ready · tlc-adaptacao · cursor-paridade · fases-checklist · adr/0000-template
samples/orders-sample/            exemplo .NET compilado e testado, com .specs/ gerado pelo tlc (ver abaixo)
tools/                            gen-ebook.py (e-book a partir dos arquivos reais) · build-cursor.py
apply.sh                          implanta o enforcement num repo (não sobrescreve)
NOTICE.md                         atribuição Tech Leads Club (CC-BY-4.0)
```

## O que vai onde

| Plugin (usuário) | `apply.sh` (repo, revisado em PR) |
|---|---|
| skills, agentes, `.mcp.json`, hook de versão do tlc, o próprio tlc | `AGENTS.md`/`CLAUDE.md`, `.claude/settings.json` (permissões + hooks bloqueantes), `.claude/rules`, `.cursor/hooks.json`, `.cursorignore`, `Directory.Build.props`, `nuget.config`, `.editorconfig`, DoR, template de ADR |

Detalhes: `docs/tlc-adaptacao.md` (dimensionamento, AD-NNN ↔ ADR, multi-repo, ritual de lições) e `docs/cursor-paridade.md`.

## Exemplo real: `samples/orders-sample`

Serviço de Pedidos em .NET 10 (Domain / Application / Infrastructure + `Erp.Legacy`) com o kit aplicado e a feature 001
(cancelamento parcial) conduzida pelo tlc-spec-driven: `.specs/STATE.md`, `spec.md`, `tasks.md` com Test Coverage
Matrix lida do `AGENTS.md`, `validation.md` do Verifier e `LESSONS.md`. Feature 001 conduzida pelo tlc-spec-driven de ponta a ponta (spec → tasks → 6 commits → Verifier). Build limpo, 14/14 testes. O e-book
"Engenharia com Agentes em .NET" é gerado destes arquivos por `tools/gen-ebook.py`
(artifact: https://claude.ai/code/artifact/2746fde4-f60e-4189-bc26-8203a1758373).

```bash
cd samples/orders-sample && dotnet test Orders.slnx     # ≈ 9 s
```

## Manutenção do kit

- Muda-se aqui primeiro; os repos recebem por `apply.sh`/PR e os usuários por `claude plugin update`. Nenhuma regra vive só num repo.
- `rules/*.md` é a fonte; `cursor/rules/*.mdc` é gerado (`tools/build-cursor.py --check` no CI).
- Todo template tem dono e data de revisão (trimestral, e a cada modelo novo: remova um componente e veja o que ainda é load-bearing).
- Lição de cliente → issue neste repo → template. Sem nome de cliente nos templates.
- Release: bump `version` em `.claude-plugin/plugin.json` e `.cursor-plugin/plugin.json`; `claude plugin tag --push`.
