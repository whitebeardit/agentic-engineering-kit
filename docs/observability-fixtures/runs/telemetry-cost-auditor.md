# telemetry-cost-auditor — execução sobre a fixture (2026-08-30)

Execução real do agente `telemetry-cost-auditor`, sobre dados **sintéticos** (`docs/observability-fixtures/series-inventory.md`) — nenhuma conta, rede ou serviço de produção real foi consultado. Não há preço unitário nesta fixture: custo fica "—" onde não houver preço; toda quantidade cita a tabela/janela de origem.

## Pergunta do operador
"A conta de telemetria subiu. Audite o que emite, o que vira sinal e o que cortar primeiro — sem propor nada que deixe o fluxo caro cego."

**Nota sobre "a conta subiu":** a fixture só dá um retrato mensal (`billing export`, 08/2026: 31.000.000 invocações/dia; `metrics-api series`: 1.600.000 séries ativas totais). Não há evidência de um pico correndo agora — não proponho contenção emergencial (regra 6 do agente exige custo "correndo"; nenhum indício disso aqui).

## Tabela (fonte: `series-inventory.md`, janela 30d para séries, 7d para traces, medido em 24/08/2026)

| Origem/família | Volume medido (janela, comando) | Custo | Vira sinal? (quem consome) | Ação proposta | Efeito colateral | Dono |
|---|---|---|---|---|---|---|
| Frontend web (aba, 10s) | 31M invocações/dia (`billing export` 08/2026); ~95% das noturnas voltam 401 e são cobradas (tabela "Emissores") | — | Não quando 401/deslogado | Reduzir/parar exportação em sessão inválida ou aba inativa | Perde-se telemetria de sessão expirando em uso ativo (raro); 401s não têm valor de produto | — |
| `http_server_duration` (14 buckets) | 412.000 séries/30d (`metrics-api series --match 'app_*'`) | — | Parcial — 1 painel de latência | Podar `service_instance_id` e id embutido em `http_route` | Perde granularidade por instância (cobrir via trace `-01` sob demanda) | — |
| Long-poll fila + gauge orçamento (traces) | 60.480 + 20.160 = 80.640 traces/7d, 100% amostrado, nenhum valor diagnóstico | — | Não (ninguém consome) | `suppressTracing` nas duas leituras internas | Nenhum identificado | serviço `cadastro` / — |
| `page_views_legacy_total` | 91.000 séries/30d, `user_id`+`session_id` | — | Não (ninguém; família antiga) | Descomissionar após confirmar ausência de consumo externo | Nenhum consumidor listado hoje | — |
| `GET /v1/clientes/*` (raro/caro, provedor pago) | 22 de 154 traces/7d exportados (obedece pai remoto, ~14%) | — | Sim — fluxo usado para depurar por timing | NÃO cortar: amostragem determinística fixa p/ este fluxo, ignorando decisão do pai remoto | Pequeno aumento (~22/dia) — custo desprezível dado o valor | serviço `cadastro` |
| `POST /v1/eventos` (traceparent `-00`) | 0 exportados de 128.486 eventos/7d (obedece pai, 0%) | — | Não hoje; alto valor quando falha | Razão fixa e determinística por trace id (não obedecer cegamente o `-00`) | Aumento de volume proporcional à razão escolhida | — |
| `app_errors_total` (alerta) | 0 séries/30d — nunca emitida (gate errado no código) | — | NÃO — alerta nunca dispara | Não é corte de telemetria: bug de instrumentação a corrigir | Enquanto não corrigido, é fluxo caro cego (time acha que tem alerta) | — |
| Terceiros no frontend (analytics de sessão) | contínuo, sempre; volume não separado do total do gateway | — | Não avaliado (sem linha própria) | Medir separadamente antes de agir | Sem evidência isolada — não proponho desligar | — |
| `cadastro_eventos_processados`, `cadastro_descartes`, `cadastro_compras_provedor`, `cadastro_budget_consumido` | 6 / 5 / 1 / 2 séries/30d | — | Sim — painel+runbook / alerta de orçamento | Manter (baixa cardinalidade, dono e consumidor claros) | — | dono do serviço |
| Serviço `cadastro` (coletor persistente, 60s) | sempre exporta; billed por série ativa | — | Referência de padrão saudável vs. gateway+função | Manter | — | dono do serviço |

## Top 3 cortes (custo × ruído)
1. **Frontend web em sessão inválida/deslogada** — maior linha de custo medida (31M invocações/dia, cobrada por invocação × 20 tenants), com ~95% das chamadas noturnas retornando 401 sem qualquer valor. Reduzir/pausar exportação fora de sessão válida.
2. **`http_server_duration` com labels de alta cardinalidade** — maior família de séries (412.000, ~26% das 1,6M séries totais), com só 1 painel consumidor e sem dono. Podar `service_instance_id` e id em `http_route`.
3. **Traces de polling sem valor (long-poll + gauge)** — 80.640 spans/7d amostrados a 100% sem nenhum consumidor. `suppressTracing` nas duas leituras internas.

Guardrail (não é corte, é o inverso): **não** reduzir a amostragem de `GET /v1/clientes/*` — é o único fluxo raro/caro que hoje já está sub-amostrado (obedece pai remoto) e é o que se depura por timing. Qualquer corte de custo não pode deixar esse fluxo mais cego do que já está.

## O que não medi (e o comando que mediria)
- Preço unitário por família/trace (a fixture declara "não fornecido") — sem ele, nenhum custo em R$/USD pode ser calculado.
- Volume isolado dos terceiros de analytics de sessão (está agregado ao gateway) — `logs count --group frontend-otlp --window 7d --filter thirdparty`.
- Cardinalidade real de valores distintos de `http_route` — `metrics-api series --match 'http_server_duration' --breakdown http_route`.
- Proporção de 401 vs. outros status nas chamadas noturnas do frontend — `logs count --group frontend-otlp --window 7d --filter status=401`.
- Consumo externo (dashboards/exports) de `page_views_legacy_total` fora desta fixture.

## O que precisa de humano
- Qualquer alteração de configuração, intervalo de exportação ou regra de amostragem em produção (fora do escopo deste agente).
- Corrigir o gate de código que zera `app_errors_total` (bug de instrumentação, não corte de telemetria).
- Confirmar ausência de consumidor externo antes de descomissionar `page_views_legacy_total`.
- Decidir a razão fixa de amostragem para `POST /v1/eventos` (trade-off custo × visibilidade em falha).
- Atribuir dono a `http_server_duration` e ao tráfego de terceiros antes de qualquer ação.
- Política de retenção e qualquer cláusula contratual com clientes — não avaliado aqui.
