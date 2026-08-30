---
id: ADR-0003
status: accepted
date: 2026-08-30
deciders: <tech lead>, <arquiteto>
enforced-by: src/__tests__/unit/arquitetura.unit.test.ts (adr-0003-domain-puro; adr-0003-application-sem-infra) via .dependency-cruiser.cjs
---

# Domain não depende de nada; Application depende só de Domain

## Contexto

Regras de cadastro estavam espalhadas entre controller, worker e repositório. Agentes de IA reproduzem o padrão que encontram.

## Decisão

`src/domain` não importa `application`, `infrastructure` nem `interfaces`. Portas (`ClienteRepository`, `FilaPort`) são
definidas no domínio e implementadas em `src/infrastructure`. `src/application` só orquestra e recebe as implementações
pela fábrica (`src/infrastructure/config/factories.ts`).

## Alternativas rejeitadas

- Application definindo as interfaces — o domínio passaria a depender de Application para persistir.
- Confiar em revisão humana — não escala; o teste falha o `npm test` com a mensagem certa.

## Consequências

- - Regra tem um endereço só; o agente `legacy-navigator` e o Verifier do tlc-spec-driven sabem onde olhar.
- − Um pouco mais de cerimônia para persistência simples.

## Como o agente deve tratar

Ao ver "adr-0003" vermelho no `npm test`: mova o acesso a dados para uma porta em `src/domain` e implemente em
`src/infrastructure`. Não importe de `infrastructure` para "resolver".
