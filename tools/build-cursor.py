#!/usr/bin/env python3
"""Gera cursor/rules/*.mdc a partir de rules/*.md (formato Claude, frontmatter `paths:`).
Uso: tools/build-cursor.py [--check] [--selftest]
  --check     falha se a saída commitada divergir, ou se algum .mdc do repositório não abrir com `---`
  --selftest  prova a segunda regra com um mutante (carimbo antes do frontmatter) e um controle (a saída do gerador)

O carimbo "gerado por" vai DENTRO do frontmatter, como comentário YAML. Até a v0.5.2 ele ia na linha 1, antes do
`---`, e o Cursor ignorava a rule inteira, `globs` e `alwaysApply` incluídos (issue #24, testado no cursor-agent)."""
import re, subprocess, sys, pathlib, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "rules", ROOT / "cursor" / "rules"
check = "--check" in sys.argv


def gerar(src):
    text = src.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)
    globs = re.findall(r'^\s*-\s*"?([^"\n]+?)"?\s*$', fm, re.M)
    title = re.search(r"^#\s+(.+)$", body, re.M)
    desc = (title.group(1).strip() if title else src.stem)
    return ("---\n# gerado por tools/build-cursor.py a partir de rules/%s — não edite à mão\n" % src.name
            + f"description: {desc}\n" + "globs:\n" + "".join(f"  - \"{g}\"\n" for g in globs)
            + "alwaysApply: false\n---\n" + body.lstrip("\n"))


def sem_frontmatter(paths):
    """.mdc cuja primeira linha não é `---`: o Cursor não lê o frontmatter e não aplica a rule."""
    return [p for p in paths if not p.read_text(encoding="utf-8").startswith("---\n")]


if "--selftest" in sys.argv:
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d, "sentinela.md")
        src.write_text('---\npaths:\n  - "src/**/*.ts"\n---\n# Sentinela\ncorpo\n', encoding="utf-8")
        controle = pathlib.Path(d, "controle.mdc"); controle.write_text(gerar(src), encoding="utf-8")
        mutante = pathlib.Path(d, "mutante.mdc")
        mutante.write_text("<!-- carimbo -->\n" + controle.read_text(encoding="utf-8").replace("# gerado por", "# x", 1), encoding="utf-8")
        ruins = sem_frontmatter([controle, mutante])
        ok = ruins == [mutante]
        print("selftest:", "mutante reprovado, controle aprovado" if ok else f"FALHOU (reprovados: {[p.name for p in ruins]})")
        sys.exit(0 if ok else 1)

DST.mkdir(parents=True, exist_ok=True)
diff = []
for src in sorted(SRC.glob("*.md")):
    out = gerar(src)
    dst = DST / (src.stem + ".mdc")
    if check:
        if not dst.exists() or dst.read_text(encoding="utf-8") != out: diff.append(dst.name)
    else:
        dst.write_text(out, encoding="utf-8"); print("gerado", dst.relative_to(ROOT))
if check:
    listados = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.mdc"], capture_output=True, text=True, check=True).stdout.split()
    ruins = sem_frontmatter([ROOT / p for p in listados])
    print("cursor/rules divergente:" if diff else "cursor/rules em dia", *diff)
    print(f".mdc sem frontmatter na linha 1: {[str(p.relative_to(ROOT)) for p in ruins]}" if ruins else f".mdc com frontmatter na linha 1: {len(listados)} de {len(listados)}")
    sys.exit(1 if diff or ruins else 0)
