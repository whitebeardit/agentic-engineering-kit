import { inferirApto } from '../../domain/cliente/service/apto';
import { eventoValido } from '../helpers/eventos';

describe('RN-ENR-006 — Aptidão inferida pelo legado', () => {
  it('RN_ENR_006_IF_evento_sem_apto_THEN_SHALL_inferir_pelo_legado', () => {
    const completo = inferirApto(eventoValido()); // nome, canal, email, telefone, cep, cidade, uf
    expect(completo.apto).toBe(true);
    const magro = inferirApto(
      eventoValido({ data: { contato: { telefone: '11999990000' } } }),
    );
    expect(magro.apto).toBe(false);
  });
  it('RN_ENR_006_WHEN_evento_declara_apto_SHALL_manter_o_declarado', () => {
    expect(inferirApto(eventoValido({ apto: false })).apto).toBe(false);
  });
});
