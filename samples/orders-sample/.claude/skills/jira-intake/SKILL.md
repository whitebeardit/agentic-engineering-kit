---
name: jira-intake
description: Transforma um card do Jira em specs/NNN-nome/requirements.md com critérios EARS, escopo e perguntas ao PO. Use ao pegar qualquer card novo; recusa card sem Definition of Ready.
---
# jira-intake

## Entrada
Chave do card (ou o texto colado). Leia também `docs/regras/<domínio>.md` do repo e, se houver, o mapa/regras transversais no vault — o card envelhece, a regra não.

## Passos
1. **Porteiro (DoR)** — confira `docs/definition-of-ready.md`. Falta objetivo, critérios, escopo ou "nunca modificar"? Pare e devolva a lista de lacunas para o PO. Não preencha por ele.
2. **Conflitos** — o card contradiz `docs/regras/` ou um ADR? Registre como `[NEEDS CLARIFICATION]`; nunca escolha em silêncio.
3. **Escreva `specs/NNN-<slug>/requirements.md`** a partir de `docs/spec-template/requirements.md`: histórias, critérios EARS (um por comportamento observável), comportamento preservado (`SHALL CONTINUE TO`), fora de escopo, "nunca modificar", tier de risco.
4. **Perguntas** — cada ambiguidade vira um marcador `[NEEDS CLARIFICATION: …]` com a pergunta pronta para o PO.
5. **Pare no gate 1.** Não avance para design nem código. Responda com o caminho do arquivo e a lista de perguntas.

## Não faça
Inventar critério que o card não sustenta · ampliar escopo "já que está aqui" · escrever solução técnica em requirements.
