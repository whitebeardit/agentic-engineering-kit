# Como o kit usa o tlc-spec-driven

O **tlc-spec-driven** (Tech Leads Club / Felipe Rodrigues, CC-BY-4.0 — ver `NOTICE.md`) é o motor da fase 3: Specify →
Design → Tasks → Execute, com Verifier independente (checagem ancorada na spec + sensor de discriminação), `.specs/STATE.md`
(decisões AD-NNN + handoff) e lições (`.specs/LESSONS.md`, `scripts/lessons.py`). O kit **não duplica nada disso**;
ele fornece o que o tlc espera encontrar no repo e liga o que o tlc produz aos loops da empresa.

## Origem: sempre o original, sempre a versão mais nova

| Plataforma | Instalação | Atualização |
|---|---|---|
| Claude Code | `claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git` → `claude plugin install kit@whitebeard-kit` (instala `tlc@whitebeard-kit` junto; entrada `git-subdir` rastreando `main` do repo Tech Leads Club) | `claude plugin update tlc@whitebeard-kit` (ative auto-update em `/plugin › Marketplaces`) |
| Cursor e outros | `npx -y @tech-leads-club/agent-skills install -s tlc-spec-driven -a cursor -g` | `npx -y @tech-leads-club/agent-skills update -s tlc-spec-driven` |

Nunca copie a skill para o repo. O hook `SessionStart` do kit avisa quando a cópia local está desatualizada, ausente ou
duplicada (global + plugin).

## O que o kit fornece ao tlc

- **`AGENTS.md`** (canônico, lido pelo tlc ao montar a Test Coverage Matrix e os Gate Check Commands): comandos com custo,
  definição de pronto, gotchas, expectativa de cobertura por camada, regras de dimensionamento.
- **`card-intake`**: porteiro (DoR) + briefing para o Specify. O tlc escreve a spec; o intake não.
- **Regras de dimensionamento**: multi-repo ou legado → Large mínimo; tier alto → Complex; contrato público → Design.
- **Agentes**: `impact-analyzer` é o passo 1 do Design; `legacy-navigator` antes de tocar o monolito; `test-designer`
  só em tier alto/legado (default do tlc: testes co-localizados na task, e o sensor pune teste fraco);
  `dotnet-reviewer`/`contract-reviewer` no PR. O **Verifier é o do tlc** — o kit não tem outro.
- **Enforcement** (hooks, analyzers, rules, permissões): o que o tlc não cobre.

## O que o tlc produz e para onde vai

| Saída do tlc | Uso no kit |
|---|---|
| `.specs/features/<f>/validation.md` | evidência do PR (link no corpo; sem `docs/evidencia/`) |
| `STATE.md › Decisions` (AD-NNN) | decisão leve de projeto. Vira **ADR** em `docs/adr/` (com `enforced-by`) quando ganha enforcement (teste de arquitetura, hook) ou cruza serviços; o ADR cita o AD |
| `STATE.md › Handoff` | reset de contexto entre sessões — use `pause work` / `resume work` |
| `.specs/LESSONS.md` (confirmed) | **ritual quinzenal**: cada lição confirmada vira hook, analyzer, rule ou linha no `AGENTS.md` quando for mecanizável; lição que vale para mais de um repo sobe para o kit (issue) |

## Multi-repo

A spec de um card que cruza serviços vive no repo **dono do contrato** (o primeiro da ordem contrato → produtor →
consumidor → legado). `tasks.md` mantém **1 task = 1 repo = 1 PR**; os outros repos recebem o link da spec e a task deles.
O tlc não carrega duas specs ao mesmo tempo — respeite isso: uma feature, uma pasta, um repo dono.
