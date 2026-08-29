# specs/ — uma pasta por feature: `NNN-nome-curto/`

Três arquivos (estilo Kiro), com **gate humano entre cada um**:

1. `requirements.md` — user stories + critérios em EARS. Ambiguidade vira `[NEEDS CLARIFICATION: pergunta]`; a spec não fecha com marcador pendente.
2. `design.md` — contratos primeiro (OpenAPI/AsyncAPI diff), sequência entre serviços, estratégia de teste (**critério → teste nomeado igual**), ordem de implementação (contrato → produtor → consumidor → legado atrás de flag), ADRs afetados.
3. `tasks.md` — uma task = um repo = um PR. Cada task termina com `Verify: <comando> → <resultado esperado>`. `[P]` marca tasks paralelizáveis.

A última task de toda feature é sempre: **registrar no vault** (repos tocados, decisões, evidência, lições).
Templates em `docs/spec-template/` do kit.
