---
paths:
  - "**/erp-mono/**"
  - "**/Legacy/**"
  - "**/*.Legacy/**"
  - "**/legacy/**"
---
# Legado (ativa ao tocar no monolito)

- **Nenhum refactor sem characterization test** cobrindo o fluxo (semente fixa: Verify + Bogus · jest snapshot + faker). Se não existe, a primeira task é criá-lo.
- Mudança de comportamento entra **atrás de feature flag**; o caminho antigo continua até o PO validar.
- `.verified.txt` ou `__snapshots__/*.snap` mudou? Isso é mudança de comportamento: explique no PR, não aprove o baseline em silêncio (`jest -u` é do humano).
- Não "modernize" de passagem (nullable, LINQ, async) — um PR de refactor é um PR de refactor.
- Pergunte ao agente `legacy-navigator` onde a regra é calculada hoje antes de assumir.
