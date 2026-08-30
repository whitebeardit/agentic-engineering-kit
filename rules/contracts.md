---
paths:
  - "**/openapi*.{yaml,yml,json}"
  - "**/asyncapi*.{yaml,yml,json}"
  - "**/Contracts/**"
  - "**/*.Contracts/**"
  - "**/Events/**"
  - "**/contracts/**"
  - "**/events/**"
  - "**/*.schema.json"
---
# Contratos (ativa ao tocar em API, eventos ou DTOs públicos)

- Mudança de contrato é **sempre** compatível retroativa ou versionada (`v2`, novo tópico). Remoção de campo = deprecação com prazo.
- Antes de commitar: `oasdiff breaking <antigo> <novo>` sem ERR; para eventos, schema novo no catálogo com consumidores listados.
- Peça ao agente `contract-reviewer` a lista de consumidores afetados e inclua no PR.
- Ordem: contrato → produtor → consumidor. Nunca o consumidor primeiro.
