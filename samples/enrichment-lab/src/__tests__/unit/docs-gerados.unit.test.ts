import { spawnSync } from 'node:child_process';
import path from 'node:path';

/**
 * Casa GERADO: docs/generated/ é derivado do código e dos contratos; ninguém edita
 * à mão (o hook bloqueia) e ninguém deixa envelhecer (este teste bloqueia). Ele
 * roda o gerador em modo --check: gerado desatualizado reprova o gate.
 */
describe('GERADO — docs/generated em dia com o código e os contratos', () => {
  it('tools/gerar-docs.cjs --check sai com 0', () => {
    const raiz = path.resolve(__dirname, '../../..');
    const r = spawnSync(process.execPath, ['tools/gerar-docs.cjs', '--check'], {
      cwd: raiz,
      encoding: 'utf8',
    });
    expect(r.stderr).toBe('');
    expect(r.status).toBe(0);
  });
});
