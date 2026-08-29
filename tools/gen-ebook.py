import html, os, re, sys
K = os.path.expanduser("~/DEV/WHITEBEARD/agentic-engineering-kit")
S = os.path.join(K, "samples/orders-sample")
OUT = os.path.expanduser("~/DEV/paperclip/ebook/engenharia-com-agentes-dotnet.html")

def f(path, start=None, end=None):
    p = path if path.startswith("/") else os.path.join(S, path)
    if not os.path.exists(p): p = os.path.join(K, path)
    lines = open(p, encoding="utf-8").read().splitlines()
    if start or end: lines = lines[(start or 1)-1:end]
    return html.escape("\n".join(lines))

def code(path, lang="", start=None, end=None, title=None):
    t = title or path
    return f'<figure class="code"><figcaption><span class="path">{html.escape(t)}</span></figcaption><pre><code class="lang-{lang}">{f(path,start,end)}</code></pre></figure>'


def snip(path, start_pat, end_pat=None, lang="", title=None, include_end=True):
    p = path if path.startswith("/") else os.path.join(S, path)
    if not os.path.exists(p): p = os.path.join(K, path)
    lines = open(p, encoding="utf-8").read().splitlines()
    i0 = next(i for i,l in enumerate(lines) if re.search(start_pat, l))
    if end_pat:
        i1 = next(i for i in range(i0+1, len(lines)) if re.search(end_pat, lines[i]))
        seg = lines[i0:(i1+1 if include_end else i1)]
        if not include_end:
            while seg and re.match(r"^\s*(\[Fact\])?\s*$", seg[-1]): seg.pop()
    else:
        seg = lines[i0:]
    body = html.escape("\n".join(seg).rstrip())
    t = title or path
    return f'<figure class="code"><figcaption><span class="path">{html.escape(t)}</span></figcaption><pre><code class="lang-{lang}">{body}</code></pre></figure>'

import subprocess
ASSETS = os.path.join(K, "tools/ebook-assets")
def asset(name):
    return open(os.path.join(ASSETS, name), encoding="utf-8").read()
def sh(cmd, cwd=K):
    try: return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e: return f"(erro ao executar: {e})"

def term(text, title="terminal"):
    return f'<figure class="code term"><figcaption><span class="path">{html.escape(title)}</span></figcaption><pre><code>{html.escape(text.strip())}</code></pre></figure>'

def arquivo(path, quem, quando, casa="REPO"):
    return f'<div class="arquivo"><div class="arq-path"><span class="tag {casa.lower()}">{casa}</span><code>{html.escape(path)}</code></div><div class="arq-meta"><b>Quem lê:</b> {quem} · <b>Quando:</b> {quando}</div></div>'

TREE = """orders-sample/
├── AGENTS.md                          ← contexto canônico: comandos, custos, gotchas, matriz de testes, Never
├── CLAUDE.md                          ← @AGENTS.md + só o que é do Claude (plugins, nomes namespaced)
├── nuget.config                       ← feed por repo (não herda o global da máquina)
├── Directory.Build.props              ← analyzers para todos os projetos (rampa no legado)
├── .editorconfig                      ← severidade das regras vive aqui, nunca NoWarn no csproj
├── Orders.slnx
├── .claude/
│   ├── settings.json                  ← allowlist, deny, hooks de enforcement, plugins esperados
│   ├── hooks/                         ← protect-paths · guard-bash · dotnet-format (bi-plataforma)
│   └── rules/                         ← contracts.md · legacy.md (ativam por caminho)
│       (skills e agentes vêm do plugin kit@whitebeard-kit: card-intake · run-and-test · regras-de-negocio ·
│        impact-analyzer · legacy-navigator · test-designer · dotnet-reviewer · contract-reviewer)
├── .cursor/                           ← hooks.json (beforeShellExecution, beforeReadFile, afterFileEdit) · rules/*.mdc
├── .specs/                            ← tlc-spec-driven (Tech Leads Club, CC-BY-4.0)
│   ├── STATE.md                       ← decisões AD-NNN + handoff
│   ├── LESSONS.md · lessons.json      ← lições grounded (candidate → confirmed)
│   └── features/001-cancelamento-parcial/
│       ├── spec.md                    ← EARS + IDs CANC-01..07 (gate validate_spec.py)
│       ├── design.md                  ← impacto (impact-analyzer), componentes, decisões técnicas
│       ├── tasks.md                   ← Test Coverage Matrix lida do AGENTS.md, gates, T1–T6 (gate validate_tasks.py)
│       └── validation.md              ← Verifier independente: ACs com file:line, sensor de discriminação
├── docs/
│   ├── regras/pedidos.md              ← AS regras (RN-ORD-*), com código e teste de cada uma
│   ├── adr/                           ← 0003 domínio puro · 0004 regra no domínio
│   └── definition-of-ready.md         ← o card só entra se… (porteiro: card-intake)
├── src/
│   ├── Orders.Domain/                 ← Order, OrderItem, Money, Specifications, Events, IOrderRepository
│   ├── Orders.Application/            ← CancelOrderItemHandler (orquestra; não decide) · AssemblyMarker
│   ├── Orders.Infrastructure/         ← InMemoryOrderRepository (adapter)
│   └── Erp.Legacy/                    ← CalculadoraFrete (2014; ninguém explica)
└── tests/Orders.Tests/
    ├── RN_ORD_012_CancelamentoParcialTests.cs   ← 10 testes, um por cláusula EARS (CANC-01..07)
    ├── ArchitectureTests.cs                     ← ADR-0003/0004 como teste
    └── Legacy/CalculadoraFreteCharacterization… ← baseline .verified.txt aprovado por humano"""

TERM_BUILD = """$ dotnet build Orders.slnx
Build succeeded.
    0 Warning(s)
    0 Error(s)
Time Elapsed 00:00:02.79"""

TERM_TEST1 = """$ dotnet test Orders.slnx --no-build
  Failed Orders.Tests.Legacy.CalculadoraFreteCharacterizationTests.Congela_comportamento_atual_do_calculo_de_frete [305 ms]
  Error Message:
  - Received: CalculadoraFreteCharacterizationTests.Congela_comportamento_atual_do_calculo_de_frete.received.txt
    Verified: CalculadoraFreteCharacterizationTests.Congela_comportamento_atual_do_calculo_de_frete.verified.txt
Failed!  - Failed:     1, Passed:     8, Skipped:     0, Total:     9, Duration: 346 ms - Orders.Tests.dll (net10.0)"""

TERM_TEST2 = """$ mv …frete.received.txt …frete.verified.txt     # humano leu os 60 casos e aprovou
$ dotnet test Orders.slnx --no-build
Passed!  - Failed:     0, Passed:     9, Skipped:     0, Total:     9, Duration: 379 ms - Orders.Tests.dll (net10.0)"""

TERM_HOOK = """$ printf '{"tool_input":{"file_path":".../CalculadoraFrete….verified.txt"}}' | bash .claude/hooks/protect-paths.sh
BLOQUEADO (kit Whitebeard): '…/CalculadoraFreteCharacterizationTests.Congela_comportamento_atual_do_calculo_de_frete.verified.txt'
é segredo, migration, artefato gerado ou baseline de characterization test. Mudança aqui passa por humano em PR separado —
veja CLAUDE.md > Never.
exit=2"""

TERM_ARCH = """$ dotnet test Orders.slnx --filter "FullyQualifiedName~ArchitectureTests"
  Failed Orders.Tests.ArchitectureTests.Application_nao_lanca_DomainRuleViolationException [10 ms]
  Error Message:
   ArchUnitNET.xUnit.FailedArchRuleException : "Types that are Application should not depend on any Types that are
   "Orders.Domain.DomainRuleViolationException" because viola ADR-0004 (regra de negócio vive no domínio).
   Correção: mova a verificação para a entidade ou specification e chame-a do handler." failed:
Failed!  - Failed:     1, Passed:     2, Skipped:     0, Total:     3, Duration: 435 ms - Orders.Tests.dll (net10.0)"""

TERM_CA1710 = """$ dotnet build Orders.slnx
src/Orders.Domain/DomainRuleViolation.cs(4,21): error CA1710: Rename Orders.Domain.DomainRuleViolation to end in 'Exception'
tests/Orders.Tests/Orders.Tests.csproj : error NU1301: Unable to load the service index for source
  https://<feed-de-outro-cliente>.d.codeartifact.us-east-1.amazonaws.com/nuget/…/index.json
tests/Orders.Tests/Orders.Tests.csproj : error NU1301:   Response status code does not indicate success: 401 (Unauthorized)"""

ARTIFACT_ROTEIRO = "https://claude.ai/code/artifact/e53c902f-b3b0-4334-b3f8-cc52c73f26bb"

TERM_PLUGIN = """$ claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git
✔ Successfully added marketplace: whitebeard-kit
$ claude plugin install kit@whitebeard-kit
✔ Successfully installed plugin: kit@whitebeard-kit (scope: user) (+ 1 dependency: tlc)
$ ls ~/.claude/plugins/cache/whitebeard-kit/tlc/*/scripts
check_commit.py  lessons.py  validate_spec.py  validate_state.py  validate_tasks.py      # 3.3.0, direto do repo do Tech Leads Club"""

TERM_VALIDATE_SPEC = """$ python3 <skill-dir>/scripts/validate_spec.py 001-cancelamento-parcial
validate_spec: 0 error(s), 0 warning(s) in .specs/features/001-cancelamento-parcial/spec.md"""

TERM_VALIDATE_TASKS = """$ python3 <skill-dir>/scripts/validate_tasks.py 001-cancelamento-parcial
  WARN  T1: Tests: none - confirm the Test Coverage Matrix says 'none' for this layer
  WARN  T3: `Where` names multiple files [...] - granularity smell, consider splitting
  ERROR T5 declares `Depends on: T4` but the diagram has no T4 -> T5 arrow
validate_tasks: 1 error(s), 5 warning(s)
$ # seta T4 → T5 acrescentada ao diagrama da fase 2
$ python3 <skill-dir>/scripts/validate_tasks.py 001-cancelamento-parcial
validate_tasks: 0 error(s), 5 warning(s)"""

TERM_CHECK_COMMIT = """$ python3 <skill-dir>/scripts/check_commit.py --message "feat(orders): Order.CancelItem com recálculo, evento único, ..."
check_commit: FAIL - see https://www.conventionalcommits.org/en/v1.0.0/     # descrição começa com maiúscula
$ python3 <skill-dir>/scripts/check_commit.py --message "feat(orders): adicionar Order.CancelItem — recálculo, evento único, ..."
check_commit: OK"""

TERM_T5_FALSE_GREEN = """$ dotnet build Orders.slnx | grep error
tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs(136,24): error CS0246: The type or namespace name
  'InMemoryOrderRepository' could not be found (are you missing a using directive or an assembly reference?)
$ dotnet test Orders.slnx --no-build
Passed!  - Failed: 0, Passed: 12, Skipped: 0, Total: 12      # ← binário ANTERIOR. Falso verde."""

TERM_LESSON = """$ python3 <skill-dir>/scripts/lessons.py add --feature 001-cancelamento-parcial --signal gate_fail \\
    --source "tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs:136" \\
    --text "Run every gate with a fresh build and check exit codes; never judge a gate with --no-build" --scope tests
ADDED L-001 (status=candidate, recurrence=1)"""


page = f"""<title>Engenharia com Agentes em .NET</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Serif+4:opsz,ital,wght@8..60,0,400;8..60,0,600;8..60,1,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
:root{{--bg:#F9F7F2;--paper:#FFFFFF;--ink:#23281F;--ink-soft:#5D6355;--accent:#315C45;--accent-soft:#E7EFE7;--rule:#DFDACB;--tech-bg:#EFEDE4;--mono-bg:#EFEDE4;--term-bg:#1E241F;--term-ink:#DCE6D9;--warn:#8A5A12;--warn-soft:#F4ECDD;
--tag-repo:#E7EFE7;--tag-vault:#EFE7D6;--tag-gen:#E7E7F0;--tag-org:#F0E4E4}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#171A15;--paper:#1F2420;--ink:#E7E9E0;--ink-soft:#A5AC9B;--accent:#8FBF9F;--accent-soft:#24322A;--rule:#3A4038;--tech-bg:#262B24;--mono-bg:#262B24;--term-bg:#0F130F;--term-ink:#C9D6C5;--warn:#D9A441;--warn-soft:#2E2A1E;--tag-repo:#24322A;--tag-vault:#3A3320;--tag-gen:#262640;--tag-org:#3D2626}}}}
:root[data-theme="dark"]{{--bg:#171A15;--paper:#1F2420;--ink:#E7E9E0;--ink-soft:#A5AC9B;--accent:#8FBF9F;--accent-soft:#24322A;--rule:#3A4038;--tech-bg:#262B24;--mono-bg:#262B24;--term-bg:#0F130F;--term-ink:#C9D6C5;--warn:#D9A441;--warn-soft:#2E2A1E;--tag-repo:#24322A;--tag-vault:#3A3320;--tag-gen:#262640;--tag-org:#3D2626}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:"Source Serif 4",Georgia,serif;font-size:17px;line-height:1.6}}
a{{color:var(--accent)}}
a:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.wrap{{max-width:74ch;margin:0 auto;padding:48px 24px 96px}}
h1,h2,h3{{font-family:"Fraunces",Georgia,serif;line-height:1.15;text-wrap:balance;margin:0}}
h1{{font-size:2.7rem;font-weight:700;font-variation-settings:"opsz" 144}}
h2{{font-size:1.9rem;font-weight:700;margin:64px 0 8px;padding-top:24px;border-top:1px solid var(--rule)}}
h3{{font-size:1.2rem;font-weight:600;margin:32px 0 8px}}
p{{margin:0 0 16px}}
.eyebrow{{font-family:"JetBrains Mono",monospace;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft)}}
.cover{{padding-bottom:32px;border-bottom:2px solid var(--ink);margin-bottom:8px}}
.cover .lede{{font-size:1.2rem;color:var(--ink-soft);max-width:60ch;margin-top:16px}}
.cover .meta{{font-family:"JetBrains Mono",monospace;font-size:.78rem;color:var(--ink-soft);margin-top:20px;display:flex;gap:20px;flex-wrap:wrap}}
nav.toc{{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:18px 22px;margin:28px 0 8px}}
nav.toc ol{{margin:8px 0 0;padding-left:22px;columns:2;column-gap:28px;font-size:.95rem}}
nav.toc li{{margin-bottom:5px;break-inside:avoid}}
nav.toc a{{text-decoration:none;border-bottom:1px solid var(--rule)}}
code{{font-family:"JetBrains Mono",monospace;font-size:.85em;background:var(--mono-bg);padding:.08em .35em;border-radius:3px}}
figure.code{{margin:18px 0 22px;background:var(--paper);border:1px solid var(--rule);border-radius:6px;overflow:hidden}}
figure.code figcaption{{font-family:"JetBrains Mono",monospace;font-size:.74rem;padding:7px 14px;border-bottom:1px solid var(--rule);color:var(--ink-soft);background:var(--tech-bg)}}
figure.code pre{{margin:0;padding:14px 16px;overflow-x:auto;font-size:.82rem;line-height:1.5}}
figure.code pre code{{background:none;padding:0;font-size:1em}}
figure.term{{background:var(--term-bg)}}
figure.term figcaption{{background:var(--term-bg);color:var(--term-ink);border-bottom-color:#33403a;opacity:.85}}
figure.term pre{{color:var(--term-ink)}}
.box{{border-radius:6px;padding:16px 20px;margin:20px 0}}
.box .lbl{{font-family:"JetBrains Mono",monospace;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;display:block;margin-bottom:6px}}
.box.tech{{background:var(--tech-bg);border-left:4px solid var(--accent)}}
.box.analogia{{background:var(--accent-soft);border-left:4px solid var(--accent)}}
.box.honesto{{background:var(--warn-soft);border-left:4px solid var(--warn)}}
.box p:last-child{{margin-bottom:0}}
.arquivo{{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:10px 14px;margin:10px 0}}
.arq-path{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.arq-path code{{font-size:.82rem}}
.arq-meta{{font-size:.9rem;color:var(--ink-soft);margin-top:4px}}
.tag{{font-family:"JetBrains Mono",monospace;font-size:.66rem;letter-spacing:.06em;padding:2px 7px;border-radius:3px}}
.tag.repo{{background:var(--tag-repo)}}.tag.vault{{background:var(--tag-vault)}}.tag.gen{{background:var(--tag-gen)}}.tag.org{{background:var(--tag-org)}}
.tbl{{overflow-x:auto;margin:14px 0 20px;border:1px solid var(--rule);border-radius:6px;background:var(--paper)}}
table{{border-collapse:collapse;width:100%;font-size:.92rem}}
th,td{{text-align:left;padding:8px 12px;border-bottom:1px solid var(--rule);vertical-align:top}}
th{{font-family:"JetBrains Mono",monospace;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);font-weight:600;background:var(--tech-bg)}}
tr:last-child td{{border-bottom:0}}
ul,ol{{padding-left:22px}} li{{margin-bottom:6px}}
.steps{{counter-reset:s;list-style:none;padding-left:0}}
.steps li{{position:relative;padding-left:36px;margin-bottom:10px}}
.steps li::before{{counter-increment:s;content:counter(s);position:absolute;left:0;top:2px;width:24px;height:24px;border-radius:50%;background:var(--accent);color:var(--bg);font-family:"JetBrains Mono",monospace;font-size:.75rem;display:flex;align-items:center;justify-content:center}}
.glos dt{{font-weight:600;margin-top:10px}} .glos dd{{margin:2px 0 0 0;color:var(--ink-soft)}}
pre.mermaid{{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:12px;overflow-x:auto}}
@media (max-width:640px){{h1{{font-size:2.1rem}} nav.toc ol{{columns:1}} .wrap{{padding:28px 16px 72px}}}}
</style>
<div class="wrap">
<header class="cover">
  <div class="eyebrow">E-book Whitebeard · nº 3 · 27 ago 2026 · rev. 2 — 29 ago (tlc-spec-driven como motor)</div>
  <h1 style="margin-top:10px">Engenharia com Agentes em .NET</h1>
  <p class="lede">Onde fica cada arquivo, o que ele faz e como se usa — num serviço .NET de verdade, com monolito legado ao lado, compilado e testado antes de entrar neste texto.</p>
  <div class="meta"><span>kit: <code>github.com/whitebeardit/agentic-engineering-kit</code> (plugin Claude + Cursor)</span><span>exemplo: <code>samples/orders-sample</code></span><span>.NET SDK 10.0.103</span><span>14/14 testes · feature 001 conduzida pelo tlc-spec-driven 3.3.0</span></div>
</header>

<nav class="toc"><div class="eyebrow">Capítulos</div><ol>
<li><a href="#c1">Por que um kit, e não um prompt</a></li>
<li><a href="#c2">As quatro casas: onde cada coisa fica</a></li>
<li><a href="#c3">A árvore do exemplo, arquivo por arquivo</a></li>
<li><a href="#c4">AGENTS.md: o que o agente não adivinha</a></li>
<li><a href="#c5">Hooks, permissões e rules: o que é garantia</a></li>
<li><a href="#c6">Regra de negócio mora no domínio</a></li>
<li><a href="#c7">ADR que falha o build</a></li>
<li><a href="#c8">Legado: congelar antes de mexer</a></li>
<li><a href="#c9">Do card ao PR: card-intake, tlc-spec-driven e o Verifier</a></li>
<li><a href="#c10">Qualidade que o build impõe (e três lições reais)</a></li>
<li><a href="#c11">Contratos entre serviços</a></li>
<li><a href="#c12">As 7 fases e como a Whitebeard usa isto</a></li>
<li><a href="#apendice">Apêndice: comandos, pendências, glossário</a></li>
</ol></nav>

<p><b>Como ler.</b> Cada capítulo mostra arquivos reais do exemplo <code>orders-sample</code> — o texto é gerado a partir deles, então o que você lê é o que compila. O método de spec (capítulo 9) é o <b>tlc-spec-driven</b> do Tech Leads Club (Felipe Rodrigues, CC-BY-4.0), instalado sempre do repositório original; o kit Whitebeard é a adaptação em volta dele. Caixas <em>Para quem é técnico</em> aprofundam; caixas <em>Honestidade</em> dizem o que ainda não está provado. Não há chamada comercial: é um texto de método.</p>

<!-- ======================= C1 ======================= -->
<h2 id="c1"><span class="eyebrow">Capítulo 1</span><br>Por que um kit, e não um prompt</h2>
<p>Uma empresa .NET típica tem um monolito de dez anos, uma dúzia de microserviços mais novos, cards no Jira e um time que já usa IA para escrever código. O que ela não tem é um lugar onde a IA <em>aprende como a empresa funciona</em> — e por isso cada sessão começa do zero, cada engenheiro cola o mesmo contexto, e a qualidade do resultado depende de quem digitou o prompt.</p>
<p>A pesquisa que fundamenta este e-book (DORA 2024/2025, Anthropic, Thoughtworks, OpenAI, GitClear, METR — reunida no <a href="{ARTIFACT_ROTEIRO}">Roteiro de Engenharia com Agentes</a>) converge em sete princípios. O kit existe para <em>impor</em> os sete, não para descrevê-los:</p>
<div class="tbl"><table><thead><tr><th>Princípio</th><th>No kit vira…</th></tr></thead><tbody>
<tr><td>IA é amplificador: fundação antes do agente</td><td>fase 0 (baseline, branch protection, testes rodando) antes de qualquer <code>.claude/</code></td></tr>
<tr><td>Contexto mínimo e concreto</td><td><code>CLAUDE.md</code> com comandos, custos e gotchas; nunca prosa de arquitetura</td></tr>
<tr><td>Enforcement mecânico &gt; texto</td><td>hooks que bloqueiam, analyzers que falham o build, testes de arquitetura</td></tr>
<tr><td>Spec antes do código, gate humano no meio</td><td><code>card-intake</code> (DoR) → tlc-spec-driven: <code>.specs/features/&lt;f&gt;/</code> com gates determinísticos (<code>validate_spec.py</code>, <code>validate_tasks.py</code>)</td></tr>
<tr><td>Autor ≠ verificador</td><td>Verifier do tlc em contexto limpo (spec-anchored + sensor de discriminação); <code>dotnet-reviewer</code> antes do humano</td></tr>
<tr><td>Cada erro vira artefato</td><td>lição grounded em <code>.specs/LESSONS.md</code> (tlc) → linha no AGENTS.md, teste, rule ou hook — nunca "tome mais cuidado"</td></tr>
<tr><td>Segurança na borda</td><td>deny de segredos, sandbox, conteúdo externo como input não confiável</td></tr>
</tbody></table></div>
<div class="box analogia"><span class="lbl">Analogia</span><p>Contratar um engenheiro sênior excelente e colocá-lo num prédio sem placas, sem crachá e sem manual de emergência. Ele vai trabalhar — e vai errar coisas que qualquer estagiário do prédio sabe. O kit são as placas, o crachá e o manual. O agente é o sênior.</p></div>

<!-- ======================= C2 ======================= -->
<h2 id="c2"><span class="eyebrow">Capítulo 2</span><br>As quatro casas: onde cada coisa fica</h2>
<p>A pergunta "onde eu coloco isso?" tem quatro respostas possíveis, e misturá-las é a causa número um de artefato que apodrece.</p>
<div class="tbl"><table><thead><tr><th>Casa</th><th>O que vive lá</th><th>Por quê</th></tr></thead><tbody>
<tr><td><span class="tag repo">REPO</span></td><td>AGENTS.md/CLAUDE.md, <code>.claude/</code>, <code>.specs/</code>, ADRs, <code>docs/regras/</code> do domínio que o serviço é dono, testes</td><td>muda junto com o código; revisado em PR; quem não usa IA também lê</td></tr>
<tr><td><span class="tag vault">VAULT</span></td><td>mapa da empresa (quem fala com quem, tabelas compartilhadas, ordem de release), regras transversais, glossário, nota por card</td><td>nenhum repo é dono do que atravessa quatro repos</td></tr>
<tr><td><span class="tag gen">GERADO</span></td><td>grafo de dependências, inventário de endpoints/eventos, relatórios de analyzers e mutation</td><td>derivável do código: gera em CI, nunca escreve à mão, nunca entra no CLAUDE.md</td></tr>
<tr><td><span class="tag org">ORG</span></td><td>política de uso de IA, deny de segredos, sandbox, allowlist de MCP</td><td>enforcement que o desenvolvedor não remove (managed settings)</td></tr>
</tbody></table></div>
<p>E a regra de decisão para artefatos novos, na ordem em que a Anthropic a formula, com as duas casas extras da empresa:</p>
<ul>
<li>Fato curto que vale sempre → <code>AGENTS.md</code> (o <code>CLAUDE.md</code> só o importa)</li>
<li>Restrição que só vale em certos caminhos → <code>.claude/rules/*.md</code> com <code>paths:</code></li>
<li>Procedimento que você colou pela terceira vez → skill</li>
<li>Deve acontecer sempre, sem exceção → hook</li>
<li>Tarefa que inunda o contexto → subagente</li>
<li>Serviço ou dado externo → MCP · Mesmo setup em segundo repo → plugin (o kit já é um: <code>kit@whitebeard-kit</code>)</li>
<li>Conhecimento que cruza serviços → vault (consultado por MCP) · Derivável do código → gerado em CI</li>
</ul>

<!-- ======================= C3 ======================= -->
<h2 id="c3"><span class="eyebrow">Capítulo 3</span><br>A árvore do exemplo, arquivo por arquivo</h2>
<p>O exemplo é um serviço de Pedidos com domínio, aplicação, infraestrutura, um pedaço de monolito legado e os testes que provam tudo isso. Foi criado com <code>apply.sh --claude --cursor --dotnet</code> do kit, com o plugin <code>kit@whitebeard-kit</code> instalado (que traz o tlc-spec-driven como dependência), e a feature 001 foi conduzida pelo tlc de ponta a ponta. Esta é a árvore como está no disco:</p>
{term(TREE, "samples/orders-sample")}
<p>Cada arquivo abaixo tem duas perguntas respondidas: <b>quem lê</b> e <b>quando</b>. Se você não consegue responder as duas para um arquivo do seu repositório, ele provavelmente não deveria existir.</p>
{arquivo("AGENTS.md","qualquer agente (Claude Code, Cursor, Copilot) e o tlc-spec-driven ao montar a matriz de testes; humanos no onboarding","sempre que um agente abre no repo")}
{arquivo("CLAUDE.md","só o Claude Code — importa o AGENTS.md e acrescenta nomes de plugin","toda sessão do Claude")}
{arquivo(".claude/settings.json","o harness do Claude Code — não o modelo","antes de cada tool call (hooks) e em cada permissão")}
{arquivo(".claude/rules/legacy.md","o agente, só ao tocar arquivos que batem no glob","ao editar src/Erp.Legacy/**")}
{arquivo(".specs/features/001-cancelamento-parcial/validation.md","o revisor do PR e o gate validate_state.py","escrito pelo Verifier do tlc após a última task; sem ele a feature não está pronta")}
{arquivo("skills/regras-de-negocio/SKILL.md (plugin kit)","o agente, ao tocar docs/regras/ ou o Domain, ou quando invocada","antes de implementar critério que muda comportamento")}
{arquivo("docs/regras/pedidos.md","card-intake, Verifier, PO e engenheiro — todos a mesma versão","antes de escrever spec; ao mudar comportamento")}
{arquivo("docs/adr/0004-regra-no-dominio.md","quem vê 'viola ADR-0004' no build","quando o teste de arquitetura falha")}
{arquivo(".specs/features/001-cancelamento-parcial/tasks.md","o agente executor (uma task por sessão) e o Verifier","durante a implementação — cada task fecha com gate + commit atômico")}
{arquivo("tests/Orders.Tests/Legacy/….verified.txt","um humano, na primeira execução e a cada mudança","antes de qualquer refactor no legado")}
{arquivo(".specs/LESSONS.md","o agente no Specify e no Design (lições confirmed) e o ritual quinzenal","lida antes de especificar; escrita só pelo lessons.py a partir de sinal do Verifier")}

<!-- ======================= C4 ======================= -->
<h2 id="c4"><span class="eyebrow">Capítulo 4</span><br>AGENTS.md: o que o agente não adivinha</h2>
<p>Um estudo de ablação com 288 execuções (jul/2026) mediu que instruções genéricas de arquitetura e estilo no arquivo de contexto <em>não melhoram a correção</em> — enquanto avisos concretos como "a suíte completa leva 20 minutos" cortaram reexecuções em 45 %. A Anthropic recomenda menos de 200 linhas; a meta do roteiro Whitebeard é ainda mais curta, ≤ 150 por repositório. A pergunta-poda: <em>remover esta linha faria o agente errar?</em></p>
<p>É por isso que o <code>AGENTS.md</code> do exemplo tem comandos com <b>tempo medido</b>, definição de pronto como exit code, gotchas — e a <b>matriz de testes por camada</b> que o tlc-spec-driven lê para montar a Test Coverage Matrix de cada feature. Nada sobre "arquitetura limpa". É <code>AGENTS.md</code>, não <code>CLAUDE.md</code>, porque Cursor, Copilot e o próprio tlc leem o mesmo arquivo:</p>
{code("AGENTS.md","md",title="orders-sample/AGENTS.md")}
<p>O <code>CLAUDE.md</code> vira duas linhas de import e o que só o Claude precisa saber:</p>
{code("CLAUDE.md","md",title="orders-sample/CLAUDE.md")}
<p>No workspace pai (o diretório que contém todos os repos) vive um segundo <code>AGENTS.md</code>, com a tabela de serviços, a ordem padrão entre eles e a etiqueta de PR. O agente é iniciado no subdiretório do serviço; o raiz carrega junto.</p>
{code("templates/AGENTS.root.md","md",title="kit/templates/AGENTS.root.md (workspace pai)")}
<h3>Como usar</h3>
<ol class="steps">
<li><code>apply.sh /repo --claude --cursor --with-tlc --dotnet</code> cria o esqueleto e instala o plugin (com o tlc); <code>/init</code> dentro do Claude rascunha o resto.</li>
<li>Pode linha a linha. Comando com custo fica; "escreva código limpo" sai.</li>
<li><code>/context</code> mostra a carga: abaixo de 10 % do contexto está bom.</li>
<li>Toda vez que o agente errar por não saber algo do repo, uma linha entra aqui — e só assim ele cresce. No exemplo, o gotcha "nunca julgue um gate com <code>--no-build</code>" nasceu de um erro real durante a feature 001 (capítulo 9).</li>
</ol>
<div class="box tech"><span class="lbl">Para quem é técnico</span><p>Hierarquia de carga: <code>~/.claude/CLAUDE.md</code> (pessoal) → raiz do workspace → repo → <code>CLAUDE.local.md</code> (gitignore). Subdiretórios carregam sob demanda quando o agente lê arquivos neles. <code>@path</code> importa outro arquivo <em>no launch</em> (não economiza tokens, só organiza). Comentários HTML são removidos antes de injetar — servem para notas humanas sem custo.</p></div>

<!-- ======================= C5 ======================= -->
<h2 id="c5"><span class="eyebrow">Capítulo 5</span><br>Hooks, permissões e rules: o que é garantia</h2>
<p>"Nunca edite o <code>.env</code>" no CLAUDE.md é um pedido. Um hook <code>PreToolUse</code> que retorna exit 2 é uma garantia: dispara antes de qualquer checagem de permissão, em todo modo — inclusive <code>bypassPermissions</code>. A diferença é a mesma entre uma placa e uma catraca. Uma ressalva honesta: um hook de repositório pode ser desligado por quem edita o <code>settings.json</code> (<code>disableAllHooks</code>); a garantia que sobrevive a isso é o hook <em>gerenciado</em> pela organização (<code>allowManagedHooksOnly</code>), que é assunto da fase 5.</p>
{code(".claude/settings.json","json",title="orders-sample/.claude/settings.json")}
<p>Os três hooks são scripts curtos, escritos para <em>explicar ao agente</em> por que foi bloqueado e o que fazer — não só para negar. São bi-plataforma: o mesmo script lê o payload do Claude Code (<code>tool_input</code> → exit 2 + stderr) ou do Cursor (<code>file_path</code>/<code>command</code> → JSON <code>{{"permission":"deny"}}</code>; em <code>afterFileEdit</code>, reverte o arquivo, porque o Cursor não tem hook pré-escrita):</p>
{code(".claude/hooks/protect-paths.sh","bash",title=".claude/hooks/protect-paths.sh (PreToolUse · Edit|Write)")}
<p>Testado de verdade contra o baseline do characterization test:</p>
{term(TERM_HOOK, "hook em ação (27-08-2026)")}
{code(".claude/hooks/guard-bash.sh","bash",title=".claude/hooks/guard-bash.sh (PreToolUse · Bash)")}
<p>As <b>rules</b> são o meio-termo: texto, mas só carregado quando o agente toca certos caminhos. É onde vive o que é verdade só no legado ou só em contratos:</p>
{code(".claude/rules/legacy.md","md",title=".claude/rules/legacy.md (ativa por paths:)")}
<div class="box tech"><span class="lbl">Para quem é técnico</span><p>Precedência de permissões: <b>deny → ask → allow</b>, primeiro match ganha. Negar <code>WebFetch</code> não impede <code>curl</code> — só o sandbox de SO (<code>/sandbox</code>, bubblewrap no Linux) fecha o egresso. <code>PostToolUse</code> não bloqueia (a ação já aconteceu): serve para formatar e para devolver erro de build ao agente na hora. O <code>dotnet-format.sh</code> formata só o <code>.cs</code> tocado, no projeto dono dele, e nunca falha o turno.</p></div>

<!-- ======================= C6 ======================= -->
<h2 id="c6"><span class="eyebrow">Capítulo 6</span><br>Regra de negócio mora no domínio</h2>
<p>"Onde fica a regra de negócio?" tem duas respostas, e as duas precisam concordar: <b>no código</b>, como comportamento imposto pela camada de domínio; <b>na documentação</b>, num arquivo que o PO, o engenheiro e o agente leem na mesma versão. O card do Jira descreve a <em>mudança</em>; <code>docs/regras/</code> descreve o <em>estado</em>.</p>
<h3>1. A regra escrita, com ID</h3>
{snip("docs/regras/pedidos.md", r"^## RN-ORD-012", r"^## Regras transversais", "md", "docs/regras/pedidos.md — bloco RN-ORD-012", include_end=False)}
<h3>2. A regra imposta: agregado, value object, specification</h3>
<p>Invariante de entidade vira método do agregado; valor válido vira value object que nasce válido ou não nasce; predicado reutilizável vira specification. Nada disso é sugestão: o teste de arquitetura do capítulo 7 falha se a regra aparecer fora do domínio.</p>
{snip("src/Orders.Domain/Order.cs", r"summary>RN-ORD-012", r"^    }$", "csharp", "src/Orders.Domain/Order.cs — CancelItem (RN-ORD-012)")}
{code("src/Orders.Domain/Specifications/PedidoElegivelParaCancelamento.cs","csharp")}
{snip("src/Orders.Domain/Money.cs", r"^namespace", r"public static Money Brl", "csharp", "src/Orders.Domain/Money.cs — value object (RN-ORD-001), trecho")}
<h3>3. A aplicação orquestra e não decide</h3>
{code("src/Orders.Application/CancelOrderItem/CancelOrderItemHandler.cs","csharp")}
<h3>4. A prova: um teste por cláusula EARS, com o ID no nome</h3>
{snip("tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs", r"^public class RN_ORD_012", r"SHALL_ser_idempotente", "csharp", "tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs (trecho: 5 de 10 testes — CANC-06, 01, 02, 03)", include_end=False)}
<p>O nome do teste repete a cláusula da regra. Quem lê <code>docs/regras</code>, o teste ou a exceção com <code>RuleId</code> chega ao mesmo lugar — e o Verifier do tlc cruza os três com <code>file:line</code>.</p>
<p>Isto <em>não</em> é TDD forçado no loop do agente — prática que a Thoughtworks mediu sem ganho de qualidade e com 3–8× de custo em tokens, e que o roteiro desaconselha. É outra coisa: um teste por cláusula EARS, escrito <b>uma vez</b> a partir da spec pelo <code>test-designer</code> (ou numa sessão separada), que fica vermelho até a regra existir e depois vira sensor permanente. Quem implementa não edita esses testes; faz passar.</p>
<h3>5. A skill: o procedimento, não o conhecimento</h3>
<p>A skill <code>regras-de-negocio</code> vive no repo dono do domínio, ativa por <code>paths:</code> e <em>aponta</em> para <code>docs/regras/</code> — se ela embutisse as regras, as duas cópias divergiriam em duas semanas.</p>
{code("skills/regras-de-negocio/SKILL.md","md",title="kit/skills/regras-de-negocio/SKILL.md (no plugin: /kit:regras-de-negocio)")}
<div class="box analogia"><span class="lbl">Analogia</span><p>A regra escrita é a lei no Diário Oficial; o método do agregado é a catraca que a aplica; o teste é o fiscal que passa todo dia; a skill é o procedimento do cartório para mudar a lei. Quatro coisas, quatro lugares — e um único número de protocolo, <code>RN-ORD-012</code>, ligando todas.</p></div>

<!-- ======================= C7 ======================= -->
<h2 id="c7"><span class="eyebrow">Capítulo 7</span><br>ADR que falha o build</h2>
<p>Um ADR carregado no contexto é informação; um ADR com <code>enforced-by</code> é regra. O exemplo tem dois, e cada um aponta o teste que o impõe:</p>
{code("docs/adr/0004-regra-no-dominio.md","md")}
{code("tests/Orders.Tests/ArchitectureTests.cs","csharp")}
<p>Para provar que funciona, criamos de propósito um arquivo em <code>Orders.Application</code> que lançava <code>DomainRuleViolationException</code> (a regra "no atalho", dentro do handler). O build passou — o compilador não se importa. O teste de arquitetura, não:</p>
{term(TERM_ARCH, "violação proposital do ADR-0004 (27-08-2026)")}
<p>Repare na mensagem: ela cita o ADR e diz o passo de correção. É escrita para o agente ler e agir — o mesmo princípio dos linters customizados do harness da OpenAI. Depois do teste, o arquivo foi removido e a suíte voltou a 9/9.</p>

<!-- ======================= C8 ======================= -->
<h2 id="c8"><span class="eyebrow">Capítulo 8</span><br>Legado: congelar antes de mexer</h2>
<p>Ninguém explica os números de <code>CalculadoraFrete</code>. É código de 2014, roda em produção e três times dependem dele sem saber. Refatorar isso com um agente — ou sem — começa por uma coisa: <em>congelar o comportamento atual</em>, não o desejado.</p>
{code("src/Erp.Legacy/CalculadoraFrete.cs","csharp")}
<p>O characterization test gera 60 casos com dados aleatórios de <b>seed fixo</b> (repetíveis), passa pelo código e grava o resultado. Na primeira execução ele <em>falha por desenho</em>: não existe baseline ainda.</p>
{code("tests/Orders.Tests/Legacy/CalculadoraFreteCharacterizationTests.cs","csharp")}
{term(TERM_TEST1, "1ª execução: cria o .received.txt e falha")}
<p>Aqui entra o humano. Ele abre o <code>.received.txt</code>, confere se aqueles 60 resultados são o que produção faz hoje, e só então renomeia para <code>.verified.txt</code>. O hook do capítulo 5 impede que o agente faça isso sozinho.</p>
{code("tests/Orders.Tests/Legacy/CalculadoraFreteCharacterizationTests.Congela_comportamento_atual_do_calculo_de_frete.verified.txt","txt",start=1,end=17,title="….verified.txt (baseline aprovado — 60 casos, 464 linhas)")}
{term(TERM_TEST2, "2ª execução: baseline aprovado")}
<p>A partir daqui, qualquer refactor que mude um centavo em qualquer dos 60 casos falha o teste. E como o arquivo está protegido, "arrumar" o baseline exige um PR separado explicando a mudança de comportamento — é a <code>rules/legacy.md</code> em ação.</p>
<div class="box tech"><span class="lbl">Para quem é técnico</span><p>Verify (VerifyTests) suporta de <code>net462</code> a <code>net10</code>; no .NET Framework use SDK 9.0.301+. Bogus com <code>new Randomizer(seed)</code> garante repetibilidade. No CI, <code>DiffEngine_Disabled=true</code> evita que o Verify tente abrir um diff tool. O projeto legado compila em <code>AnalysisMode=Minimum</code> — a rampa sobe um degrau por sprint, e o kit deixa isso explícito no <code>Directory.Build.props</code>.</p></div>

<!-- ======================= C9 ======================= -->
<h2 id="c9"><span class="eyebrow">Capítulo 9</span><br>Do card ao PR: card-intake, tlc-spec-driven e o Verifier</h2>
<p>O motor deste capítulo não é nosso. É o <b>tlc-spec-driven</b> do Tech Leads Club (Felipe Rodrigues, CC-BY-4.0): quatro fases auto-dimensionadas — Specify, Design, Tasks, Execute — com gates determinísticos em scripts, um Verifier independente que injeta falhas para provar que os testes discriminam, memória em <code>STATE.md</code> e lições que só nascem de sinal real. O kit Whitebeard entra <em>em volta</em>: o porteiro <code>card-intake</code> antes do Specify, o <code>impact-analyzer</code> como primeiro passo do Design, a matriz de testes no <code>AGENTS.md</code> que o tlc lê, e o enforcement que ele não cobre. E o tlc é instalado sempre do repositório original deles — como dependência do plugin:</p>
{term(TERM_PLUGIN, "instalação (27–29 ago 2026)")}
<pre class="mermaid">
flowchart LR
  J[Card ORD-231] -->|/kit:card-intake · DoR| B[briefing]
  B -->|specify feature| S[spec.md · validate_spec.py]
  S -->|gate 1: PO| I[kit:impact-analyzer]
  I --> D[design.md]
  D --> T[tasks.md · matriz do AGENTS.md · validate_tasks.py]
  T -->|gate 2: tech lead| E[Execute: teste → código → gate → check_commit]
  E -->|última task| V[Verifier: file:line · sensor · validation.md · validate_state.py]
  V -->|sinal| L[LESSONS.md]
  V -->|PASS| PR[PR draft + validation.md]
  PR -->|UAT com o PO| W[nota no vault]
</pre>
<p>Tudo abaixo aconteceu de verdade em 29 de agosto de 2026 no <code>orders-sample</code>: a feature RN-ORD-012 foi <b>removida</b> do código e reconstruída pelo fluxo, com os scripts 3.3.0 do tlc rodando a cada passo.</p>

<h3>1. O card e o porteiro</h3>
<p>O card chegou como texto (o MCP do Jira não estava conectado nesta sessão — o adaptador de texto é exatamente para isso). O <code>card-intake</code> aplicou o Definition of Ready, dimensionou e parou no gate:</p>
{term(asset("card-ORD-231.md"), "ORD-231, como veio do PO")}
{term(asset("briefing-card-intake.md"), "/kit:card-intake · saída (briefing para o Specify — não é spec)")}

<h3>2. Specify: a spec com IDs e o gate que não depende de memória</h3>
<p>O tlc escreve <code>spec.md</code> com problema, fora de escopo, assumptions (nada fica "silenciosamente" indefinido), histórias com critérios EARS e uma tabela de rastreabilidade. Antes de pedir confirmação, o script valida seções, IDs e forma dos critérios:</p>
{snip(".specs/features/001-cancelamento-parcial/spec.md", r"^### P1:", r"^\*\*Independent Test\*\*", "md", ".specs/features/001-cancelamento-parcial/spec.md — P1 (CANC-01..07)")}
{snip(".specs/features/001-cancelamento-parcial/spec.md", r"^## Assumptions", r"^\*\*Open questions", "md", "spec.md — Assumptions & Open Questions (o que decidimos por default e o que fica para o PO)")}
{term(TERM_VALIDATE_SPEC, "gate determinístico do Specify")}

<h3>3. Design: o impact-analyzer entra primeiro</h3>
<p>Para um card que cruza serviços, o Design não é pulado. O primeiro passo é o agente <code>kit:impact-analyzer</code> (só leitura), que devolveu a tabela de impacto e três achados que a spec não tinha: o gancho <code>OrderItem.Cancel()</code> já existia sem ninguém chamar; <b>não há mecanismo de publicação de eventos</b> no exemplo; e o "ERP" do card não é o <code>Erp.Legacy</code> deste repo.</p>
{snip(".specs/features/001-cancelamento-parcial/design.md", r"^## Impacto", r"^## Code Reuse", "md", "design.md — Impacto (saída do impact-analyzer)", include_end=False)}
{snip(".specs/features/001-cancelamento-parcial/design.md", r"^## Tech Decisions", None, "md", "design.md — Tech Decisions (o que foi decidido e o que foi deixado fora)")}

<h3>4. Tasks: a matriz de testes vem do AGENTS.md</h3>
<p>O tlc monta a Test Coverage Matrix lendo as diretrizes do repo — e é por isso que o <code>AGENTS.md</code> do capítulo 4 tem aquela tabela por camada. Seis tasks em duas fases, cada uma com <code>Done when</code>, tipo de teste e gate. O script pegou um erro real no diagrama:</p>
{snip(".specs/features/001-cancelamento-parcial/tasks.md", r"^## Test Coverage Matrix", r"^## Execution Plan", "md", "tasks.md — Test Coverage Matrix e Gate Check Commands", include_end=False)}
{term(TERM_VALIDATE_TASKS, "gate determinístico das Tasks")}

<h3>5. Execute: teste vermelho, código, gate, commit atômico</h3>
<p>Cada task segue o mesmo ciclo. O teste é escrito <b>a partir da cláusula da spec</b>, antes do código — em C#, "vermelho" é erro de compilação:</p>
{term(asset("gate-T4-red.txt").strip(), "T4 · gate antes da implementação")}
{term(asset("gate-T4.txt").strip(), "T4 · gate depois (build fresco, 0 warnings)")}
<p>O commit só é aceito se a mensagem passar no <code>check_commit.py</code> (Conventional Commits). O script reprovou a minha primeira tentativa:</p>
{term(TERM_CHECK_COMMIT, "gate da mensagem de commit")}
{term(sh("git log --oneline 545d58a..HEAD"), "commits da feature — um por task (git log)")}

<h3>6. O erro que virou lição</h3>
<p>Na task T5 o build quebrou (um <code>using</code> ausente), mas o gate que eu registrei veio de <code>dotnet test --no-build</code> — rodando o binário da task anterior. Passou. Era falso. O tlc chama isso de <em>victory declaration bias</em>, e a regra dele é literal: o test runner decide, não a auto-avaliação; exit code diferente de zero é STOP.</p>
{term(TERM_T5_FALSE_GREEN, "T5 · o falso verde")}
<p>A correção foi um commit de <code>fix</code>, um gotcha novo no <code>AGENTS.md</code> ("nunca julgue um gate com <code>--no-build</code>") e uma <b>lição grounded</b> registrada pelo script — com o <code>file:line</code> obrigatório, sem o qual ele recusa gravar:</p>
{term(TERM_LESSON, "lições: só com evidência")}
{snip(".specs/LESSONS.md", r"^## Candidates", None, "md", ".specs/LESSONS.md — L-001 (candidate: vira confirmed quando reincidir em outra feature)")}

<h3>7. O Verifier: autor ≠ verificador, evidência ou zero</h3>
<p>Depois da última task, um sub-agente <b>novo</b>, sem o contexto de quem implementou, refaz a cobertura do zero: para cada critério da spec, o <code>file:line</code> e a expressão de assert que prova o resultado <em>definido na spec</em>; o gate com build fresco; e o <b>sensor de discriminação</b> — três falhas injetadas num worktree descartável para confirmar que os testes matam o mutante. Tudo vai para <code>validation.md</code>, e o <code>validate_state.py</code> só aceita o veredito com PASS explícito e evidência citada.</p>
{snip(".specs/features/001-cancelamento-parcial/validation.md", r"^## Spec-Anchored", r"^## Discrimination Sensor", "md", "validation.md — critérios ancorados na spec (trecho)", include_end=False)}
{snip(".specs/features/001-cancelamento-parcial/validation.md", r"^## Discrimination Sensor", r"^## (Interactive UAT|Code Quality)", "md", "validation.md — sensor de discriminação", include_end=False)}
{snip(".specs/features/001-cancelamento-parcial/validation.md", r"^## Summary", None, "md", "validation.md — veredito")}

<h3>8. Memória: decisões que sobrevivem à feature</h3>
<p><code>STATE.md</code> guarda só decisões de projeto (as que outra feature precisa conhecer) e o handoff para retomar sem reler tudo. As duas decisões desta feature já apontam para ADRs com <code>enforced-by</code> — é a ponte AD-NNN → ADR do kit:</p>
{snip(".specs/STATE.md", r"^## Decisions", r"^## Handoff", "md", ".specs/STATE.md — Decisions", include_end=False)}

<h3>Os agentes do kit em volta do tlc</h3>
<p>O roteiro cataloga nove; o exemplo usa seis (o Verifier é o do tlc, não um agente nosso). "Só leitura" = Read/Grep/Glob; "+ Bash" = Bash sob a allowlist do <code>settings.json</code>.</p>
<div class="tbl"><table><thead><tr><th>Agente</th><th>Quando</th><th>Entrada → saída</th><th>Ferramentas</th></tr></thead><tbody>
<tr><td><code>card-intake</code> (skill)</td><td>ao pegar o card</td><td>card (Jira/ClickUp/texto) → DoR + dimensionamento + briefing; não escreve spec</td><td>MCP atlassian/clickup, leitura</td></tr>
<tr><td><code>impact-analyzer</code></td><td>passo 1 do Design</td><td>fluxo → repos, contratos, ordem, riscos, "o que não encontrei"</td><td>só leitura</td></tr>
<tr><td><code>legacy-navigator</code></td><td>antes de mudar comportamento do monolito</td><td>regra → onde vive, entradas, tabelas, efeitos colaterais, há characterization?</td><td>leitura + Bash</td></tr>
<tr><td><code>test-designer</code></td><td>tier alto ou legado (opcional; default é o do tlc)</td><td>spec → um teste por cláusula com o ID no nome; characterization no legado</td><td>leitura + Write só em <code>tests/</code></td></tr>
<tr><td><code>dotnet-reviewer</code></td><td>todo PR, antes do humano</td><td>diff → achados por severidade; "precisa de humano em…"</td><td>leitura + Bash</td></tr>
<tr><td><code>contract-reviewer</code></td><td>quando a rule de contratos ativa</td><td>diff de contrato → breaking, consumidores, ação</td><td>leitura + oasdiff</td></tr>
</tbody></table></div>
<div class="box honesto"><span class="lbl">Honestidade</span><p>O que é real: os artefatos de <code>.specs/</code>, os sete commits, os gates e o Verifier (sub-agente com contexto limpo) rodaram nesta data com a skill 3.3.0 instalada pelo plugin. O que não é: os dois gates humanos foram registrados pela aprovação do plano da v0.2 pelo fundador, não por um PO em reunião; o MCP do Jira não foi conectado (texto colado); o consumidor no ERP (R2.1) ficou fora por decisão multi-repo e não existe catálogo AsyncAPI no exemplo; o status <code>Cancelado</code> não é alcançável neste repo, então a cláusula WHILE ficou coberta por construção e registrada como assumption.</p></div>

<!-- ======================= C10 ======================= -->
<h2 id="c10"><span class="eyebrow">Capítulo 10</span><br>Qualidade que o build impõe (e três lições reais)</h2>
<p>O agente obedece ao build com muito mais consistência do que obedece a texto. Então a qualidade que importa vai para o build:</p>
{code("Directory.Build.props","xml")}
{snip(".editorconfig", r"^\[\*\.cs\]", None, "ini", ".editorconfig (trecho C#)")}
<p>Ao construir este exemplo, o próprio build ensinou três coisas — e as três viraram artefato no mesmo dia, como manda o princípio 6:</p>
{term(TERM_CA1710, "primeira tentativa de build (27-08-2026)")}
<div class="tbl"><table><thead><tr><th>O que aconteceu</th><th>Lição</th><th>Virou</th></tr></thead><tbody>
<tr><td><code>CA1710</code>: exceção sem sufixo <code>Exception</code></td><td>O analyzer barra o que a revisão humana deixaria passar. A classe foi renomeada em código, docs e specs.</td><td>o próprio build (nada a acrescentar)</td></tr>
<tr><td><code>NU1301</code>: 401 num feed CodeArtifact de <em>outro</em> cliente</td><td>O <code>NuGet.config</code> global da máquina vaza entre projetos. Repo tem o seu, com <code>&lt;clear/&gt;</code>.</td><td><code>nuget.config</code> no template do kit</td></tr>
<tr><td><code>IDE0005</code> só roda no build com doc file; API do ArchUnitNET mudou (<code>ResideInNamespaceMatching</code>)</td><td>Dependência de versão é evidência classe B: verificar, não lembrar. <code>dotnet format --diagnostics IDE0005</code> resolve o resto sozinho. E o <code>CS1591</code> que o doc file traz foi silenciado no <code>.editorconfig</code> — não com <code>NoWarn</code> no props, como a própria regra manda.</td><td><code>GenerateDocumentationFile</code> no props; <code>CS1591</code> no editorconfig; regex no teste</td></tr>
</tbody></table></div>
{code("nuget.config","xml")}
{term(TERM_BUILD, "build final")}

<!-- ======================= C11 ======================= -->
<h2 id="c11"><span class="eyebrow">Capítulo 11</span><br>Contratos entre serviços</h2>
<p>Entre serviços, o sensor mais barato é o teste de contrato. O evento <code>OrderItemCancelled</code> é público: mudar um campo é versionar. A rule de contratos ativa quando o agente toca nele:</p>
{code(".claude/rules/contracts.md","md")}
{code("src/Orders.Domain/Events/OrderItemCancelled.cs","csharp")}
<p>No pipeline, três ferramentas cobrem os três tipos de contrato: <code>oasdiff breaking</code> para HTTP (falha o PR em mudança incompatível; deprecação com prazo), AsyncAPI + catálogo de eventos para mensageria (responde "quem consome isto?"), e Pact para os pares consumidor/produtor mais críticos (<code>can-i-deploy</code> antes do deploy).</p>
<div class="box honesto"><span class="lbl">Honestidade</span><p>O exemplo não tem projeto de API nem pipeline: <code>oasdiff</code>, AsyncAPI e Pact estão descritos, não executados aqui. A rule e o agente <code>contract-reviewer</code> existem e são aplicados pelo kit; a prova de contrato rodando é a fase 4 do roteiro num repositório real.</p></div>

<!-- ======================= C12 ======================= -->
<h2 id="c12"><span class="eyebrow">Capítulo 12</span><br>As 7 fases e como a Whitebeard usa isto</h2>
<p>Tudo o que este e-book mostra é a <b>fase 1</b> (contexto mínimo), parte da <b>fase 2</b> (ADRs e <code>docs/regras/</code> — sem o mapa da empresa nem o grafo gerado), a <b>fase 3</b> (card → spec → PR, com o tlc-spec-driven como motor) e parte da <b>fase 4</b> (sensores) do roteiro. A fase 5 já tem o seu artefato central: o kit é um plugin instalável (<code>claude plugin install kit@whitebeard-kit</code>; no Cursor, o mesmo repo com <code>.cursor-plugin/</code>). As fases têm critério de saída, e nenhuma começa sem o da anterior:</p>
<div class="tbl"><table><thead><tr><th>Fase</th><th>Quando</th><th>Sai quando</th></tr></thead><tbody>
<tr><td>0 Fundação</td><td>sem. 1–2</td><td>política de IA publicada; baseline medido; repos com teste rodando e branch protegida</td></tr>
<tr><td>1 Contexto mínimo</td><td>sem. 2–3</td><td>agente builda e testa sozinho; <code>.env</code> bloqueado por hook; <code>/context</code> &lt; 10 %</td></tr>
<tr><td>2 Mapa da empresa</td><td>sem. 3–5</td><td><code>impact-analyzer</code> acerta repos e ordem em 3 cards históricos</td></tr>
<tr><td>3 Card → spec → PR</td><td>sem. 5–8</td><td>5 cards fim a fim; nenhum PR sem evidência; rework e p75 vs baseline</td></tr>
<tr><td>4 Sensores e segurança</td><td>sem. 8–12</td><td>quebra de contrato falha no CI; refactor sem characterization bloqueado; sessão auditável</td></tr>
<tr><td>5 Harness e escala</td><td>mês 3–6</td><td>2ª equipe operando via plugin (já existe); managed settings; DORA não regrediu</td></tr>
<tr><td>6 Contínua</td><td>sempre</td><td>artefato com dono, data e frescor; CLAUDE.md diminui, não cresce</td></tr>
</tbody></table></div>
<p>A Whitebeard usa o mesmo kit de três formas: nos <b>próprios repositórios</b> (toda lição vira template no kit, não num repo só); como <b>serviço de implantação</b> (fases 0→3 em cerca de oito semanas no cliente, 4→6 como advisory recorrente); e como <b>formação</b> — o time do cliente executa cada fase pelo checklist e a Whitebeard revisa. A transferência de conhecimento é o entregável; o kit é o que permite que ela seja verificável.</p>

<!-- ======================= APÊNDICE ======================= -->
<h2 id="apendice"><span class="eyebrow">Apêndice</span><br>Comandos, pendências, glossário</h2>
<h3>Comandos do dia a dia</h3>
{term('''$ claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git && claude plugin install kit@whitebeard-kit
$ ~/DEV/WHITEBEARD/agentic-engineering-kit/apply.sh /caminho/do/repo --claude --cursor --with-tlc --dotnet
$ claude                                  # no diretório do serviço; /init, depois pode o AGENTS.md
$ /kit:card-intake ORD-231                # porteiro → briefing → "specify feature ..." (tlc)
$ claude plugin update tlc@whitebeard-kit  # o tlc é sempre o original do Tech Leads Club
$ /context                                # carga do contexto (< 10 %)
$ dotnet build Orders.slnx                # ≈ 2 s; warning de análise é erro
$ dotnet test Orders.slnx                 # ≈ 9 s; 9 testes
$ dotnet test --filter "FullyQualifiedName~RN_ORD_012"
$ dotnet format Orders.slnx --diagnostics IDE0005
$ DiffEngine_Disabled=true dotnet test    # no CI''', "referência")}
<h3>O que o exemplo ainda não prova</h3>
<ul>
<li>Projeto de API e pipeline de CI (portanto <code>oasdiff</code>, Pact e Stryker não rodaram); catálogo AsyncAPI para o evento.</li>
<li>Consumidor no ERP (feature separada no repo do ERP, pela regra multi-repo) e nota no vault.</li>
<li>Gates humanos com PO/tech lead reais e o MCP do Jira/ClickUp conectado (a sessão usou o adaptador de texto).</li>
<li>Grafo de dependências gerado e mapa da empresa no vault (fase 2) — o exemplo é um repo só.</li>
<li>Sandbox com egresso controlado (fase 4) e managed settings (fase 5) — configuração de máquina e de organização, não de repositório.</li>
</ul>
<h3>Glossário</h3>
<dl class="glos">
<dt>Characterization test</dt><dd>Teste que registra o comportamento atual de um código (o que faz, não o que deveria) para detectar mudanças durante refactor.</dd>
<dt>EARS</dt><dd>Sintaxe de requisitos: <code>WHEN … THE SYSTEM SHALL …</code>, <code>IF … THEN …</code>, <code>WHILE …</code>, <code>SHALL CONTINUE TO …</code>.</dd>
<dt>Harness</dt><dd>Tudo que cerca o modelo: contexto, hooks, permissões, testes, linters, agentes — a infraestrutura que torna o agente confiável.</dd>
<dt>Hook</dt><dd>Script que o Claude Code executa antes ou depois de uma ferramenta; exit 2 bloqueia e devolve a mensagem ao agente.</dd>
<dt>Rule</dt><dd>Arquivo em <code>.claude/rules/</code> carregado só quando o agente toca caminhos que batem no <code>paths:</code>.</dd>
<dt>Skill</dt><dd>Procedimento reutilizável em <code>.claude/skills/&lt;nome&gt;/SKILL.md</code>; a <code>description</code> é a regra de roteamento.</dd>
<dt>Specification</dt><dd>Objeto do domínio que encapsula um predicado de negócio reutilizável (<code>IsSatisfiedBy</code>).</dd>
<dt>Value object</dt><dd>Tipo sem identidade, imutável, que nasce válido ou não nasce (<code>Money</code>).</dd>
<dt>Verifier (tlc)</dt><dd>Sub-agente do tlc-spec-driven, em contexto limpo, que valida a implementação contra a spec com <code>file:line</code>, gate com build fresco e sensor de discriminação; nunca é quem implementou. Escreve <code>validation.md</code>.</dd>
<dt>Sensor de discriminação</dt><dd>Injeção de falhas de comportamento num worktree descartável para confirmar que os testes falham (mutante morto); mutante que sobrevive vira fix task.</dd>
<dt>Lição (tlc)</dt><dd>Regra geral e curta gravada por <code>lessons.py</code> só a partir de um sinal do Verifier com <code>file:line</code>; <em>candidate</em> até reincidir em outra feature, então <em>confirmed</em>.</dd>
</dl>
<p class="eyebrow" style="margin-top:40px">Whitebeard · Engenharia · IA · Advisory — texto de método, sem chamada comercial. Roteiro completo com fontes: <a href="{ARTIFACT_ROTEIRO}">Roteiro de Engenharia com Agentes</a>. Método de spec: <a href="https://github.com/tech-leads-club/agent-skills">tlc-spec-driven</a> © Tech Leads Club / Felipe Rodrigues, CC-BY-4.0. Kit: <a href="https://github.com/whitebeardit/agentic-engineering-kit">whitebeardit/agentic-engineering-kit</a>.</p>
</div>
"""
open(OUT, "w", encoding="utf-8").write(page)
print(OUT, len(page.splitlines()), "linhas", round(len(page.encode())/1024), "KB")
