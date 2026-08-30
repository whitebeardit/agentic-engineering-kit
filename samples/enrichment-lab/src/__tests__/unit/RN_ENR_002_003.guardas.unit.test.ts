import { aplicarGuardas } from '../../domain/cliente/service/guardas';
import { DomainRuleViolation } from '../../domain/errors/domain-rule-violation';
import { BLACKLIST_PADRAO } from '../../infrastructure/config/factories';
import { eventoValido } from '../helpers/eventos';

const repoQueJaViu = (ids: string[]) => ({
  jaProcessado: async (id: string) => ids.includes(id),
});

describe('RN-ENR-002 — Idempotência por eventId', () => {
  it('RN_ENR_002_IF_eventId_ja_processado_THEN_SHALL_devolver_duplicado', async () => {
    const evento = eventoValido();
    const r = await aplicarGuardas(
      evento,
      repoQueJaViu([evento.eventId]),
      BLACKLIST_PADRAO,
    );
    expect(r).toEqual({ ok: false, motivo: 'duplicado' });
  });
  it('RN_ENR_002_WHEN_eventId_novo_SHALL_seguir_para_as_outras_guardas', async () => {
    const r = await aplicarGuardas(eventoValido(), repoQueJaViu([]), BLACKLIST_PADRAO);
    expect(r.ok).toBe(true);
  });
});

describe('RN-ENR-003 — Blacklist', () => {
  it('RN_ENR_003_WHEN_valor_global_proibido_SHALL_remover_so_a_unidade', async () => {
    const evento = eventoValido({
      data: { cadastro: { nome: 'N/A' }, contato: { email: 'ana@exemplo.test' } },
    });
    const r = await aplicarGuardas(evento, repoQueJaViu([]), BLACKLIST_PADRAO);
    expect(r.ok && r.evento.data).toEqual({ contato: { email: 'ana@exemplo.test' } });
  });
  it('RN_ENR_003_WHEN_valor_proibido_no_caminho_SHALL_remover_o_caminho', async () => {
    const evento = eventoValido({
      data: { contato: { email: 'nao@informado.com', telefone: '11999990000' } },
    });
    const r = await aplicarGuardas(evento, repoQueJaViu([]), BLACKLIST_PADRAO);
    expect(r.ok && r.evento.data).toEqual({ contato: { telefone: '11999990000' } });
  });
  it('RN_ENR_003_IF_nao_sobra_unidade_THEN_SHALL_recusar_com_ruleId', async () => {
    const evento = eventoValido({ data: { cadastro: { nome: '-' } } });
    await expect(
      aplicarGuardas(evento, repoQueJaViu([]), BLACKLIST_PADRAO),
    ).rejects.toMatchObject({
      ruleId: 'RN-ENR-003',
      motivo: 'descartado-blacklist',
    } satisfies Partial<DomainRuleViolation>);
  });
});
