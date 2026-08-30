# Fixtures de observabilidade (sintéticas, na forma das saídas reais)

Entradas para exercitar os agentes `trace-finder`, `telemetry-cost-auditor` e `alert-auditor` sem tocar em nenhuma conta.
A **forma** é a de saídas reais de um serviço em produção (linhas de log estruturado com `eventName`/`trace_flags`,
inventário de séries por família, lista de alarmes com destino e assinaturas); os **valores** — ids, nomes, volumes,
contas — são inventados. Nenhum dado de cliente. `runs/` guarda a saída real de cada agente rodando sobre estas
fixtures (data no cabeçalho de cada arquivo).

| Arquivo | Para | Forma |
|---|---|---|
| `logs-ingestao.jsonl` | trace-finder | 9 linhas de log de um mesmo pedido: aceito → enfileirado → consumido → descartado; `trace_flags` `"00"` |
| `series-inventory.md` | telemetry-cost-auditor | famílias de métricas × séries ativas/30d × intervalo de exportação × consumidor |
| `alarms.json` | alert-auditor | 3 alarmes: um com assinante confirmado, um apontando para tópico sem assinatura, um sem destino |
| `debug-prod.md` | trace-finder | o `docs/debug-prod.md` preenchido para o serviço fictício |
