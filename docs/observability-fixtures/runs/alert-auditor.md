# alert-auditor — execução sobre a fixture (2026-08-30)

Execução real do agente `alert-auditor`, sobre dados **sintéticos** (`docs/observability-fixtures/alarms.json`) — nenhuma conta ou serviço de produção real foi consultado.

## Pergunta do operador
"Vamos fazer um backfill arriscado amanhã. Temos alarme para tudo o que importa? Se disparar, alguém recebe?"

**Resposta curta: não.** Existem 3 alarmes com forma de alarme de produção, mas hoje **nenhum dos três** chega, com confirmação, a uma pessoa. Os dois que apontam para um tópico apontam para o único assinante que está `PendingConfirmation` há mais de 5 semanas; o terceiro não tem destino nenhum; e o único tópico com assinante `Confirmed` não recebe ação de nenhum alarme.

## Alarmes (real prevalece sobre o doc de infra — ver "pontos cegos")

| Alarme | Métrica | Condição | Destino | Assinante confirmado? | Dono | Runbook | Estado / última transição |
|---|---|---|---|---|---|---|---|
| `cadastro-prod-dlq-nao-vazia` | `fila/ApproximateNumberOfMessagesVisible` (QueueName=`cadastro-prod-dlq.fifo`) | Maximum > 0, 1 período de 300 s; dado ausente = notBreaching | tópico `cadastro-prod-alertas` | **Não** — email `on-call@<dominio-ficticio>` em `PendingConfirmation` desde 2026-07-23 | null | Sim — `debug-prod.md`: "DLQ não vazia → ler mensagem, redrive só com humano" | OK desde 2026-07-23T18:40Z |
| `cadastro-prod-fila-envelhecendo` | `fila/ApproximateAgeOfOldestMessage` (QueueName=`cadastro-prod.fifo`) | Maximum > 900 s, 1 período de 300 s; tratamento de dado ausente **não especificado** | tópico `cadastro-prod-alertas` (mesmo destino acima) | **Não** — mesma assinatura pendente | "dono do serviço" (papel genérico, sem contato) | **Não** — `debug-prod.md` só cobre DLQ, não idade/backlog da fila principal | OK desde 2026-08-13T09:12Z |
| `cadastro-prod-5xx` | `http_server_duration{status=5xx}` (taxa) | taxa > 2% em 5 min; tratamento de dado ausente **não especificado** | **nenhum** (`acoes: []`) | N/A — sem destino | null | Não | `INSUFFICIENT_DATA` desde 2026-06-02T11:00Z (~3 meses) |

Tópico `cadastro-prod-alertas-financeiro` (assinatura `Confirmed`, `financeiro@<dominio-ficticio>`) existe mas **nenhum alarme aponta para ele** — capacidade de notificação confirmada e não usada.

## Pontos cegos
1. **Script de verificação** (`scripts/check-production-infra.sh`, passo 10) confere `describe-alarms` (alarme existe) e `list-topics` (tópico existe), mas **não chama `list-subscriptions-by-topic`**. Resultado da última execução: "ok" — mesmo com a única assinatura operacional pendente há 5+ semanas. Checar que o tópico existe não é checar que alguém recebe.
2. **Doc de infra desatualizado**: `docs/infra/infra-stages.md` diz "❌ Alarme DLQ não vazia" e "❌ Tópico de alertas + assinaturas" — ambos falsos hoje (alarme em OK há mais de um mês; tópicos existem, um com assinante confirmado). Exatamente o caso que o procedimento manda desconfiar: doc não é prova.
3. `cadastro-prod-5xx` está em `INSUFFICIENT_DATA` há quase 3 meses — na prática é um alarme cego, não coberto, mesmo aparecendo na lista.
4. Métrica de `cadastro-prod-5xx` é nomeada como **duração** (`http_server_duration`) sendo usada para calcular **taxa de erro** por status; vale confirmar se é a métrica de origem certa ou se deveria existir um contador de requests dedicado por status.

## Lacunas (recursos críticos sem alarme confirmado)
- Nenhum alarme, hoje, entrega notificação com assinante confirmado — cobertura efetiva é zero para o backfill de amanhã.
- Falta alarme de **profundidade/backlog em contagem** da fila principal (`cadastro-prod.fifo`) — só há alarme de idade da mensagem mais antiga, não de volume, relevante justamente num backfill que empurra volume.
- Sem sinal de alarme de **orçamento de provedor pago** ou de **erro/throttling de terceiro** na fixture — se o backfill chama provider externo, não há cobertura visível.

## O que precisa de humano
1. Confirmar a assinatura `PendingConfirmation` de `on-call@<dominio-ficticio>` no tópico `cadastro-prod-alertas` — sem isso, 2 dos 3 alarmes disparam no vácuo.
2. Investigar e corrigir `cadastro-prod-5xx` em `INSUFFICIENT_DATA` há ~3 meses, e decidir/atribuir dono (`cadastro-prod-dlq-nao-vazia` e `cadastro-prod-5xx` estão com dono `null`).
3. Decidir se, como mitigação antes do backfill, os alarmes operacionais devem ganhar a ação do tópico `cadastro-prod-alertas-financeiro` (já com assinante confirmado) — mudança de config de alarme, não de permissão/IAM; decisão do dono do serviço.
4. Corrigir o passo 10 do script de verificação para checar `list-subscriptions-by-topic` e o estado da assinatura, não só a existência do tópico.
5. Atualizar `docs/infra/infra-stages.md`, hoje desatualizado em dois pontos.
