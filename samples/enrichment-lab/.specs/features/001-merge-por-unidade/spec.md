# Aplicar evento ao cadastro com limiar de completude (ENR-042) Specification

**Card**: ENR-042 · **Tier de risco**: alto (dados pessoais) · **Tamanho (auto-sizing)**: Complex — tier alto e contrato público novo (`ClienteAtualizado` v1)
**Repo dono do contrato**: enrichment-lab. O consumidor no CRM é feature separada no repo do CRM.

## Problem Statement

Hoje o worker **substitui** o cadastro pelo conteúdo de cada evento (`Cliente.substituir`): um evento antigo ou parcial
apaga informação boa, e quem consome o cadastro não sabe se algo mudou de verdade. Queremos aplicar cada evento
**por unidade** (campo folha), respeitando recência e proveniência, recusando evento incompleto contra cadastro completo,
e avisar os consumidores só quando o cadastro muda.

## Goals

- [ ] Evento de documento novo cria o cadastro; evento seguinte preenche lacunas e sobrescreve só o que é mais novo.
- [ ] Evento de provedor nunca sobrescreve unidade declarada pelo cliente; evento incompleto contra cadastro completo é recusado com `RN-ENR-004`.
- [ ] Nada muda → nada grava, versão não avança, nenhum evento; algo muda → exatamente um `ClienteAtualizado` v1.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
| ------- | ------ |
| Consulta ao provedor quando o documento não existe | Card próprio depois desta entrega |
| Política de retenção de dados pessoais | Regra transversal (vault), não deste serviço |
| Consumidor do `ClienteAtualizado` no CRM | Outro repositório; esta spec é a do repo dono do contrato |
| Alterar `POST /v1/eventos` (v2.1), o schema de ingestão ou `ClienteAtualizado` v1 depois de publicado | "Nunca modificar" do card |
| Publicação real do evento (fila de saída) | Neste laboratório o publicador é em memória; o contrato é o objeto + `asyncapi.yaml` |

---

## Assumptions & Open Questions

Every ambiguity is resolved or recorded here - nothing is left silently unclear.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Valor de N (limiar de completude) | 11, configurável por `LIMIAR_N` (`src/infrastructure/config/env.ts`) | O card diz "hoje a operação usa 11"; parâmetro evita hardcode | n — [NEEDS CLARIFICATION: PO confirma 11?] |
| Evento de provedor mais novo sobre unidade declarada pelo cliente | Nunca sobrescreve (critério 4 é absoluto) | Declarado pelo cliente vale mais que comprado | y (card) |
| Empate de instante entre evento e unidade gravada | Mantém o gravado | "Estritamente mais novo" no card | y (card) |
| `apto` | É uma unidade como as outras (recência e proveniência); quando ausente, RN-ENR-006 já a inferiu antes do merge | Uma regra só para todas as unidades | y |
| Contagem de campos para o limiar | Unidades folha depois da blacklist (RN-ENR-003), sem contar `apto` | O limiar mede completude dos dados, não flags | y |
| Concorrência entre dois eventos do mesmo documento | Coberta por RN-ENR-005 (gravação condicional com releitura) — o merge é refeito na releitura | Já existe e tem teste | y |
| Evento que não muda nada | Não grava, não avança versão, não emite; `eventId` é registrado como processado | Anti-eco: consumidores não recebem ruído | y (card) |

**Open questions:** none blocking - o valor de N segue como parâmetro com default 11 até o PO confirmar (registrado acima).

### Implicit-requirement dimensions (Complex: cada dimensão vira requisito ou N/A)

| Dimension | Resolution |
| --------- | ---------- |
| Input validation & bounds | Já coberta na borda (schema 2020-12) e pelas guardas RN-ENR-001/003; ING-05 (limiar) |
| Failure / partial-failure states | ING-06 (nada muda → nada grava); falha técnica → RN-ENR-005 (retry/DLQ) |
| Idempotency / retry / duplicate handling | RN-ENR-002 (fora desta spec, já existe); ING-06 garante que reprocessar o mesmo estado não emite evento |
| Auth boundaries & rate limits | N/A because não há autenticação neste laboratório; a borda HTTP é contrato + schema |
| Concurrency / ordering | RN-ENR-005 (releitura + merge refeito); fila FIFO por documento garante ordem por grupo |
| Data lifecycle / expiry | N/A because nada é apagado por esta feature; retenção é transversal |
| Observability | ING-07 (o evento é o sinal); recusa por ING-05 é logada pelo worker com `ruleId` e `motivo` (já existe) |
| External-dependency failure | N/A because o publicador é em memória; consumidor fora do escopo |
| State-transition integrity | ING-03/ING-04 (quem pode sobrescrever o quê) e ING-06 (versão só avança com mudança) |
| Personal data (tier alto) | Documento mascarado em todo log (RN-ENR-001); o evento publicado leva só documento e versão |

---

## User Stories

### P1: Aplicar o evento ao cadastro sem apagar informação boa ⭐ MVP

**User Story**: As a operação de dados, I want que cada evento seja aplicado ao cadastro campo a campo, respeitando o que já sabemos e de quem veio so that um evento antigo ou incompleto não apague informação boa e os consumidores sejam avisados só quando algo mudou.

**Why P1**: É o vertical slice inteiro: criação, merge por unidade, proveniência, limiar, anti-eco e evento.

**Acceptance Criteria** (each line is one EARS pattern):
1. WHEN chega um evento de um documento sem cadastro THEN system SHALL criar o cadastro com as unidades do evento, cada uma anotada com o instante (`updatedAt`) e a origem (`origin`) do evento, e gravar com versão 1  <!-- event-driven -->
2. WHEN o evento traz uma unidade que o cadastro não tem THEN system SHALL preencher a unidade, mesmo que o `updatedAt` do evento seja anterior ao das unidades já gravadas  <!-- event-driven -->
3. WHEN o evento traz uma unidade que o cadastro já tem THEN system SHALL sobrescrever só se o `updatedAt` do evento for estritamente posterior ao instante da unidade gravada; em empate ou evento anterior SHALL manter o gravado  <!-- event-driven -->
4. IF a origem do evento é `provedor:*` THEN system SHALL só preencher lacunas ou sobrescrever unidades cuja origem gravada também é `provedor:*` — nunca uma unidade de origem `cliente:*`, mesmo com instante mais novo  <!-- unwanted-behavior -->
5. IF o cadastro tem N ou mais unidades e o evento traz menos de N THEN system SHALL recusar com `DomainRuleViolation` cujo `ruleId` é `RN-ENR-004` e `motivo` `descartado-limiar`, sem alterar unidades, versão nem eventos; eventos de origem `provedor:*` nunca são recusados por isto  <!-- unwanted-behavior -->
6. IF o estado resultante do merge é idêntico ao gravado THEN system SHALL devolver `changed = false`, não gravar, não avançar a versão e não emitir evento  <!-- unwanted-behavior -->
7. WHEN o cadastro muda THEN system SHALL emitir exatamente um `ClienteAtualizado` v1 com `documento`, a `versao` nova e `occurredAt` — e o worker SHALL só orquestrar: carregar, delegar a decisão ao domínio (entidade + specification), gravar condicionalmente e publicar  <!-- event-driven -->

**Independent Test**: Documento novo recebe evento A (nome, e-mail, telefone; 12:00) → versão 1 e um `ClienteAtualizado`. Evento B do mesmo documento (e-mail diferente, 11:00; cep novo) → e-mail mantido, cep preenchido, versão 2, um evento. Evento C de provedor (nome diferente, 13:00) → nome mantido, `changed = false`, versão 2, nenhum evento. Evento D com um campo só contra cadastro com N ≥ 11 → recusa `RN-ENR-004`, nada muda.

---

## Edge Cases

Edge cases are usually unwanted-behavior (IF/THEN) or boundary (WHEN) criteria:
- WHEN o evento e a unidade gravada têm o mesmo instante THEN system SHALL manter o gravado (boundary de ING-03)
- WHEN o cadastro tem exatamente N unidades e o evento traz exatamente N THEN system SHALL aceitar (boundary de ING-05: "menos de N" recusa)
- IF o evento é de provedor e a unidade gravada é de provedor com instante mais antigo THEN system SHALL sobrescrever (ING-04 permite)
- IF o evento não traz nenhuma unidade nova nem mais nova, mas traz `apto` diferente THEN system SHALL tratar `apto` como unidade (ING-03) e emitir evento (ING-07)

---

## Requirement Traceability

Each requirement gets a unique ID for tracking across design, tasks, and validation.

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| ING-01 | P1: documento novo cria cadastro com versão 1 | In Tasks | In Tasks |
| ING-02 | P1: unidade ausente é preenchida mesmo de evento antigo | In Tasks | In Tasks |
| ING-03 | P1: sobrescreve só se estritamente mais novo; empate mantém | In Tasks | In Tasks |
| ING-04 | P1: provedor só preenche lacuna ou sobrescreve provedor | In Tasks | In Tasks |
| ING-05 | P1: limiar de completude recusa com RN-ENR-004 | In Tasks | In Tasks |
| ING-06 | P1: anti-eco — nada muda, nada grava, sem evento | In Tasks | In Tasks |
| ING-07 | P1: um ClienteAtualizado v1 por mudança; worker orquestra | In Tasks | In Tasks |

**ID format:** `[CATEGORY]-[NUMBER]` · **Status values:** Pending → In Design → In Tasks → Implementing → Verified
**Coverage:** 7 total, 7 mapped to tasks (T1–T6), 0 unmapped

---

## Success Criteria

How we know the feature is successful:
- [ ] `npm run gate` verde com os testes `RN_ENR_004_*` cobrindo ING-01..07 (1:1, nomes com o ID da regra).
- [ ] Verifier do tlc: validation.md PASS, mutantes injetados mortos.
- [ ] `docs/regras/enriquecimento.md` com o bloco RN-ENR-004 apontando código, teste e `Confiança: verified`; `Cliente.substituir` removido.
