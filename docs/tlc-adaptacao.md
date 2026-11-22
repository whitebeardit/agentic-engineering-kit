# Como o kit usa o tlc-spec-driven

O **tlc-spec-driven** (Tech Leads Club / Felipe Rodrigues, CC-BY-4.0 — ver `NOTICE.md`) é o motor da fase 3: Specify →
Design → Tasks → Execute, com aprovação gravada da spec e das tarefas, um check com prova por critério, Verifier independente (lê o teste de cada
check e julga se ele seguraria o critério) e gate final em script, `.specs/STATE.md`
(decisões AD-NNN + handoff) e lições (`.specs/LESSONS.md`, `scripts/lessons.py`). O kit **não duplica nada disso**;
ele fornece o que o tlc espera encontrar no repo e liga o que o tlc produz aos loops da empresa.

## Origem: sempre o original, sempre a versão mais nova

| Plataforma | Instalação | Atualização |
|---|---|---|
| Claude Code | `claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git` → `claude plugin install kit@whitebeard-kit` (instala `tlc@whitebeard-kit` junto; entrada `git-subdir` rastreando `main` do repo Tech Leads Club) | `claude plugin update tlc@whitebeard-kit` (ative auto-update em `/plugin › Marketplaces`) |
| Cursor e outros | `npx -y @tech-leads-club/agent-skills@1.4.10 install -s tlc-spec-driven -a cursor -g` | `npx -y @tech-leads-club/agent-skills@1.4.10 update -s tlc-spec-driven` |

Nunca copie a skill para o repo. O hook `SessionStart` do kit avisa quando a cópia local está desatualizada, ausente ou
duplicada (global + plugin).

## O que o kit fornece ao tlc

- **`AGENTS.md`** (canônico, lido pelo tlc ao montar a Test Coverage Matrix e os Gate Check Commands): comandos com custo,
  definição de pronto, gotchas, expectativa de cobertura por camada, regras de dimensionamento.
- **`card-intake`**: porteiro (DoR) + briefing para o Specify. O tlc escreve a spec; o intake não.
- **Regras de dimensionamento**: multi-repo ou legado → Large mínimo; tier alto → Complex; contrato público → Design.
- **Agentes**: `impact-analyzer` é o passo 1 do Design; `legacy-navigator` antes de tocar o monolito; `test-designer`
  só em tier alto/legado (default do tlc: testes co-localizados na task; o Verifier aponta o teste mais frouxo que o critério);
  `dotnet-reviewer`/`contract-reviewer` no PR. O **Verifier é o do tlc** — o kit não tem outro.
- **Enforcement** (hooks, analyzers, rules, permissões): o que o tlc não cobre.

## O que o tlc produz e para onde vai

| Saída do tlc | Uso no kit |
|---|---|
| `.specs/features/<f>/proofs.md` (escrito por `check_proofs.py`) e `verification.md` (escrito pelo Verifier) | evidência do PR (link no corpo; sem `docs/evidencia/`). Até a 3.3.0 era um arquivo só, `validation.md` |
| `STATE.md › Decisions` (AD-NNN) | decisão leve de projeto. Vira **ADR** em `docs/adr/` (com `enforced-by`) quando ganha enforcement (teste de arquitetura, hook) ou cruza serviços; o ADR cita o AD |
| `STATE.md › Handoff` | reset de contexto entre sessões — use `pause work` / `resume work` |
| `.specs/LESSONS.md` (confirmed) | **ritual quinzenal**: cada lição confirmada vira hook, analyzer, rule ou linha no `AGENTS.md` quando for mecanizável; lição que vale para mais de um repo sobe para o kit (issue) |

## Multi-repo

A spec de um card que cruza serviços vive no repo **dono do contrato** (o primeiro da ordem contrato → produtor →
consumidor → legado). `tasks.md` mantém **1 task = 1 repo = 1 PR**; os outros repos recebem o link da spec e a task deles.
O tlc não carrega duas specs ao mesmo tempo — respeite isso: uma feature, uma pasta, um repo dono.

## O que o kit pede a mais ao Verifier: mutação (desde 2026-11-22, tlc 4.1.0)

Até a 3.3.0 o Verifier do tlc estragava o código de propósito e via se algum teste reclamava. A 4.1.0 trocou isso por
leitura: ele abre o teste de cada check e julga se o teste falharia caso a afirmação fosse falsa. O kit mantém a
mutação como pedido explícito, escrito no papel que o orquestrador entrega ao Verifier, depois do que o método já manda:

1. Trabalhe numa cópia fora da árvore (`git worktree add` num diretório temporário, ou cópia da pasta). Nada do que
   for estragado é commitado, e a árvore do repositório termina limpa.
2. Para pelo menos três regras da spec, estrague uma decisão do código por vez: tire uma condição, inverta uma
   comparação, troque um valor devolvido. Uma mutação por rodada.
3. Rode os comandos `Run` do `tasks.md` na cópia. Mutação morta é a que deixa pelo menos um teste vermelho.
4. Escreva em `verification.md` a seção `## Mutations`, com uma linha por mutação: o que foi estragado, arquivo e
   linha, o comando rodado e o teste que morreu. Mutação que sobrevive vira linha em `## Findings`, como qualquer outro
   achado.

O gate `validate_verification.py` não lê essa seção; quem confere é o humano que lê o relatório.

## Como se chama o método (conferido em 2026-11-22, tlc 4.1.0; `tools/test-validadores.sh`)

O tlc é uma skill: não tem comando próprio. Chama-se escrevendo na sessão o que se quer, e ele reconhece a fase.

| Para | Escreva na sessão |
|---|---|
| abrir a spec de uma feature | `Specify feature <nome>` |
| desenhar (Large e Complex) | `Design feature` |
| quebrar em tarefas | `Break into tasks` |
| executar uma tarefa | `Implement task T1` |
| verificar | `Validate` ou `verify work` |
| parar e retomar | `Pause work` · `Resume work` |

Os scripts se chamam à mão quando se quer conferir fora da sessão. `<feature>` é o nome da pasta em `.specs/features/`:

```bash
TLC=$(ls -d ~/.claude/plugins/cache/*/tlc/*/scripts | head -1)
python3 "$TLC/validate_spec.py" .specs/features/<feature>
python3 "$TLC/validate_tasks.py" .specs/features/<feature>            # antes de pedir aprovação
python3 "$TLC/validate_tasks.py" .specs/features/<feature> --execute  # antes da primeira tarefa
python3 "$TLC/check_proofs.py" <feature>                              # escreve proofs.md
python3 "$TLC/validate_verification.py" <feature>                     # gate final
```

Há dois pontos em que o método para e espera um humano: a aprovação da spec e a das tarefas. Cada uma vira uma linha
no arquivo, `**Approved**: <data> - user: "<as palavras de quem aprovou>"`, e `validate_tasks.py --execute` recusa
começar sem as duas. O Verifier não se chama: o orquestrador o despacha no fim, como sub-agente de contexto limpo.

## O que os validadores do tlc conferem hoje (conferido em 2026-11-22, tlc 4.1.0; `tools/test-validadores.sh`)

| Validador | Confere | **Não** confere (nesta data) |
|---|---|---|
| `validate_spec.py` | estrutura da spec (seções, tabela de rastreabilidade, IDs) | o **conteúdo** dos critérios: uma spec com o critério 1 trocado por "O sistema deve fazer a coisa certa quando der." passa com 0 erros — o cabeçalho `**Acceptance Criteria** (each line is one EARS pattern):` do próprio template não casa a regex do script (upstream `tech-leads-club/agent-skills#162`, aberta desde 2026-08-08; segue assim na 4.1.0) |
| `validate_tasks.py` | seções obrigatórias (agora com `## Checks`), campos `Tests`/`Gate`, dependências contra tarefas existentes (`Depends on: T99` reprova), um `Proof:` por check, a linha `**Build**:`, e com `--execute` as duas linhas `**Approved**` | se a prova nomeada segura o critério: isso é o que o Verifier lê |
| `check_proofs.py` | roda cada comando `Run` e cada prova uma vez, procura a linha de cada teste na saída, roda o `**Build**:` e escreve `proofs.md` com o `HEAD` e o estado da árvore | o que o teste afirma; teste que passa sem segurar o critério sai `pass` |
| `validate_verification.py` | `proofs.md` no `HEAD` atual e sem falha, uma linha por check em `verification.md` com o teste nomeado, todo achado com commit em `Closed`, as duas aprovações | o **veredito**: um relatório que diz `FAIL` com os achados fechados passa com 0 erros |

Saíram na 4.x: as mutações do Verifier (o kit as mantém como pedido, seção acima), o `validation.md` e o
`validate_state.py`.

### O que rodar a 4.1.0 nos laboratórios mostrou (2026-11-22)

- **O Jest 30 resume a saída dentro de agente.** Quando detecta uma sessão de agente (variáveis como `AI_AGENT` e
  `CLAUDECODE`), ele troca o relator e a linha por teste some. A prova `run <nome> | <linha>` leria `no test ran`.
  O `Run` do laboratório Node pede `--reporters=default`.
- **Projeto em subpasta do repositório.** `check_proofs.py` trata como suja a árvore que tiver arquivo sem commit fora
  de `.specs/`, contando a partir da raiz do git. Com dois laboratórios no mesmo repositório, o `proofs.md` de um
  suja a conferência do outro: roda-se um por vez, com o anterior já commitado.
- **O gate final só dá 0 antes do commit que grava o `proofs.md`.** O arquivo guarda o `HEAD` em que rodou; gravá-lo
  muda o `HEAD`. Num repositório já commitado, `validate_verification.py` reprova por isso, e o teste do kit espera
  essa reprovação.
- **`dotnet test` não imprime uma linha por teste por padrão.** O `Run` do laboratório .NET pede
  `--logger "console;verbosity=normal"`.

`tools/test-validadores.sh` roda os validadores contra a spec e as tasks do laboratório e contra mutantes, e reprova
qualquer desvio **do que está documentado aqui** — inclusive o upstream corrigir o #162: aí a linha acima muda, com
data. O kit não fixa a versão do tlc (rastreia `main`); registra o que ela faz.
