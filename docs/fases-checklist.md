# Checklist por fase — critérios de saída (resumo executável do roteiro)

Detalhe no vault `agentes-ia/processo-engenharia-com-agentes.md`. Nada avança sem o critério de saída da fase anterior.

## 0 · Fundação (sem. 1–2)
- [ ] Política de uso de IA (1 pág.) publicada e lida pelos champions
- [ ] Baseline registrado com data: DORA 5 + rework, p75 PR, pickup/review, duplicação
- [ ] 2 champions seniores; 1 fluxo piloto (legado + 1 micro); PO disponível
- [ ] Repos do piloto: testes rodam, CI existe, branch protection, lockfile, segredos fora

## 1 · Contexto mínimo (sem. 2–3)
- [ ] Workspace pai; `CLAUDE.md` raiz (tabela de serviços) e por repo (< 150 linhas)
- [ ] `apply.sh` aplicado; hook bloqueia `.env`/migrations; `dotnet format` automático
- [ ] Analyzers via `Directory.Build.props` (rampa no legado)
- [ ] Agente builda e testa sozinho; `/context` < 10 %

## 2 · Mapa da empresa (sem. 3–5)
- [ ] Grafo de dependências e inventário de endpoints/eventos **gerados** em CI
- [ ] Repo Coordination Graph no vault (owners nomeados); C4 Contexto+Container em DSL; 5 ADRs
- [ ] `impact-analyzer` acerta repos e ordem em 3 cards históricos

## 3 · Card → spec → PR (sem. 5–8)
- [ ] Definition of Ready em uso; specs em 3 arquivos com 2 gates humanos
- [ ] verifier ≠ autor; AI review antes do humano; PR draft ≤ 400 linhas; CODEOWNERS; tiers de risco
- [ ] 5 cards fim a fim; nota por card no vault; p75 e rework vs baseline

## 4 · Sensores e segurança (sem. 8–12)
- [ ] Characterization tests nos 5 fluxos críticos do legado
- [ ] `oasdiff` no PR; Pact nos 3 pares críticos; AsyncAPI/EventCatalog; ArchUnitNET; Stryker `--since`
- [ ] Sandbox + egresso + token por repo + OTel de tool-calls; verificação de pacote novo

## 5 · Harness e escala (mês 3–6)
- [ ] Plugin interno; managed settings; Writer/Reviewer em worktrees; evaluator com browser; GC semanal
- [ ] 2ª equipe operando; DORA não regrediu; nenhuma política depende de "lembrar"

## 6 · Contínua
- [ ] Loops com cadência (card · PR · semana · quinzena · mês · trimestre · modelo novo)
- [ ] Todo artefato com dono, data e check de frescor; CLAUDE.md diminui, não cresce
