# 001-merge-por-unidade proofs

**HEAD**: 1f534ae
**Tree**: clean
**Shell**: /bin/sh
**Result**: 17 pass, 0 fail

| Check | Proof | Result |
| --- | --- | --- |
| C1 | `run unit / ✓ RN_ENR_004_WHEN_documento_sem_cadastro_SHALL_criar_com_todas_as_unidades` | pass |
| C2 | `run unit / ✓ RN_ENR_004_WHEN_unidade_ausente_SHALL_preencher_mesmo_de_evento_antigo` | pass |
| C3 | `run unit / ✓ RN_ENR_004_WHEN_evento_estritamente_mais_novo_SHALL_sobrescrever` | pass |
| C3 | `run unit / ✓ RN_ENR_004_IF_empate_ou_evento_anterior_THEN_SHALL_manter_o_gravado` | pass |
| C4 | `run unit / ✓ RN_ENR_004_IF_origem_provedor_THEN_SHALL_nao_sobrescrever_cliente` | pass |
| C4 | `run unit / ✓ RN_ENR_004_IF_origem_provedor_THEN_SHALL_preencher_lacuna_e_provedor` | pass |
| C5 | `run unit / ✓ RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_lancar` | pass |
| C5 | `run unit / ✓ RN_ENR_004_WHEN_evento_traz_exatamente_N_SHALL_aceitar` | pass |
| C5 | `run unit / ✓ RN_ENR_004_IF_origem_provedor_THEN_limiar_nao_se_aplica` | pass |
| C5 | `run unit / ✓ RN_ENR_004_WHEN_cadastro_tem_apto_SHALL_nao_contar_apto_no_limiar` | pass |
| C6 | `run unit / ✓ RN_ENR_004_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir` | pass |
| C7 | `run unit / ✓ RN_ENR_004_WHEN_cadastro_muda_SHALL_emitir_um_ClienteAtualizado_v1` | pass |
| C7 | `run int / ✓ should publish one ClienteAtualizado v1 per real change, none otherwise` | pass |
| C8 | `run unit / ✓ RN_ENR_004_WHEN_cliente_reafirma_valor_de_provedor_SHALL_anotar_cliente_sem_emitir` | pass |
| C8 | `run unit / ✓ RN_ENR_004_IF_provedor_traz_valor_igual_THEN_SHALL_nao_reanotar` | pass |
| C8 | `run int / ✓ should store a client reaffirmation with a new version and publish nothing` | pass |
| Build | `npm run gate` | pass |

## Output

`Run unit` - exit 0

```
    ✓ RN_ENR_004_IF_empate_ou_evento_anterior_THEN_SHALL_manter_o_gravado (1 ms)
    ✓ RN_ENR_004_IF_origem_provedor_THEN_SHALL_nao_sobrescrever_cliente (1 ms)
    ✓ RN_ENR_004_IF_origem_provedor_THEN_SHALL_preencher_lacuna_e_provedor (1 ms)
    ✓ RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_lancar (1 ms)
    ✓ RN_ENR_004_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir (1 ms)
    ✓ RN_ENR_004_WHEN_cliente_reafirma_valor_de_provedor_SHALL_anotar_cliente_sem_emitir (1 ms)
    ✓ RN_ENR_004_IF_provedor_traz_valor_igual_THEN_SHALL_nao_reanotar (1 ms)
    ✓ RN_ENR_004_WHEN_cadastro_muda_SHALL_emitir_um_ClienteAtualizado_v1 (1 ms)
    ✓ RN_ENR_004_WHEN_so_apto_muda_SHALL_tratar_como_unidade_e_emitir (2 ms)

Test Suites: 8 skipped, 1 passed, 1 of 9 total
Tests:       25 skipped, 16 passed, 41 total
Snapshots:   0 total
Time:        1.472 s, estimated 2 s
Ran all test suites with tests matching "RN_ENR_004".
```

`Run int` - exit 0

```
    ✓ should publish one ClienteAtualizado v1 per real change, none otherwise (19 ms)
    ✓ should store a client reaffirmation with a new version and publish nothing (14 ms)
    ✓ should answer 304 when If-None-Match carries the current version (3 ms)
    ✓ should log the ruleId when an event is discarded by a rule (5 ms)

PASS int src/__tests__/integration/contrato.int.test.ts
  Contrato de resposta — GET /v1/clientes/{documento}
    ✓ should answer 200 when the use case returns exactly the contract shape (243 ms)
    ✓ should answer 500 when the response carries a field outside the contract (163 ms)

Test Suites: 3 passed, 3 total
Tests:       14 passed, 14 total
Snapshots:   0 total
Time:        1.837 s, estimated 2 s
Ran all test suites.
```
