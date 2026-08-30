# enrichment-lab

Serviço de enriquecimento de cadastro **em miniatura** — laboratório do kit Whitebeard e do livro _Cercando a IA_.
Sintético, escrito do zero; espelha a arquitetura de um serviço real em produção (contract-first, fila, worker com
guardas, merge por unidade, gravação condicional por versão), sem nuvem: tudo roda em memória.

```bash
npm install      # ≈ 30 s, uma vez
npm run gate     # tsc --noEmit && eslint && jest --ci  (o gate que o agente obedece)
npm run dev      # build + sobe em http://localhost:3000 — POST /v1/eventos, GET /v1/clientes/{documento}, /health
```

Leia `AGENTS.md` antes de pedir qualquer coisa a um agente: é o contexto canônico deste repositório.
