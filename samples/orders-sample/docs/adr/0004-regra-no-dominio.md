---
id: ADR-0004
status: accepted
date: 2026-08-27
deciders: <tech lead>
enforced-by: tests/Orders.Tests/ArchitectureTests.cs (Application_nao_lanca_DomainRuleViolationException)
---
# Regra de negócio é lançada pelo domínio, nunca pela aplicação

## Contexto
`if (order.Status == Faturado) throw …` no handler "funciona" — e some da vista de quem lê o domínio.

## Decisão
Só `Orders.Domain` lança `DomainRuleViolationException`. Handlers chamam métodos do agregado/specification e deixam a exceção subir.

## Alternativas rejeitadas
- Result pattern em toda camada — adiado; exceção com `RuleId` já dá rastreabilidade para logs e testes.

## Consequências
- + `grep DomainRuleViolationException` lista todas as regras impostas.
- − Exceção como fluxo de controle em casos esperados (cancelar pedido faturado). Aceito por ora.

## Como o agente deve tratar
Ao ver "viola ADR-0004": mova a verificação para a entidade ou specification e chame-a do handler.
