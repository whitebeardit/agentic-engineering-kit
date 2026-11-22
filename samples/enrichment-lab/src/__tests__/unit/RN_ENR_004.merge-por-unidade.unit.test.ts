import { EventoElegivelParaMerge } from '../../domain/cliente/specifications/evento-elegivel-para-merge';
import { clienteComUnidades } from '../helpers/clientes';
import { eventoValido } from '../helpers/eventos';

const N = 11;
const dados = (n: number) => ({
  cadastro: { nome: 'x' },
  contato: n > 1 ? { email: 'a@b.test' } : {},
});

describe('RN-ENR-004 — limiar de completude (ING-05)', () => {
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
    const comNMenos1 = {
      ...evento,
      data: Object.fromEntries(
        [...Array(N - 1).keys()].map((i) => [`g${i}`, { v: i }]),
      ),
    };
    expect(EventoElegivelParaMerge.estaSatisfeitaPor(cliente, comNMenos1, N)).toEqual({
      ok: false,
      motivo: 'descartado-limiar',
    });
  });
  it('RN_ENR_004_WHEN_cadastro_tem_apto_SHALL_nao_contar_apto_no_limiar', () => {
    const unidades = new Map(clienteComUnidades(N - 1).unidades);
    unidades.set('apto', { valor: true, instante: T12, origem: 'cliente:app' });
    const c = Cliente.reidratar(CPF_VALIDO, 'F', 1, unidades);
    expect(c.quantidadeDeCampos).toBe(N - 1);
    expect(
      EventoElegivelParaMerge.estaSatisfeitaPor(c, eventoValido({ data: dados(1) }), N),
    ).toEqual({ ok: true });
  });
});

import { Cliente } from '../../domain/cliente/cliente.entity';
import { DomainRuleViolation } from '../../domain/errors/domain-rule-violation';
import { CPF_VALIDO } from '../helpers/eventos';

const T12 = '2026-08-30T12:00:00Z';
const T11 = '2026-08-30T11:00:00Z';
const T13 = '2026-08-30T13:00:00Z';
const unidade = (c: Cliente, caminho: string) => c.unidades.get(caminho);

describe('RN-ENR-004 — Aplicar evento ao cadastro: merge por unidade', () => {
  it('RN_ENR_004_WHEN_documento_sem_cadastro_SHALL_criar_com_todas_as_unidades', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    const r = c.aplicar(eventoValido({ updatedAt: T12 }), N);
    expect(r.changed).toBe(true);
    expect(c.quantidadeDeCampos).toBe(7);
    expect(unidade(c, 'contato.email')).toEqual({
      valor: 'ana@exemplo.test',
      instante: T12,
      origem: 'cliente:app',
    });
    for (const u of c.unidades.values())
      expect(u).toMatchObject({ instante: T12, origem: 'cliente:app' });
    expect(r.eventos).toHaveLength(1);
    expect(r.eventos[0]?.versao).toBe(1);
  });
  it('RN_ENR_004_WHEN_unidade_ausente_SHALL_preencher_mesmo_de_evento_antigo', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido({ updatedAt: T12, data: { cadastro: { nome: 'Ana' } } }), N);
    const r = c.aplicar(
      eventoValido({ updatedAt: T11, data: { endereco: { cep: '01001000' } } }),
      N,
    );
    expect(r.changed).toBe(true);
    expect(unidade(c, 'endereco.cep')?.valor).toBe('01001000');
    expect(unidade(c, 'cadastro.nome')?.valor).toBe('Ana');
  });
  it('RN_ENR_004_WHEN_evento_estritamente_mais_novo_SHALL_sobrescrever', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido({ updatedAt: T12, data: { cadastro: { nome: 'Ana' } } }), N);
    const r = c.aplicar(
      eventoValido({ updatedAt: T13, data: { cadastro: { nome: 'Ana Maria' } } }),
      N,
    );
    expect(r.changed).toBe(true);
    expect(unidade(c, 'cadastro.nome')).toEqual({
      valor: 'Ana Maria',
      instante: T13,
      origem: 'cliente:app',
    });
  });
  it('RN_ENR_004_IF_empate_ou_evento_anterior_THEN_SHALL_manter_o_gravado', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido({ updatedAt: T12, data: { cadastro: { nome: 'Ana' } } }), N);
    expect(
      c.aplicar(
        eventoValido({ updatedAt: T12, data: { cadastro: { nome: 'Outra' } } }),
        N,
      ).changed,
    ).toBe(false);
    expect(
      c.aplicar(
        eventoValido({ updatedAt: T11, data: { cadastro: { nome: 'Outra' } } }),
        N,
      ).changed,
    ).toBe(false);
    expect(unidade(c, 'cadastro.nome')?.valor).toBe('Ana');
  });
  it('RN_ENR_004_IF_origem_provedor_THEN_SHALL_nao_sobrescrever_cliente', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido({ updatedAt: T12, data: { cadastro: { nome: 'Ana' } } }), N);
    const provedor = eventoValido({
      origin: 'provedor:biro',
      updatedAt: T13,
      data: { cadastro: { nome: 'ANA S' } },
    });
    expect(c.aplicar(provedor, N).changed).toBe(false);
    expect(unidade(c, 'cadastro.nome')?.valor).toBe('Ana');
  });
  it('RN_ENR_004_IF_origem_provedor_THEN_SHALL_preencher_lacuna_e_provedor', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    const p1 = eventoValido({
      origin: 'provedor:biro',
      updatedAt: T12,
      data: { endereco: { uf: 'SP' } },
    });
    const p2 = eventoValido({
      origin: 'provedor:outro',
      updatedAt: T13,
      data: { endereco: { uf: 'RJ' } },
    });
    expect(c.aplicar(p1, N).changed).toBe(true);
    expect(c.aplicar(p2, N).changed).toBe(true);
    expect(unidade(c, 'endereco.uf')).toEqual({
      valor: 'RJ',
      instante: T13,
      origem: 'provedor:outro',
    });
  });
  it('RN_ENR_004_IF_cadastro_completo_e_evento_incompleto_THEN_SHALL_lancar', () => {
    const c = clienteComUnidades(N);
    const antes = c.versao;
    let erro: unknown;
    try {
      c.aplicar(eventoValido({ data: dados(1) }), N);
    } catch (e) {
      erro = e;
    }
    expect(erro).toBeInstanceOf(DomainRuleViolation);
    expect(erro).toMatchObject({ ruleId: 'RN-ENR-004', motivo: 'descartado-limiar' });
    expect(c.versao).toBe(antes);
    expect(c.quantidadeDeCampos).toBe(N);
  });
  it('RN_ENR_004_IF_estado_identico_THEN_SHALL_nao_mudar_nem_emitir', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido({ updatedAt: T12 }), N);
    // mesmos valores, evento mais novo
    const r = c.aplicar(eventoValido({ updatedAt: T13 }), N);
    expect(r).toEqual({ changed: false, eventos: [] });
    expect(unidade(c, 'cadastro.nome')?.instante).toBe(T12); // anotação não renova
  });
  it('RN_ENR_004_WHEN_cliente_reafirma_valor_de_provedor_SHALL_anotar_cliente_sem_emitir', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    const uf = (origin: 'provedor:biro' | 'cliente:app', updatedAt: string, v: string) =>
      eventoValido({ origin, updatedAt, data: { endereco: { uf: v } } });
    c.aplicar(uf('provedor:biro', T12, 'SP'), N);
    const r = c.aplicar(uf('cliente:app', T13, 'SP'), N);
    expect(r).toEqual({ changed: false, eventos: [], reanotado: true });
    expect(unidade(c, 'endereco.uf')).toEqual({
      valor: 'SP',
      instante: T13,
      origem: 'cliente:app',
    });
    // provedor mais novo já não sobrescreve
    const T14 = '2026-08-30T14:00:00Z';
    expect(c.aplicar(uf('provedor:biro', T14, 'RJ'), N).changed).toBe(false);
    expect(unidade(c, 'endereco.uf')?.valor).toBe('SP');
    // reafirmação mais antiga que o gravado: a origem passa, o instante fica
    const d = Cliente.novo(CPF_VALIDO, 'F');
    d.aplicar(uf('provedor:biro', T12, 'SP'), N);
    d.aplicar(uf('cliente:app', T11, 'SP'), N);
    expect(unidade(d, 'endereco.uf')).toEqual({
      valor: 'SP',
      instante: T12,
      origem: 'cliente:app',
    });
  });
  it('RN_ENR_004_IF_provedor_traz_valor_igual_THEN_SHALL_nao_reanotar', () => {
    const uf = (origin: 'provedor:biro' | 'provedor:outro' | 'cliente:app', at: string) =>
      eventoValido({ origin, updatedAt: at, data: { endereco: { uf: 'SP' } } });
    // sobre unidade de provedor
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(uf('provedor:biro', T12), N);
    expect(c.aplicar(uf('provedor:outro', T13), N)).toEqual({
      changed: false,
      eventos: [],
    });
    expect(unidade(c, 'endereco.uf')).toEqual({
      valor: 'SP',
      instante: T12,
      origem: 'provedor:biro',
    });
    // sobre unidade de cliente
    const d = Cliente.novo(CPF_VALIDO, 'F');
    d.aplicar(uf('cliente:app', T12), N);
    expect(d.aplicar(uf('provedor:biro', T13), N)).toEqual({
      changed: false,
      eventos: [],
    });
    expect(unidade(d, 'endereco.uf')).toEqual({
      valor: 'SP',
      instante: T12,
      origem: 'cliente:app',
    });
  });
  it('RN_ENR_004_WHEN_cadastro_muda_SHALL_emitir_um_ClienteAtualizado_v1', () => {
    const c = Cliente.reidratar(CPF_VALIDO, 'F', 3, new Map());
    const r = c.aplicar(eventoValido({ updatedAt: T12 }), N);
    expect(r.eventos).toHaveLength(1);
    expect(r.eventos[0]).toMatchObject({
      type: 'ClienteAtualizado',
      version: 1,
      documento: CPF_VALIDO,
      versao: 4,
    });
    const occurredAt = r.eventos[0]?.occurredAt ?? '';
    expect(occurredAt).toBe(new Date(occurredAt).toISOString());
  });
  it('RN_ENR_004_WHEN_so_apto_muda_SHALL_tratar_como_unidade_e_emitir', () => {
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido({ updatedAt: T12, apto: false }), N);
    const r = c.aplicar(eventoValido({ updatedAt: T13, apto: true }), N);
    expect(r.changed).toBe(true);
    expect(c.apto).toBe(true);
    expect(c.snapshot()).not.toHaveProperty('apto');
  });
});
