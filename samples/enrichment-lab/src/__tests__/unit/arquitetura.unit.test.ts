import { spawnSync } from 'node:child_process';
import path from 'node:path';

// As regras vivem em .dependency-cruiser.cjs; aqui cada ADR vira um teste com nome,
// para o vermelho aparecer
// no `npm test` com a mensagem do ADR — igual a qualquer outro sensor. A CLI roda uma
// vez por arquivo de teste.
interface Violacao {
  from: string;
  to: string;
  rule: { name: string; severity: string };
}

const raiz = path.join(__dirname, '..', '..', '..');
let violacoes: Violacao[] = [];

beforeAll(() => {
  const cli = path.join(raiz, 'node_modules', '.bin', 'depcruise');
  const r = spawnSync(
    cli,
    ['src', '--config', '.dependency-cruiser.cjs', '--output-type', 'json'],
    { cwd: raiz, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 },
  );
  if (!r.stdout) throw new Error(`depcruise não produziu saída: ${r.stderr}`);
  const saida = JSON.parse(r.stdout) as { summary: { violations: Violacao[] } };
  violacoes = saida.summary.violations;
});

const das = (regra: string) =>
  violacoes.filter((v) => v.rule.name === regra).map((v) => `${v.from} → ${v.to}`);

describe('Arquitetura (dependency-cruiser)', () => {
  it('ADR-0003: src/domain não depende de nada fora do domínio', () => {
    expect(das('adr-0003-domain-puro')).toEqual([]);
  });
  it('ADR-0003: src/application não depende de infrastructure nem interfaces', () => {
    expect(das('adr-0003-application-sem-infra')).toEqual([]);
  });
  it('ADR-0004: só o domínio lança DomainRuleViolation', () => {
    expect(das('adr-0004-violation-so-no-domain')).toEqual([]);
  });
});
