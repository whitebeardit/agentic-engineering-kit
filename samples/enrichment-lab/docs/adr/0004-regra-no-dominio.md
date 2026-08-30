---
id: ADR-0004
status: accepted
date: 2026-08-30
deciders: <tech lead>
enforced-by: src/__tests__/unit/arquitetura.unit.test.ts (adr-0004-violation-so-no-domain) via .dependency-cruiser.cjs
---

# Regra de negócio vive no domínio; só o domínio lança DomainRuleViolation

## Contexto

Um `if` de negócio dentro do controller ou do worker é invisível para o teste da regra e para o documento de regras.

## Decisão

Toda recusa por regra nasce em `src/domain` como `DomainRuleViolation(ruleId, motivo)`. `src/application` e
`src/interfaces` não importam a classe. Quem captura é o worker (`src/infrastructure/messaging/worker.ts`), que loga
`ruleId` e `motivo` e faz ack.

## Consequências

- - O log de produção diz qual regra recusou; o teste da regra e o documento apontam para o mesmo lugar.
- − Um erro novo de negócio exige tocar o domínio, mesmo quando "era só um if".

## Como o agente deve tratar

Ao ver "adr-0004" vermelho: leve a decisão para a entidade ou para uma specification em `src/domain/cliente`, com ID em
`docs/regras/enriquecimento.md`.
