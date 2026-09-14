#!/usr/bin/env python3
"""Agentes e template raiz não prometem o que o agente não alcança (#13) e dizem as duas ordens entre serviços (#14).

1. Agente com lista `tools:` sem ferramenta `mcp__` não cita MCP nem o vault como fonte que ele consulta; o template raiz
   não manda consultar via MCP. Até a v0.5.6 o impact-analyzer tinha "mapa transversal no vault (via MCP, se disponível)"
   com `tools: Read, Grep, Glob` — a fonte nunca era consultada e o agente seguia em silêncio.
2. O impact-analyzer diz como enxergar os repositórios irmãos (`--add-dir`) e manda o mapa que não veio para
   "O que não encontrei".
3. Ordem entre serviços: o template raiz e o impact-analyzer trazem a de acrescentar, a inversa ("consumidores primeiro")
   e a regra "sobe primeiro quem pode mudar sem quebrar quem ainda não mudou". Até a v0.5.6 o template só tinha a de
   acrescentar, como se fosse a única.

Não testa o comportamento do modelo — só o que os arquivos declaram e prometem.
Uso: python3 tools/check-agentes.py [--selftest]
"""
import pathlib, re, sys

KIT = pathlib.Path(__file__).resolve().parent.parent
RAIZ = "templates/AGENTS.root.md"
IMPACTO = "agents/impact-analyzer.md"
PROMESSA_AGENTE = re.compile(r"via MCP|por MCP|mapa do vault|\bno vault\b")
PROMESSA_RAIZ = re.compile(r"via MCP")
REGRA_ORDEM = "sobe primeiro quem pode mudar sem quebrar quem ainda não mudou"


def espacos(t):
    return re.sub(r"\s+", " ", t)


def tools_de(texto):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None
    t = re.search(r"^tools:\s*(.+)$", m.group(1), re.M)
    return [x.strip() for x in t.group(1).split(",")] if t else None


def confere(textos):
    erros = []
    for nome, texto in sorted(textos.items()):
        if not nome.startswith("agents/"):
            continue
        tools = tools_de(texto)
        corpo = re.sub(r"^---\n.*?\n---\n", "", texto, count=1, flags=re.S)
        if tools is not None and not any(t.startswith("mcp__") for t in tools):
            for m in PROMESSA_AGENTE.finditer(espacos(corpo)):
                erros.append(f"{nome}: promete fonte fora do alcance (`tools: {', '.join(tools)}` sem mcp__): “{m.group(0)}”")
    raiz = espacos(textos[RAIZ])
    if PROMESSA_RAIZ.search(raiz):
        erros.append(f"{RAIZ}: manda consultar via MCP, mas nenhum agente do kit tem ferramenta de MCP")
    imp = espacos(textos[IMPACTO])
    if "--add-dir" not in imp:
        erros.append(f"{IMPACTO}: não diz como enxergar os repositórios irmãos (`--add-dir`)")
    if not re.search(r"mapa transversal que não veio.*?O que não encontrei", imp):
        erros.append(f"{IMPACTO}: não manda o mapa transversal que não veio para “O que não encontrei”")
    for nome, t in ((RAIZ, raiz), (IMPACTO, imp)):
        if "consumidores primeiro" not in t:
            erros.append(f"{nome}: sem a ordem inversa (consumidores primeiro)")
        if REGRA_ORDEM not in t:
            erros.append(f"{nome}: sem a regra “{REGRA_ORDEM}”")
    if "Para acrescentar" not in raiz:
        erros.append(f"{RAIZ}: a ordem de acrescentar não diz que é a de acrescentar")
    return erros


def carrega(base=KIT):
    textos = {str(p.relative_to(base)): p.read_text(encoding="utf-8") for p in sorted((base / "agents").glob("*.md"))}
    textos[RAIZ] = (base / RAIZ).read_text(encoding="utf-8")
    return textos


def selftest():
    base = carrega()
    assert not confere(base), f"controle reprovado: {confere(base)}"

    def mutante(nome, arquivo, de, para, todas=False):
        t = dict(base)
        assert de in t[arquivo], f"mutante {nome}: trecho {de[:40]!r} não está em {arquivo}"
        t[arquivo] = t[arquivo].replace(de, para, -1 if todas else 1)
        assert confere(t), f"mutante {nome} passou"

    mutante("fonte via MCP no agente (v0.5.6)", IMPACTO, "mapa transversal, **se vier no pedido**",
            "mapa transversal no vault (via MCP, se disponível)")
    mutante("template manda consultar via MCP (v0.5.6)", RAIZ, "(não copiar para cá;", "(consultar via MCP; não copiar para cá;")
    mutante("sem --add-dir (em nenhum lugar do agente)", IMPACTO, "--add-dir", "", todas=True)
    mutante("mapa ausente em silêncio", IMPACTO, "e mapa transversal que não veio,", ",")
    mutante("template só com a ordem de acrescentar (v0.5.6)", RAIZ, "inverte — consumidores primeiro", "inverte")
    mutante("contract-reviewer com o mapa do vault (v0.5.6)", "agents/contract-reviewer.md",
            "mapa transversal, se vier no pedido (você não lê o vault)", "mapa do vault")
    print("check-agentes: selftest — controle aprovado; seis mutantes reprovados")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    erros = confere(carrega())
    for e in erros:
        print("check-agentes:", e, file=sys.stderr)
    print(f"check-agentes: {len(erros)} erro(s)")
    sys.exit(1 if erros else 0)
