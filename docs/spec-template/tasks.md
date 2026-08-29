# <NNN> — <nome> · tasks

Uma task = um repo = um PR. Sessão nova por task; plan mode; commit atômico; PR draft com intenção + prova + risco.

- [ ] T1 `<repo-contrato>` — publicar contrato vN (compatível) · Verify: `oasdiff breaking old.yaml new.yaml` → sem ERR
- [ ] T2 `<repo-produtor>` — … · Verify: `dotnet test --filter Category=Contract` → verde
- [ ] T3 [P] `<repo-consumidor>` — … · Verify: `dotnet test --filter FullyQualifiedName~Cancel` → verde
- [ ] T4 `<legado>` — atrás de flag `…` · Verify: characterization `.verified.txt` inalterado + novo cenário
- [ ] T5 — registrar no vault: repos tocados, ordem, decisões, evidência, lições

**Verificação (verifier ≠ autor)**: <data> · resultado: PASS / gaps: …
