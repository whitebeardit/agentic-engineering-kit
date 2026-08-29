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

def term(text, title="terminal"):
    return f'<figure class="code term"><figcaption><span class="path">{html.escape(title)}</span></figcaption><pre><code>{html.escape(text.strip())}</code></pre></figure>'

def arquivo(path, quem, quando, casa="REPO"):
    return f'<div class="arquivo"><div class="arq-path"><span class="tag {casa.lower()}">{casa}</span><code>{html.escape(path)}</code></div><div class="arq-meta"><b>Quem lê:</b> {quem} · <b>Quando:</b> {quando}</div></div>'

TREE = """orders-sample/
├── CLAUDE.md                          ← contexto do repo: comandos, custos, gotchas, Never
├── nuget.config                       ← feed por repo (não herda o global da máquina)
├── Directory.Build.props              ← analyzers para todos os projetos (rampa no legado)
├── .editorconfig                      ← severidade das regras vive aqui, nunca NoWarn no csproj
├── Orders.slnx
├── .claude/
│   ├── settings.json                  ← allowlist, deny e hooks
│   ├── hooks/                         ← protect-paths · guard-bash · dotnet-format
│   ├── rules/                         ← contracts.md · legacy.md (ativam por caminho)
│   ├── agents/                        ← impact-analyzer · legacy-navigator · test-designer · verifier · dotnet-reviewer · contract-reviewer
│   └── skills/                        ← jira-intake · regras-de-negocio · run-and-test
├── docs/
│   ├── regras/pedidos.md              ← AS regras (RN-ORD-*), com código e teste de cada uma
│   ├── adr/                           ← 0003 domínio puro · 0004 regra no domínio
│   ├── definition-of-ready.md         ← o card só entra se…
│   └── evidencia/                     ← output de teste colado, com data
├── specs/001-cancelamento-parcial/    ← requirements (EARS) · design · tasks (com Verify)
├── src/
│   ├── Orders.Domain/                 ← Order, OrderItem, Money, Specifications, Events, IOrderRepository
│   ├── Orders.Application/            ← CancelOrderItemHandler (orquestra; não decide)
│   ├── Orders.Infrastructure/         ← InMemoryOrderRepository (adapter)
│   └── Erp.Legacy/                    ← CalculadoraFrete (2014; ninguém explica)
└── tests/Orders.Tests/
    ├── RN_ORD_012_CancelamentoParcialTests.cs   ← um teste por cláusula EARS
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
  <div class="eyebrow">E-book Whitebeard · nº 3 · 27 ago 2026 · rev. 28 ago</div>
  <h1 style="margin-top:10px">Engenharia com Agentes em .NET</h1>
  <p class="lede">Onde fica cada arquivo, o que ele faz e como se usa — num serviço .NET de verdade, com monolito legado ao lado, compilado e testado antes de entrar neste texto.</p>
  <div class="meta"><span>kit: <code>~/DEV/WHITEBEARD/agentic-engineering-kit</code></span><span>exemplo: <code>samples/orders-sample</code></span><span>.NET SDK 10.0.103</span><span>9/9 testes verdes</span></div>
</header>

<nav class="toc"><div class="eyebrow">Capítulos</div><ol>
<li><a href="#c1">Por que um kit, e não um prompt</a></li>
<li><a href="#c2">As quatro casas: onde cada coisa fica</a></li>
<li><a href="#c3">A árvore do exemplo, arquivo por arquivo</a></li>
<li><a href="#c4">CLAUDE.md: o que o agente não adivinha</a></li>
<li><a href="#c5">Hooks, permissões e rules: o que é garantia</a></li>
<li><a href="#c6">Regra de negócio mora no domínio</a></li>
<li><a href="#c7">ADR que falha o build</a></li>
<li><a href="#c8">Legado: congelar antes de mexer</a></li>
<li><a href="#c9">Do card ao PR: specs, skills e agentes</a></li>
<li><a href="#c10">Qualidade que o build impõe (e três lições reais)</a></li>
<li><a href="#c11">Contratos entre serviços</a></li>
<li><a href="#c12">As 7 fases e como a Whitebeard usa isto</a></li>
<li><a href="#apendice">Apêndice: comandos, pendências, glossário</a></li>
</ol></nav>

<p><b>Como ler.</b> Cada capítulo mostra arquivos reais do exemplo <code>orders-sample</code> — o texto é gerado a partir deles, então o que você lê é o que compila. Caixas <em>Para quem é técnico</em> aprofundam; caixas <em>Honestidade</em> dizem o que ainda não está provado. Não há chamada comercial: é um texto de método.</p>

<!-- ======================= C1 ======================= -->
<h2 id="c1"><span class="eyebrow">Capítulo 1</span><br>Por que um kit, e não um prompt</h2>
<p>Uma empresa .NET típica tem um monolito de dez anos, uma dúzia de microserviços mais novos, cards no Jira e um time que já usa IA para escrever código. O que ela não tem é um lugar onde a IA <em>aprende como a empresa funciona</em> — e por isso cada sessão começa do zero, cada engenheiro cola o mesmo contexto, e a qualidade do resultado depende de quem digitou o prompt.</p>
<p>A pesquisa que fundamenta este e-book (DORA 2024/2025, Anthropic, Thoughtworks, OpenAI, GitClear, METR — reunida no <a href="{ARTIFACT_ROTEIRO}">Roteiro de Engenharia com Agentes</a>) converge em sete princípios. O kit existe para <em>impor</em> os sete, não para descrevê-los:</p>
<div class="tbl"><table><thead><tr><th>Princípio</th><th>No kit vira…</th></tr></thead><tbody>
<tr><td>IA é amplificador: fundação antes do agente</td><td>fase 0 (baseline, branch protection, testes rodando) antes de qualquer <code>.claude/</code></td></tr>
<tr><td>Contexto mínimo e concreto</td><td><code>CLAUDE.md</code> com comandos, custos e gotchas; nunca prosa de arquitetura</td></tr>
<tr><td>Enforcement mecânico &gt; texto</td><td>hooks que bloqueiam, analyzers que falham o build, testes de arquitetura</td></tr>
<tr><td>Spec antes do código, gate humano no meio</td><td><code>specs/NNN/</code> em 3 arquivos; <code>jira-intake</code> para no gate 1</td></tr>
<tr><td>Autor ≠ verificador</td><td>agente <code>verifier</code> em contexto limpo; <code>dotnet-reviewer</code> antes do humano</td></tr>
<tr><td>Cada erro vira artefato</td><td>lição → linha no CLAUDE.md, teste, rule ou hook — nunca "tome mais cuidado"</td></tr>
<tr><td>Segurança na borda</td><td>deny de segredos, sandbox, conteúdo externo como input não confiável</td></tr>
</tbody></table></div>
<div class="box analogia"><span class="lbl">Analogia</span><p>Contratar um engenheiro sênior excelente e colocá-lo num prédio sem placas, sem crachá e sem manual de emergência. Ele vai trabalhar — e vai errar coisas que qualquer estagiário do prédio sabe. O kit são as placas, o crachá e o manual. O agente é o sênior.</p></div>

<!-- ======================= C2 ======================= -->
<h2 id="c2"><span class="eyebrow">Capítulo 2</span><br>As quatro casas: onde cada coisa fica</h2>
<p>A pergunta "onde eu coloco isso?" tem quatro respostas possíveis, e misturá-las é a causa número um de artefato que apodrece.</p>
<div class="tbl"><table><thead><tr><th>Casa</th><th>O que vive lá</th><th>Por quê</th></tr></thead><tbody>
<tr><td><span class="tag repo">REPO</span></td><td>CLAUDE.md, <code>.claude/</code>, specs, ADRs, <code>docs/regras/</code> do domínio que o serviço é dono, testes</td><td>muda junto com o código; revisado em PR; quem não usa IA também lê</td></tr>
<tr><td><span class="tag vault">VAULT</span></td><td>mapa da empresa (quem fala com quem, tabelas compartilhadas, ordem de release), regras transversais, glossário, nota por card</td><td>nenhum repo é dono do que atravessa quatro repos</td></tr>
<tr><td><span class="tag gen">GERADO</span></td><td>grafo de dependências, inventário de endpoints/eventos, relatórios de analyzers e mutation</td><td>derivável do código: gera em CI, nunca escreve à mão, nunca entra no CLAUDE.md</td></tr>
<tr><td><span class="tag org">ORG</span></td><td>política de uso de IA, deny de segredos, sandbox, allowlist de MCP</td><td>enforcement que o desenvolvedor não remove (managed settings)</td></tr>
</tbody></table></div>
<p>E a regra de decisão para artefatos novos, na ordem em que a Anthropic a formula, com as duas casas extras da empresa:</p>
<ul>
<li>Fato curto que vale sempre → <code>CLAUDE.md</code></li>
<li>Restrição que só vale em certos caminhos → <code>.claude/rules/*.md</code> com <code>paths:</code></li>
<li>Procedimento que você colou pela terceira vez → skill</li>
<li>Deve acontecer sempre, sem exceção → hook</li>
<li>Tarefa que inunda o contexto → subagente</li>
<li>Serviço ou dado externo → MCP · Mesmo setup em segundo repo → plugin interno</li>
<li>Conhecimento que cruza serviços → vault (consultado por MCP) · Derivável do código → gerado em CI</li>
</ul>

<!-- ======================= C3 ======================= -->
<h2 id="c3"><span class="eyebrow">Capítulo 3</span><br>A árvore do exemplo, arquivo por arquivo</h2>
<p>O exemplo é um serviço de Pedidos com domínio, aplicação, infraestrutura, um pedaço de monolito legado e os testes que provam tudo isso. Foi criado com <code>apply.sh --dotnet</code> do kit e depois preenchido. Esta é a árvore como está no disco:</p>
{term(TREE, "samples/orders-sample")}
<p>Cada arquivo abaixo tem duas perguntas respondidas: <b>quem lê</b> e <b>quando</b>. Se você não consegue responder as duas para um arquivo do seu repositório, ele provavelmente não deveria existir.</p>
{arquivo("CLAUDE.md","o agente, em toda sessão (carrega sozinho); humanos no onboarding","sempre que o Claude abre no repo")}
{arquivo(".claude/settings.json","o harness do Claude Code — não o modelo","antes de cada tool call (hooks) e em cada permissão")}
{arquivo(".claude/rules/legacy.md","o agente, só ao tocar arquivos que batem no glob","ao editar src/Erp.Legacy/**")}
{arquivo(".claude/agents/verifier.md","um subagente com contexto limpo","ao final de cada task e antes do PR")}
{arquivo(".claude/skills/regras-de-negocio/SKILL.md","o agente, ao tocar docs/regras/ ou o Domain, ou quando invocada","antes de implementar critério que muda comportamento")}
{arquivo("docs/regras/pedidos.md","jira-intake, verifier, PO e engenheiro — todos a mesma versão","antes de escrever spec; ao mudar comportamento")}
{arquivo("docs/adr/0004-regra-no-dominio.md","quem vê 'viola ADR-0004' no build","quando o teste de arquitetura falha")}
{arquivo("specs/001-cancelamento-parcial/tasks.md","o agente executor (uma task por sessão) e o verifier","durante a implementação")}
{arquivo("tests/Orders.Tests/Legacy/….verified.txt","um humano, na primeira execução e a cada mudança","antes de qualquer refactor no legado")}
{arquivo("docs/evidencia/2026-08-27-dotnet-test.txt","o revisor do PR","ao abrir o PR: sem output, não está pronto")}

<!-- ======================= C4 ======================= -->
<h2 id="c4"><span class="eyebrow">Capítulo 4</span><br>CLAUDE.md: o que o agente não adivinha</h2>
<p>Um estudo de ablação com 288 execuções (jul/2026) mediu que instruções genéricas de arquitetura e estilo no arquivo de contexto <em>não melhoram a correção</em> — enquanto avisos concretos como "a suíte completa leva 20 minutos" cortaram reexecuções em 45 %. A Anthropic recomenda menos de 200 linhas; a meta do roteiro Whitebeard é ainda mais curta, ≤ 150 por repositório. A pergunta-poda: <em>remover esta linha faria o agente errar?</em></p>
<p>É por isso que o <code>CLAUDE.md</code> do exemplo tem comandos com <b>tempo medido</b>, definição de pronto como exit code e gotchas — e nada sobre "arquitetura limpa":</p>
{code("CLAUDE.md","md",title="orders-sample/CLAUDE.md")}
<p>No workspace pai (o diretório que contém todos os repos) vive um segundo <code>CLAUDE.md</code>, com a tabela de serviços, a ordem padrão entre eles e a etiqueta de PR. O Claude é iniciado no subdiretório do serviço; o raiz carrega junto.</p>
{code("templates/CLAUDE.root.md","md",title="kit/templates/CLAUDE.root.md (workspace pai)")}
<h3>Como usar</h3>
<ol class="steps">
<li><code>apply.sh /repo --dotnet</code> cria o esqueleto; <code>/init</code> dentro do Claude rascunha o resto.</li>
<li>Pode linha a linha. Comando com custo fica; "escreva código limpo" sai.</li>
<li><code>/context</code> mostra a carga: abaixo de 10 % do contexto está bom.</li>
<li>Toda vez que o agente errar por não saber algo do repo, uma linha entra aqui — e só assim ele cresce.</li>
</ol>
<div class="box tech"><span class="lbl">Para quem é técnico</span><p>Hierarquia de carga: <code>~/.claude/CLAUDE.md</code> (pessoal) → raiz do workspace → repo → <code>CLAUDE.local.md</code> (gitignore). Subdiretórios carregam sob demanda quando o agente lê arquivos neles. <code>@path</code> importa outro arquivo <em>no launch</em> (não economiza tokens, só organiza). Comentários HTML são removidos antes de injetar — servem para notas humanas sem custo.</p></div>

<!-- ======================= C5 ======================= -->
<h2 id="c5"><span class="eyebrow">Capítulo 5</span><br>Hooks, permissões e rules: o que é garantia</h2>
<p>"Nunca edite o <code>.env</code>" no CLAUDE.md é um pedido. Um hook <code>PreToolUse</code> que retorna exit 2 é uma garantia: dispara antes de qualquer checagem de permissão, em todo modo — inclusive <code>bypassPermissions</code>. A diferença é a mesma entre uma placa e uma catraca. Uma ressalva honesta: um hook de repositório pode ser desligado por quem edita o <code>settings.json</code> (<code>disableAllHooks</code>); a garantia que sobrevive a isso é o hook <em>gerenciado</em> pela organização (<code>allowManagedHooksOnly</code>), que é assunto da fase 5.</p>
{code(".claude/settings.json","json",title="orders-sample/.claude/settings.json")}
<p>Os três hooks são scripts curtos, escritos para <em>explicar ao agente</em> por que foi bloqueado e o que fazer — não só para negar:</p>
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
{snip("tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs", r"^/// <summary>Prova", r"SHALL_CONTINUE_TO_ser_idempotente", "csharp", "tests/Orders.Tests/RN_ORD_012_CancelamentoParcialTests.cs (trecho: 3 de 5 testes)", include_end=False)}
<p>O nome do teste repete a cláusula da regra. Quem lê <code>docs/regras</code>, o teste ou a exceção com <code>RuleId</code> chega ao mesmo lugar — e o <code>verifier</code> cruza os três.</p>
<p>Isto <em>não</em> é TDD forçado no loop do agente — prática que a Thoughtworks mediu sem ganho de qualidade e com 3–8× de custo em tokens, e que o roteiro desaconselha. É outra coisa: um teste por cláusula EARS, escrito <b>uma vez</b> a partir da spec pelo <code>test-designer</code> (ou numa sessão separada), que fica vermelho até a regra existir e depois vira sensor permanente. Quem implementa não edita esses testes; faz passar.</p>
<h3>5. A skill: o procedimento, não o conhecimento</h3>
<p>A skill <code>regras-de-negocio</code> vive no repo dono do domínio, ativa por <code>paths:</code> e <em>aponta</em> para <code>docs/regras/</code> — se ela embutisse as regras, as duas cópias divergiriam em duas semanas.</p>
{code(".claude/skills/regras-de-negocio/SKILL.md","md",title=".claude/skills/regras-de-negocio/SKILL.md")}
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
<h2 id="c9"><span class="eyebrow">Capítulo 9</span><br>Do card ao PR: specs, skills e agentes</h2>
<p>O fluxo tem dois gates humanos — o PO aprova os requisitos (gate 1) e o tech lead aprova o design (gate 2) — mais o UAT com o PO antes de fechar o card. Cada etapa tem um arquivo ou um agente responsável. Nunca um prompt solto.</p>
<pre class="mermaid">
flowchart LR
  J[Card Jira] -->|skill jira-intake| R[requirements.md]
  R -->|gate 1: PO| I[agente impact-analyzer]
  I --> D[design.md]
  D -->|gate 2: tech lead| T[tasks.md]
  T -->|1 task = 1 repo = 1 PR| E[execute]
  E -->|agente verifier ≠ autor| V{{PASS?}}
  V -->|sim| PR[PR draft + evidência]
  V -->|não| E
  PR -->|dotnet-reviewer, depois humano por tier| M[merge]
  M -->|UAT com o PO| W[nota no vault]
</pre>
<h3>A spec em três arquivos</h3>
{code("specs/001-cancelamento-parcial/requirements.md","md")}
{code("specs/001-cancelamento-parcial/tasks.md","md")}
<p>O <code>design.md</code> (não reproduzido inteiro) traz a tabela de impacto, o contrato do evento <code>OrderItemCancelled</code>, a sequência e — o mais importante — a tabela <b>critério → teste nomeado</b>, que é o que o verifier usa.</p>
<h3>A skill que recusa card ruim</h3>
<p>O Definition of Ready canônico vive no vault e no template do card no Jira — é regra da empresa, não de um repositório. <code>docs/definition-of-ready.md</code> é a cópia que o agente lê no repo; o kit a instala para que <code>jira-intake</code> nunca dependa de rede para recusar um card.</p>
{code(".claude/skills/jira-intake/SKILL.md","md")}
<h3>Os agentes: uma responsabilidade cada</h3>
<p>O roteiro cataloga nove agentes; o exemplo traz seis. <code>security-reviewer</code> (fase 4), <code>evaluator</code> e <code>docs-gc</code> (fase 5) ficam fora do escopo deste repo. Ferramentas: "só leitura" significa Read/Grep/Glob; "+ Bash" significa Bash sob a allowlist do <code>settings.json</code> (build, test, git de leitura).</p>
<div class="tbl"><table><thead><tr><th>Agente</th><th>Quando</th><th>Entrada → saída</th><th>Ferramentas</th></tr></thead><tbody>
<tr><td><code>impact-analyzer</code></td><td>antes do design de card que cruza serviços</td><td>fluxo → repos, contratos, ordem, riscos, "o que não encontrei"</td><td>só leitura</td></tr>
<tr><td><code>legacy-navigator</code></td><td>antes de mudar comportamento do monolito</td><td>regra → onde vive, entradas, tabelas, efeitos colaterais, há characterization?</td><td>leitura + Bash</td></tr>
<tr><td><code>test-designer</code></td><td>task de testes, antes da implementação</td><td>requirements.md → um teste por cláusula EARS com o ID no nome; characterization no legado; contagem de falhas esperadas</td><td>leitura + Write só em <code>tests/</code></td></tr>
<tr><td><code>verifier</code></td><td>fim de cada task e antes do PR</td><td>spec + diff → PASS/FAIL por critério, com output colado</td><td>leitura + test/build</td></tr>
<tr><td><code>dotnet-reviewer</code></td><td>todo PR, antes do humano</td><td>diff → achados por severidade; "precisa de humano em…"</td><td>leitura + Bash</td></tr>
<tr><td><code>contract-reviewer</code></td><td>quando a rule de contratos ativa</td><td>diff de contrato → breaking, consumidores, ação</td><td>leitura + oasdiff</td></tr>
</tbody></table></div>
{code(".claude/agents/verifier.md","md",title=".claude/agents/verifier.md")}
<h3>Uma sessão típica</h3>
<ol class="steps">
<li><code>claude</code> no diretório do serviço → <code>/jira-intake ORD-231</code> → <code>requirements.md</code> com duas perguntas ao PO. Sessão encerra.</li>
<li>PO responde; <code>impact-analyzer</code> roda (subagente); tech lead aprova o <code>design.md</code>.</li>
<li>Sessão nova: <code>test-designer</code> escreve a regra em <code>docs/regras</code> e os testes da T2 (um por cláusula; ficam vermelhos). Commit. Sessão nova, plan mode: T3 (implementação) faz passar sem editar os testes. Commit.</li>
<li><code>verifier</code> em subagente: cola o output real. PR draft com intenção, prova, risco, áreas geradas por IA rotuladas.</li>
<li><code>dotnet-reviewer</code> no CI; humano revisa spec e testes (tier médio). Merge. Nota no vault.</li>
</ol>
<div class="box honesto"><span class="lbl">Honestidade</span><p>T1 está parcial: o record do evento existe e é aditivo, mas não há catálogo AsyncAPI no exemplo para publicar o schema. T4 (o consumidor no ERP) e T5 (nota no vault) estão em aberto. O fluxo foi exercitado até T3 — o que basta para mostrar os arquivos, não para afirmar que o ciclo inteiro rodou num cliente. Onde rodou, está registrado nas notas de projeto do vault, não aqui.</p></div>

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
<p>Tudo o que este e-book mostra é a <b>fase 1</b> (contexto mínimo), parte da <b>fase 2</b> (ADRs e <code>docs/regras/</code> — sem o mapa da empresa nem o grafo gerado), a <b>fase 3</b> (card → spec → PR) e parte da <b>fase 4</b> (sensores) do roteiro. As fases têm critério de saída, e nenhuma começa sem o da anterior:</p>
<div class="tbl"><table><thead><tr><th>Fase</th><th>Quando</th><th>Sai quando</th></tr></thead><tbody>
<tr><td>0 Fundação</td><td>sem. 1–2</td><td>política de IA publicada; baseline medido; repos com teste rodando e branch protegida</td></tr>
<tr><td>1 Contexto mínimo</td><td>sem. 2–3</td><td>agente builda e testa sozinho; <code>.env</code> bloqueado por hook; <code>/context</code> &lt; 10 %</td></tr>
<tr><td>2 Mapa da empresa</td><td>sem. 3–5</td><td><code>impact-analyzer</code> acerta repos e ordem em 3 cards históricos</td></tr>
<tr><td>3 Card → spec → PR</td><td>sem. 5–8</td><td>5 cards fim a fim; nenhum PR sem evidência; rework e p75 vs baseline</td></tr>
<tr><td>4 Sensores e segurança</td><td>sem. 8–12</td><td>quebra de contrato falha no CI; refactor sem characterization bloqueado; sessão auditável</td></tr>
<tr><td>5 Harness e escala</td><td>mês 3–6</td><td>2ª equipe operando via plugin; DORA não regrediu</td></tr>
<tr><td>6 Contínua</td><td>sempre</td><td>artefato com dono, data e frescor; CLAUDE.md diminui, não cresce</td></tr>
</tbody></table></div>
<p>A Whitebeard usa o mesmo kit de três formas: nos <b>próprios repositórios</b> (toda lição vira template no kit, não num repo só); como <b>serviço de implantação</b> (fases 0→3 em cerca de oito semanas no cliente, 4→6 como advisory recorrente); e como <b>formação</b> — o time do cliente executa cada fase pelo checklist e a Whitebeard revisa. A transferência de conhecimento é o entregável; o kit é o que permite que ela seja verificável.</p>

<!-- ======================= APÊNDICE ======================= -->
<h2 id="apendice"><span class="eyebrow">Apêndice</span><br>Comandos, pendências, glossário</h2>
<h3>Comandos do dia a dia</h3>
{term('''$ ~/DEV/WHITEBEARD/agentic-engineering-kit/apply.sh /caminho/do/repo --dotnet   # esqueleto sem sobrescrever
$ claude                                  # no diretório do serviço; /init, depois pode o CLAUDE.md
$ /context                                # carga do contexto (< 10 %)
$ dotnet build Orders.slnx                # ≈ 2 s; warning de análise é erro
$ dotnet test Orders.slnx                 # ≈ 9 s; 9 testes
$ dotnet test --filter "FullyQualifiedName~RN_ORD_012"
$ dotnet format Orders.slnx --diagnostics IDE0005
$ DiffEngine_Disabled=true dotnet test    # no CI''', "referência")}
<h3>O que o exemplo ainda não prova</h3>
<ul>
<li>Projeto de API e pipeline de CI (portanto <code>oasdiff</code>, Pact e Stryker não rodaram).</li>
<li>Consumidor no ERP (T4) e nota no vault (T5) da spec 001.</li>
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
<dt>Verifier</dt><dd>Agente em contexto limpo que valida a implementação contra a spec com comandos executados; nunca é quem implementou.</dd>
</dl>
<p class="eyebrow" style="margin-top:40px">Whitebeard · Engenharia · IA · Advisory — texto de método, sem chamada comercial. Roteiro completo com fontes: <a href="{ARTIFACT_ROTEIRO}">Roteiro de Engenharia com Agentes</a>.</p>
</div>
"""
open(OUT, "w", encoding="utf-8").write(page)
print(OUT, len(page.splitlines()), "linhas", round(len(page.encode())/1024), "KB")
