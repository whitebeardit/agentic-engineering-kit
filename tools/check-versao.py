#!/usr/bin/env python3
"""Gate de release: a versão dos manifestos do plugin (Claude e Cursor) é a da primeira entrada do CHANGELOG — e, quando o
CI roda numa tag `kit--vX.Y.Z`, é a da tag.

As tags kit--v0.5.4 e kit--v0.5.5 saíram com `"version": "0.5.3"` nos dois manifestos: o README manda subir a versão a
cada release, e nada conferia. `claude plugin details` mostrava 0.5.3 para quem instalava a 0.5.5 (achado na revisão do
bump do livro *Cercando a IA*, 14/09/2026).

Uso: python3 tools/check-versao.py [--tag kit--vX.Y.Z] [--selftest]
"""
import json, os, pathlib, re, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent


def erros(raiz, tag=None):
    raiz = pathlib.Path(raiz); out = []
    m = re.search(r"^## kit--v(\d+\.\d+\.\d+)\b", (raiz / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    if not m:
        return ["CHANGELOG.md sem entrada '## kit--vX.Y.Z'"]
    changelog = m.group(1)
    for man in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        v = json.loads((raiz / man).read_text(encoding="utf-8")).get("version")
        if v != changelog:
            out.append(f"{man}: version {v!r} ≠ primeira entrada do CHANGELOG ({changelog})")
    if tag:
        t = re.fullmatch(r"(?:refs/tags/)?kit--v(\d+\.\d+\.\d+)", tag)
        if t and t.group(1) != changelog:
            out.append(f"tag {tag} ≠ primeira entrada do CHANGELOG ({changelog})")
    return out


if "--selftest" in sys.argv:
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        for man in (".claude-plugin", ".cursor-plugin"):
            (d / man).mkdir(); (d / man / "plugin.json").write_text('{"name":"kit","version":"1.2.3"}', encoding="utf-8")
        (d / "CHANGELOG.md").write_text("# Changelog\n\n## kit--v1.2.3 — 2026-01-01\n", encoding="utf-8")
        controle = erros(d, "refs/tags/kit--v1.2.3")
        (d / ".cursor-plugin/plugin.json").write_text('{"name":"kit","version":"1.2.2"}', encoding="utf-8")
        mutante_manifesto = erros(d)
        (d / ".cursor-plugin/plugin.json").write_text('{"name":"kit","version":"1.2.3"}', encoding="utf-8")
        mutante_tag = erros(d, "refs/tags/kit--v1.2.4")
        ok = controle == [] and len(mutante_manifesto) == 1 and len(mutante_tag) == 1
        print("selftest:", "controle aprovado; manifesto atrasado e tag divergente reprovados" if ok else f"FALHOU {controle} {mutante_manifesto} {mutante_tag}")
        sys.exit(0 if ok else 1)

tag = None
if "--tag" in sys.argv:
    tag = sys.argv[sys.argv.index("--tag") + 1]
elif os.environ.get("GITHUB_REF", "").startswith("refs/tags/"):
    tag = os.environ["GITHUB_REF"]
e = erros(ROOT, tag)
for x in e: print(f"check-versao: ERRO — {x}")
print(f"check-versao: {len(e)} erro(s)" + (f" · tag {tag}" if tag else ""))
sys.exit(1 if e else 0)
