---
name: regras-de-negocio
description: Como criar, alterar ou verificar uma regra de negócio deste domínio (RN-*). Use antes de implementar qualquer critério de aceite que mude comportamento, ou ao tocar em docs/regras/ ou no Domain. As regras em si vivem em docs/regras/, não aqui.
paths:
  - "docs/regras/**"
  - "src/**/Domain/**"
  - "src/**.Domain/**"
---
# regras-de-negocio

Esta skill é o **procedimento**. O **conhecimento** (as regras) fica em `docs/regras/<domínio>.md`; a **prova** fica em `tests/`
com o ID da regra no nome. Se a skill embutir regras, ela e o doc divergem em duas semanas.

## Ao implementar ou mudar comportamento
1. Localize a regra pelo ID em `docs/regras/`. Não existe? Crie o bloco `RN-<DOM>-<n>` em EARS **antes** de codar (modelo abaixo).
2. Conflito com ADR ou com regra transversal (vault)? Marque `[NEEDS CLARIFICATION]` e pare — não decida em silêncio.
3. Um teste por cláusula EARS, com o ID no nome (`RN_ORD_012_…`), escrito **uma vez a partir da spec** — pelo `test-designer` ou
   em sessão separada. Ele falha até a regra existir. É um sensor, não red-green por micro-passo (TDD forçado no loop do agente
   não compensou: Thoughtworks, ago/2026).
4. Implemente **no domínio**: invariante → método da entidade/agregado; validação de valor → value object; regra entre agregados →
   domain service; predicado reutilizável → specification. Nunca em controller, application service, repositório ou SP —
   o teste de arquitetura reclama citando o ADR.
5. Atualize no bloco da regra: `Código:`, `Teste:`, `Confiança:` (`verified` = tem teste que passa; `inferred` = lida do código, sem
   teste), `Última revisão:`, `Dono:`.
6. A regra cruza serviços? Ela sobe para o vault; este doc passa a apontar para lá.

## Modelo de bloco (docs/regras/<domínio>.md)
```
## RN-ORD-012 — Cancelamento parcial
WHEN o cliente cancela um item de pedido não faturado
THE SYSTEM SHALL recalcular o total e emitir OrderItemCancelled
IF o pedido já foi faturado THEN THE SYSTEM SHALL recusar com PedidoFaturado
Código: Orders.Domain/Order.cs → CancelItem   Teste: RN_ORD_012_*   Confiança: verified   Dono: <pessoa>   Desde: ADR-0003   Última revisão: AAAA-MM-DD
```

## Não faça
Regra em `AGENTS.md`/`CLAUDE.md` (é fato de negócio, não gotcha) · regra só no card do Jira (o card é a mudança, não o estado) ·
"modernizar de passagem" no legado · aprovar `.verified.txt` alterado sem explicar no PR.
