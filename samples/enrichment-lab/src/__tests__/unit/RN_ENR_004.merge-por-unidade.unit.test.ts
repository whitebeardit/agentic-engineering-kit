import { EventoElegivelParaMerge } from '../../domain/cliente/specifications/evento-elegivel-para-merge';
import { clienteComUnidades } from '../helpers/clientes';
import { eventoValido } from '../helpers/eventos';

const N = 11;
const dados = (n: number) => ({
  cadastro: { nome: 'x' },
  contato: n > 1 ? { email: 'a@b.test' } : {},
});

describe('RN-ENR-004 — Aplicar evento ao cadastro: limiar de completude (ING-05)', () => {
  it('RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_recusar', () => {
    const r = EventoElegivelParaMerge.estaSatisfeitaPor(
      clienteComUnidades(N),
      eventoValido({ data: dados(1) }),
      N,
    );
    expect(r).toEqual({ ok: false, motivo: 'descartado-limiar' });
  });
  it('RN_ENR_004_IF_origem_provedor_THEN_limiar_nao_se_aplica', () => {
    const evento = eventoValido({ origin: 'provedor:biro', data: dados(1) });
    expect(
      EventoElegivelParaMerge.estaSatisfeitaPor(clienteComUnidades(N), evento, N),
    ).toEqual({ ok: true });
  });
  it('RN_ENR_004_WHEN_evento_traz_exatamente_N_SHALL_aceitar', () => {
    const cliente = clienteComUnidades(N);
    const evento = eventoValido({ data: dados(1) });
    // boundary: N unidades no evento → aceito; N-1 → recusado
    const comN = {
      ...evento,
      data: Object.fromEntries([...Array(N).keys()].map((i) => [`g${i}`, { v: i }])),
    };
    expect(EventoElegivelParaMerge.estaSatisfeitaPor(cliente, comN, N)).toEqual({
      ok: true,
    });
    expect(
      EventoElegivelParaMerge.estaSatisfeitaPor(clienteComUnidades(N - 1), evento, N),
    ).toEqual({ ok: true });
  });
});
