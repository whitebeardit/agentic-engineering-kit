import { Cliente } from '../../domain/cliente/cliente.entity';
import { ConflictError } from '../../domain/errors/domain-error';
import { ClienteRepositoryMemoria } from '../../infrastructure/memory/cliente.memoria';
import { CPF_VALIDO, eventoValido } from '../helpers/eventos';
import { servicosDeTeste } from '../helpers/servicos';

describe('RN-ENR-005 — Gravação condicional por versão', () => {
  it('RN_ENR_005_WHEN_documento_novo_SHALL_gravar_esperando_versao_zero', async () => {
    const repo = new ClienteRepositoryMemoria();
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido(), 11);
    await expect(repo.gravar(c, 0)).resolves.toBe(1);
  });
  it('RN_ENR_005_IF_versao_persistida_mudou_THEN_SHALL_lancar_conflito', async () => {
    const repo = new ClienteRepositoryMemoria();
    const c = Cliente.novo(CPF_VALIDO, 'F');
    c.aplicar(eventoValido(), 11);
    await repo.gravar(c, 0);
    await expect(repo.gravar(c, 0)).rejects.toBeInstanceOf(ConflictError);
    expect((await repo.obter(CPF_VALIDO))?.versao).toBe(1);
  });
  it('RN_ENR_005_WHEN_conflito_THEN_worker_SHALL_reler_e_refazer', async () => {
    const s = servicosDeTeste();
    const original = s.repo.gravar.bind(s.repo);
    let interferiu = false;
    jest.spyOn(s.repo, 'gravar').mockImplementation(async (cliente, versaoEsperada) => {
      if (!interferiu) {
        interferiu = true; // alguém gravou entre a leitura e a escrita
        const outro = Cliente.novo(cliente.documento, cliente.tipoPessoa);
        outro.aplicar(
          eventoValido({ data: { cadastro: { nome: 'Outro Processo' } } }),
          11,
        );
        await original(outro, 0);
      }
      return original(cliente, versaoEsperada);
    });
    await s.ingerir.executar(eventoValido(), 'cid-teste');
    await expect(s.worker.processarPendentes()).resolves.toEqual(['gravado']);
    expect((await s.repo.obter(CPF_VALIDO))?.versao).toBe(2);
  });
  it('RN_ENR_005_IF_falha_tecnica_persiste_THEN_SHALL_ir_para_dlq', async () => {
    const s = servicosDeTeste();
    jest.spyOn(s.repo, 'gravar').mockRejectedValue(new Error('store fora do ar'));
    await s.ingerir.executar(eventoValido(), 'cid-teste');
    // A fila em memória reentrega na hora (sem visibility timeout): cinco recebimentos
    // numa passada só.
    await expect(s.worker.processarPendentes()).resolves.toEqual(
      Array<string>(5).fill('retry'),
    );
    expect(s.fila.dlq).toHaveLength(1);
    expect(s.fila.tamanho).toBe(0);
  });
});
