#!/usr/bin/env python3
"""Gera cursor/rules/*.mdc a partir de rules/*.md (formato Claude, frontmatter `paths:`).
Uso: tools/build-cursor.py [--check]   (--check falha se a saída commitada divergir)"""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "rules", ROOT / "cursor" / "rules"
check = "--check" in sys.argv
DST.mkdir(parents=True, exist_ok=True)
diff = []
for src in sorted(SRC.glob("*.md")):
    text = src.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)
    globs = re.findall(r'^\s*-\s*"?([^"\n]+?)"?\s*$', fm, re.M)
    title = re.search(r"^#\s+(.+)$", body, re.M)
    desc = (title.group(1).strip() if title else src.stem)
    out = "---\n" + f"description: {desc}\n" + "globs:\n" + "".join(f"  - \"{g}\"\n" for g in globs) + "alwaysApply: false\n---\n" + body.lstrip("\n")
    out = "<!-- gerado por tools/build-cursor.py a partir de rules/%s — não edite à mão -->\n" % src.name + out
    dst = DST / (src.stem + ".mdc")
    if check:
        if not dst.exists() or dst.read_text(encoding="utf-8") != out: diff.append(dst.name)
    else:
        dst.write_text(out, encoding="utf-8"); print("gerado", dst.relative_to(ROOT))
if check:
    print("cursor/rules divergente:" if diff else "cursor/rules em dia", *diff); sys.exit(1 if diff else 0)
