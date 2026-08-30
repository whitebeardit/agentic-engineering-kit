import {
  cnpjValido,
  cpfValido,
  exigirDocumentoValido,
  mascarar,
} from '../../domain/cliente/documento';
import { DomainRuleViolation } from '../../domain/errors/domain-rule-violation';
import { CNPJ_VALIDO, CPF_VALIDO } from '../helpers/eventos';

describe('RN-ENR-001 — Documento válido', () => {
  it('RN_ENR_001_WHEN_cpf_com_digitos_corretos_SHALL_aceitar', () => {
    expect(cpfValido(CPF_VALIDO)).toBe(true);
  });
  it('RN_ENR_001_WHEN_cnpj_com_digitos_corretos_SHALL_aceitar', () => {
    expect(cnpjValido(CNPJ_VALIDO)).toBe(true);
  });
  it('RN_ENR_001_IF_digito_verificador_errado_THEN_SHALL_recusar_com_ruleId', () => {
    const errado = CPF_VALIDO.slice(0, 10) + (CPF_VALIDO.endsWith('5') ? '6' : '5');
    expect(() => exigirDocumentoValido(errado, 'F')).toThrow(DomainRuleViolation);
    try {
      exigirDocumentoValido(errado, 'F');
    } catch (e) {
      expect((e as DomainRuleViolation).ruleId).toBe('RN-ENR-001');
      expect((e as DomainRuleViolation).motivo).toBe('descartado-documento');
    }
  });
  it('RN_ENR_001_IF_todos_os_digitos_iguais_THEN_SHALL_recusar', () => {
    expect(cpfValido('11111111111')).toBe(false);
    expect(cnpjValido('22222222222222')).toBe(false);
  });
  it('RN_ENR_001_SHALL_mascarar_o_documento_em_qualquer_log', () => {
    expect(mascarar(CPF_VALIDO)).toBe('*******4725');
  });
});
