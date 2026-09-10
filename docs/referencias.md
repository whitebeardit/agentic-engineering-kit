# Referências do kit

Claim de pesquisa impresso numa skill, num agente ou no e-book exige ficha — a mesma regra do livro *Cercando a IA*.
Cada linha diz o que a fonte sustenta e o que **não** sustenta.

| Chave | Fonte | O que sustenta | O que não sustenta | Acesso |
|---|---|---|---|---|
| Böckeler, 2026 | Böckeler, B. "TDD inside the agent loop — theater or actual value?". Série *Exploring Gen AI* (martinfowler.com), 10 ago. 2026. https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html | Experimento exploratório (cinco lotes de tarefas, com e sem TDD imposto no loop do agente, qualidade julgada por um modelo): "there was no clearly discernable difference based on TDD workflow versus no TDD workflow"; tokens com TDD 8,50× (tarefas pequenas), 2,96× (médias), 4,89× (grandes); recomenda *mutation testing* como sensor e testes escritos a partir da spec — é o passo 3 da skill `regras-de-negocio` | Não é ensaio controlado nem amostra grande; mede TDD **forçado no loop do agente**, não TDD praticado por pessoas; "não compensou" é resumo nosso — a frase do artigo é "sem diferença discernível" a ≥ 3× o custo | 2026-09-07 (conferida pelo livro); 2026-09-09 |
