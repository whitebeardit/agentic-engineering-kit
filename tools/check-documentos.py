#!/usr/bin/env python3
"""Gate: nenhum artefato de exibição do kit usa documento (CPF/CNPJ) que passe na validação.

Um número com forma de documento e dígitos verificadores corretos pode pertencer a alguém — chamá-lo de sintético
não prova o contrário, e este repositório é público (ERRATA.md, 09/09/2026). Onde a validade é necessária para
exercitar uma regra (o teste da RN-ENR-001), o valor mora em `src/__tests__/helpers/` e não sai de lá; todo o
resto — docs, README, fixtures, e-book, testes que só precisam de um documento qualquer — usa um que reprova.
Uso: python3 tools/check-documentos.py   (exit 1 com a lista arquivo:linha: número)"""
import re, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
PERMITIDOS = ("/__tests__/helpers/",)
IGNORAR = ("package-lock.json", "node_modules/", ".git/")

def cpf_valido(c):
    if c == c[0] * 11: return False
    for n in (9, 10):
        d = (sum(int(c[i]) * ((n + 1) - i) for i in range(n)) * 10) % 11 % 10
        if d != int(c[n]): return False
    return True

def cnpj_valido(c):
    if c == c[0] * 14: return False
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for pesos, pos in ((p1, 12), ([6] + p1, 13)):
        r = sum(int(c[i]) * pesos[i] for i in range(pos)) % 11
        if (0 if r < 2 else 11 - r) != int(c[pos]): return False
    return True

PADRAO = re.compile(r"(?<![0-9A-Za-z.])(\d{11}|\d{14})(?![0-9A-Za-z])")
arquivos = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
hits = []
for f in arquivos:
    if any(x in f for x in IGNORAR) or any(x in "/" + f for x in PERMITIDOS): continue
    try: texto = (ROOT / f).read_text(encoding="utf-8", errors="ignore")
    except OSError: continue
    for i, linha in enumerate(texto.split("\n"), start=1):
        for m in PADRAO.finditer(linha):
            v = m.group(1)
            if (len(v) == 11 and cpf_valido(v)) or (len(v) == 14 and cnpj_valido(v)):
                hits.append(f"{f}:{i}: {v}")
for h in hits: print(h)
print(f"check-documentos: {len(hits)} documento(s) válido(s) fora de __tests__/helpers/ em {len(arquivos)} arquivo(s)")
sys.exit(1 if hits else 0)
