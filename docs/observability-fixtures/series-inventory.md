# Inventário de séries e emissores — serviço fictício "cadastro" (janela: 30 dias, medido em 24/08/2026)

Comandos usados (contas fictícias): `metrics-api series --match 'app_*' --window 30d` · `logs count --group frontend-otlp --window 7d` · `billing export --service telemetry --month 08`.

## Emissores
| Origem | Intervalo de exportação | Exporta quando… | Destino | Cobrança |
|---|---|---|---|---|
| Frontend web (aba do usuário) | 10 s | aba aberta, mesmo deslogada (≈ 95 % das requisições noturnas voltam 401 e são cobradas) | gateway HTTP + função por requisição (uma por tenant, 20 tenants) | por invocação |
| Serviço `cadastro` (API + worker) | 60 s (métricas), traces por span | sempre | coletor persistente | por série ativa |
| Terceiros carregados no frontend (analytics de sessão) | contínuo | sempre | mesmo gateway (interceptado pelo SDK) | por invocação |

## Famílias de métricas (séries ativas/30d)
| Família | Séries ativas | Labels de alta cardinalidade | Quem consome | Dono |
|---|---|---|---|---|
| `http_server_duration` (histograma, 14 buckets) | 412.000 | `service_instance_id`, `http_route` com id na rota | painel de latência (1 painel) | — |
| `page_views_total` | 96.000 | `user_id` | painel de produto | time de produto |
| `page_views_legacy_total` | 91.000 | `user_id`, `session_id` | ninguém (família antiga, ainda emitida) | — |
| `app_errors_total` | 0 | — | alerta de erro (nunca disparou: gate errado no código, a métrica não é emitida) | — |
| `cadastro_eventos_processados` | 6 | `resultado` | painel do serviço + runbook | dono do serviço |
| `cadastro_descartes` | 5 | `guarda` | painel do serviço + runbook | dono do serviço |
| `cadastro_compras_provedor` | 1 | `provider` | alerta de orçamento | dono do serviço |
| `cadastro_budget_consumido` (gauge lido a cada 60 s) | 2 | `provider`, `janela` | alerta de orçamento | dono do serviço |

## Traces (7 dias)
| Fluxo | Traces/7d | Amostragem atual | Valor diagnóstico |
|---|---|---|---|
| Leitura do gauge de orçamento (a cada 60 s, fora de span de requisição) | 20.160 | 100 % | nenhum (é a exportação criando raiz) |
| `POST /v1/eventos` com `traceparent … -00` do chamador | 0 exportados de 128.486 eventos | obedece o pai (0 %) | alto quando um evento falha; nenhum no volume |
| `GET /v1/clientes/*` (raro, caro: chama provedor pago) | 22 de 154 | obedece o pai | alto — é o fluxo que se depura por timing |
| Long-poll da fila (`ReceiveMessage`) | 60.480 | 100 % | nenhum |
| `/health` | 0 | ignorado na instrumentação | — |

## Custo
| Item | Valor medido | Fonte |
|---|---|---|
| Invocações do gateway+função de telemetria | 31.000.000/dia | `billing export` (08/2026) |
| Séries ativas totais | 1.600.000 | `metrics-api series` |
| Preço unitário | não fornecido nesta fixture | — |
