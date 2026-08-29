---
id: ADR-0003
status: accepted
date: 2026-08-27
deciders: <tech lead>, <arquiteto>
enforced-by: tests/Orders.Tests/ArchitectureTests.cs (Domain_nao_depende_de_Application_nem_de_Infrastructure; Application_nao_depende_de_Infrastructure)
---
# Domain não depende de nada; Application depende só de Domain

## Contexto
Regras de pedido estavam espalhadas entre controller, handler e repositório. Agentes de IA reproduzem o padrão que encontram.

## Decisão
`Orders.Domain` não referencia outro projeto. Portas (`IOrderRepository`) são definidas no domínio e implementadas em `Orders.Infrastructure`. `Orders.Application` só orquestra.

## Alternativas rejeitadas
- Application definindo as interfaces — o domínio passaria a depender de Application para persistir eventos.
- Confiar em revisão humana — não escala; o teste falha o build com a mensagem certa.

## Consequências
- + Regra tem um endereço só; o agente `legacy-navigator` e o `verifier` sabem onde olhar.
- − Um pouco mais de cerimônia para persistência simples.

## Como o agente deve tratar
Ao ver "viola ADR-0003" no build: mova o acesso a dados para uma interface em Domain e implemente em Infrastructure. Não adicione referência de projeto para "resolver".
