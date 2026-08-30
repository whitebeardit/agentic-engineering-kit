# trace-finder — execução sobre a fixture (2026-08-30)

Execução real do agente `trace-finder` sobre dados sintéticos (`docs/observability-fixtures/`), sem conta real e sem rede — ver `docs/observability-fixtures/README.md`.

---

## Pergunta 1 — eventId `6f1c2a9e-8b3d-4c1e-9a7f-2d5b8e4c1a30` / cid `c-7a1f3e` / traceId `4bf92f3577b34da6a3ce929d0e0e4736`

**Antes de procurar**: li `docs/observability-fixtures/debug-prod.md` (coordenadas do serviço fictício "cadastro"). Não há script canônico real disponível nesta fixture; conforme o próprio `debug-prod.md` manda, "nesta fixture: leia o `.jsonl` com `grep`". Nenhum dos três ids tem 11/14 dígitos — guarda de LGPD não se aplica aqui.

**Id e janela**: eventId/cid/traceId acima; fonte lida: `docs/observability-fixtures/logs-ingestao.jsonl` (8 linhas do pedido). Backend de traces (Tempo) não consultável nesta fixture — tratado como "não consultável", não como falha.

**Comandos usados**:
```
grep -n "6f1c2a9e-8b3d-4c1e-9a7f-2d5b8e4c1a30" logs-ingestao.jsonl
grep "6f1c2a9e-8b3d-4c1e-9a7f-2d5b8e4c1a30" logs-ingestao.jsonl | grep -o '"trace_flags":"[0-9]*"' | sort -u
```

**Logs primeiro — `trace_flags`**: as 8 linhas do pedido trazem `trace_flags:"00"` (único valor, confirmado por `sort -u`). Por procedimento: `"00"` = o chamador mandou `traceparent … -00` e o trace **nunca foi exportado**; um 404 no Tempo é o resultado **correto** — não se caça retenção nem falha de exportador. **Traces depois** não se aplica (seria só para `"01"`).

**Linha do tempo** (`eventName · resultado · trace_flags`):
- `13:02:11.104` · `evento.ingestao.aceito` · http_status 202 · `00`
- `13:02:11.131` · `evento.ingestao.enfileirado` · `00`
- `13:02:14.502` · `evento.ingestao.consumido` · tentativa 1 · `00`
- `13:02:14.509` · `guarda.idempotencia` · resultado `novo` · `00`
- `13:02:14.511` · `guarda.documento` · resultado `valido` · `00`
- `13:02:14.513` · `guarda.blacklist` · "1 unidade removida" (`contato.email`) · `00`
- `13:02:14.520` · `evento.ingestao.descartado` · guard `limiar`, ruleId `RN-ENR-004` · `00`
- `13:02:14.522` · `evento.ingestao.ack` · resultado `descartado` · `00`

**Onde parou e por quê**: parou na guarda `limiar` (`ruleId: RN-ENR-004`), mensagem literal `"motivo":"descartado-limiar"`, com `unidades_evento:3`, `unidades_cadastro:12`, `limiar:11` — o evento trouxe menos unidades de dado do que o cadastro já tem, abaixo do piso exigido para sobrescrever; por isso o cadastro **não** foi atualizado. Não foi falha de fila/consumo (aceito → enfileirado → consumido → guardas ok até aqui).

**Próximo movimento**: falar com o publicador informando a guarda e o motivo (`RN-ENR-004` / `descartado-limiar` — evento com 3 unidades contra piso 11, cadastro já tem 12), conforme a linha "Registro não atualizou" do `debug-prod.md`. Não é caso de replay: replay com `-01` e `eventId` novo só resolve idempotência/exportação de trace, não a guarda de limiar — o mesmo payload seria descartado de novo pela mesma regra.

**Não verificável**: árvore de spans (trace nunca exportado, Tempo não consultável nesta fixture); conteúdo da DLQ (mensagem foi `ack`ada como descartada, não houve remessa à DLQ nos logs); valor real configurado para `limiar`/`unidades_cadastro` além do que está no log.

---

## Pergunta 2 — "e o id `52998224725`?"

**Guarda de LGPD acionada, sem busca**: `52998224725` tem 11 dígitos — é documento de pessoa (CPF), não `traceId`/`cid`/`eventId`. Por instrução do agente ("Nunca: buscar por documento sem máscara"), a consulta foi **recusada** antes de qualquer grep nos logs. Nenhum comando de busca foi executado para este id.

**Resposta ao operador**: não posso pesquisar por número de documento. Preciso do `traceId`, `cid` ou `eventId` do pedido para localizar o caso.

**Próximo movimento**: pedir ao operador o `traceId`/`cid`/`eventId` correto do pedido em questão.
