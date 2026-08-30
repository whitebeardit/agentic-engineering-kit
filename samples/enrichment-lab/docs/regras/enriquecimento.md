# Regras de negócio — Enriquecimento de cadastro (src/domain/cliente)

Fonte de verdade escrita. O card descreve a **mudança**; este arquivo descreve o **estado**. Toda regra tem ID, EARS,
onde vive no código, qual teste a prova, **confiança** (`verified` = teste passa; `inferred` = lida do código, sem teste
completo), dono e data. A skill `regras-de-negocio` é o procedimento para mudar isto.

Ordem fixa das guardas no worker: RN-ENR-002 → RN-ENR-001 → RN-ENR-003 → RN-ENR-006 (apto) → RN-ENR-004 (limiar e merge) → gravação (RN-ENR-005).

## RN-ENR-001 — Documento válido

THE SYSTEM SHALL recusar CPF (11 dígitos) ou CNPJ (14 dígitos) cujos dígitos verificadores não conferem, ou com todos os dígitos iguais
THE SYSTEM SHALL recusar com `DomainRuleViolation(RN-ENR-001, descartado-documento)` antes de ler ou gravar qualquer coisa
THE SYSTEM SHALL CONTINUE TO nunca escrever o documento inteiro em log ou mensagem de erro (só os 4 últimos dígitos)
Código: `src/domain/cliente/documento.ts` (`cpfValido`, `cnpjValido`, `exigirDocumentoValido`, `mascarar`) Teste: `src/__tests__/unit/RN_ENR_001.documento.unit.test.ts` (5) Confiança: inferred Dono: <pessoa> Desde: 2026-08-30 Última revisão: 2026-08-30

## RN-ENR-002 — Idempotência por eventId

IF o `eventId` já foi processado (gravado ou descartado) THEN THE SYSTEM SHALL fazer ack sem reprocessar e sem erro
THE SYSTEM SHALL registrar o `eventId` como processado só depois de um resultado terminal (gravado ou descartado por regra)
Código: `src/domain/cliente/service/guardas.ts` (guarda 1) · `src/infrastructure/messaging/worker.ts` (`registrarProcessado`) Teste: `src/__tests__/unit/RN_ENR_002_003.guardas.unit.test.ts` (2) Confiança: inferred Dono: <pessoa> Desde: 2026-08-30 Última revisão: 2026-08-30

## RN-ENR-003 — Blacklist de valores

THE SYSTEM SHALL remover do evento a unidade cujo valor está na lista global ou na lista do caminho, mantendo o restante
IF não sobra unidade nenhuma (e o evento não traz `apto`) THEN THE SYSTEM SHALL recusar com `DomainRuleViolation(RN-ENR-003, descartado-blacklist)`
Código: `src/domain/cliente/service/guardas.ts` (guarda 3) · lista em `src/infrastructure/config/factories.ts` (`BLACKLIST_PADRAO`) Teste: `src/__tests__/unit/RN_ENR_002_003.guardas.unit.test.ts` (3) Confiança: inferred Dono: <pessoa> Desde: 2026-08-30 Última revisão: 2026-08-30

## RN-ENR-004 — Aplicar evento ao cadastro (merge por unidade)

WHEN chega um evento de um documento sem cadastro THE SYSTEM SHALL criar o cadastro com as unidades do evento, anotadas com instante e origem, e gravar com versão 1
WHEN o evento traz uma unidade que o cadastro não tem THE SYSTEM SHALL preencher a unidade, mesmo que o evento seja mais antigo
WHEN o evento traz uma unidade que o cadastro já tem THE SYSTEM SHALL sobrescrever só se o instante do evento for estritamente posterior ao da unidade; em empate ou evento anterior SHALL manter
IF a origem é `provedor:*` THEN THE SYSTEM SHALL só preencher lacunas ou sobrescrever unidades cuja origem gravada também é provedor — nunca uma unidade `cliente:*`
IF o cadastro tem N ou mais unidades e o evento traz menos de N THEN THE SYSTEM SHALL recusar com `DomainRuleViolation(RN-ENR-004, descartado-limiar)` sem alterar nada (nunca para origem provedor; N = `LIMIAR_N`, default 11)
IF o estado resultante é idêntico ao gravado THEN THE SYSTEM SHALL devolver `changed = false`, não gravar, não avançar a versão e não emitir evento
WHEN o cadastro muda THE SYSTEM SHALL emitir exatamente um `ClienteAtualizado` v1 (documento, versão nova, instante); `apto` é uma unidade como as outras
Código: `src/domain/cliente/cliente.entity.ts → aplicar` · merge em `src/domain/cliente/service/merge.ts` · predicado em `src/domain/cliente/specifications/evento-elegivel-para-merge.ts` · worker `src/infrastructure/messaging/worker.ts` (só orquestra)
Teste: `src/__tests__/unit/RN_ENR_004.merge-por-unidade.unit.test.ts` (um por cláusula EARS + boundaries) · integração `src/__tests__/integration/clientes.get.int.test.ts` Confiança: inferred
Contrato afetado: evento `ClienteAtualizado` v1 (público — `src/contracts/asyncapi.yaml`; `rules/contracts.md`; AD-001)
Dono: <pessoa> Desde: spec `.specs/features/001-merge-por-unidade/` (ING-01..07) Última revisão: 2026-08-30

## RN-ENR-005 — Gravação condicional por versão

THE SYSTEM SHALL gravar o cadastro só se a versão persistida for a que foi lida (0 = ainda não existe); a versão nova é a lida + 1
IF a versão persistida for outra THEN THE SYSTEM SHALL lançar `ConflictError`, e o worker SHALL reler, refazer a aplicação do evento e tentar de novo (até 3 vezes)
IF a falha for técnica e persistir THEN THE SYSTEM SHALL devolver a mensagem à fila; após 5 recebimentos ela vai para a DLQ
Código: `src/infrastructure/memory/cliente.memoria.ts` (`gravar`) · `src/infrastructure/messaging/worker.ts` (`gravarComRetry`) · `src/infrastructure/memory/fila.memory.ts` (`devolver`) Teste: `src/__tests__/unit/RN_ENR_005.gravacao-condicional.unit.test.ts` (4) Confiança: inferred Dono: <pessoa> Desde: 2026-08-30 Última revisão: 2026-08-30

## RN-ENR-006 — Aptidão inferida pelo legado

IF o evento não declara `apto` THEN THE SYSTEM SHALL inferir `apto` pela pontuação de `legacy/calcula-apto.js` (só "APTO" vira `true`)
THE SYSTEM SHALL CONTINUE TO respeitar `apto` quando o evento o declara (o legado não sobrescreve)
Código: `src/domain/cliente/service/apto.ts` (`inferirApto`) · `legacy/calcula-apto.js` (pesos e cortes sem explicação; characterization em `src/__tests__/unit/legacy/`) Teste: `src/__tests__/unit/RN_ENR_006.apto.unit.test.ts` (2) Confiança: inferred Dono: <pessoa> Desde: 2026-08-30 Última revisão: 2026-08-30

## Regras transversais (vivem no vault, não aqui)

- Política de retenção de dados pessoais → Jurídico + Engenharia concordam no vault `engenharia/regras-transversais.md#retencao`.
