# debug-prod — primeiro movimento por sintoma (serviço fictício "cadastro")

## Coordenadas
| O quê | Onde |
|---|---|
| Backend de traces | Tempo (retenção 14 dias) |
| Logs | grupo `cadastro-prod`; campos `trace_id`, `cid`, `eventId`, `eventName`, `trace_flags`; fixture: `docs/observability-fixtures/logs-ingestao.jsonl` |
| Fila principal · DLQ | `cadastro-prod.fifo` · `cadastro-prod-dlq.fifo` (redrive: rota `/ops/redrive` — **não liga trace**) |
| Script canônico de busca por id | `scripts/trace-lookup.py --trace-id <hex> --format prompt` (nesta fixture: leia o `.jsonl` com `grep`) |
| Painel mínimo | um painel por métrica `cadastro_*` |
| Quem chamar | dono do serviço (on-call: tópico `cadastro-prod-alertas`) |

## Sintoma → primeiro movimento
| Sintoma | Primeiro movimento | Depois |
|---|---|---|
| Cliente reporta id "que não abre" | logs pelo id; ler `trace_flags` | replay com `traceparent … -01`, `eventId` novo |
| "Registro não atualizou" | `eventName = evento.ingestao.descartado` por `eventId`/`cid` | falar com o publicador com guarda e motivo |
| DLQ não vazia | ler a mensagem na DLQ | redrive só com humano |

## Verdades operacionais
1. `trace_flags: "00"` = nunca exportado. 2. Redrive não liga trace. 3. Replay exige `eventId` novo. 4. O real prevalece sobre o documento. 5. 11/14 dígitos é documento, não traceId.
