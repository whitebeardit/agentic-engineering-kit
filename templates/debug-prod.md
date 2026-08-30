# debug-prod — primeiro movimento por sintoma (<serviço>)

Preencha por serviço ao aplicar o kit. É o arquivo que o agente `trace-finder` lê antes de procurar qualquer coisa, e o
que um humano abre às 3 da manhã. Só coordenadas, movimentos e verdades operacionais — nada de teoria.

## Coordenadas
| O quê | Onde |
|---|---|
| Backend de traces | `<Tempo/Jaeger/X-Ray — instância, retenção>` |
| Logs | `<grupo/stream; campos: trace_id, cid, eventId, eventName, trace_flags>` |
| Fila principal · DLQ | `<nomes>` (redrive: `<rota ou comando>` — **não liga trace**) |
| Script canônico de busca por id | `<caminho>` — uma implementação, com testes, usada por todos os canais (GUI, chat, CLI) |
| Painel mínimo | `<um painel por métrica de negócio>` |
| Quem chamar | `<dono do serviço · on-call>` |

## Sintoma → primeiro movimento
| Sintoma | Primeiro movimento | Depois |
|---|---|---|
| Cliente reporta erro com `traceId`/`cid` "que não abre" | logs pelo id; leia `trace_flags` — `"00"` = nunca exportado (não é retenção) | replay com `traceparent … -01`, uma requisição, `eventId` novo |
| "O registro X não atualizou" | trilha de descartes: `eventName = <descartado>` filtrado por `eventId`/`cid`; sem id, agrupe por guarda × origem | falar com o publicador com a guarda e o motivo em mãos |
| DLQ não vazia · fila envelhecendo | ler a mensagem na DLQ (corpo completo) antes de qualquer redrive | redrive só com humano; investigar é re-POST com `-01` |
| Orçamento do provedor pago no limite | métrica de compras × preço; breaker ativo? | ação é de humano (o breaker já parou de comprar) |
| Latência do fluxo caro | traces do fluxo raro (sempre amostrado); span do provedor | — |

## Trace sob demanda
`traceparent: 00-<traceid>-<spanid>-01` numa requisição única força a exportação de ponta a ponta (aceite → fila → consumidor → guardas → escrita). **Nunca ligar `-01` por padrão em produção** — é ferramenta de uma requisição. Fonte de payload para replay: DLQ ou sistema de origem; **nunca os logs** (documento mascarado).

## Verdades operacionais (preencha as suas; estas vieram de um serviço real)
1. `trace_flags: "00"` no log é o primeiro check quando um id não resolve — não é retenção nem exportador quebrado.
2. Redrive re-entrega com o `traceparent` original — não serve para investigar.
3. Replay de ingestão exige `eventId` novo: o mesmo cai na deduplicação e o trace mostra o descarte.
4. O real prevalece sobre o documento: confira produção antes de concluir "não existe".
5. Um identificador de 11/14 dígitos é documento de pessoa, não traceId — não pesquise por ele.

## Nunca
Mutação de produção (redrive, purge, alteração de alarme, permissão) sem humano e confirmação explícita · imprimir token · buscar por documento sem máscara · culpar retenção antes de ler `trace_flags`.
