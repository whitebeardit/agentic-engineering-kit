/** Regras de arquitetura — cada uma cita o ADR e diz como corrigir. Rodam dentro do
 * `npm
 * test`
 *  (src/__tests__/unit/arquitetura.unit.test.ts) para o agente ler a falha no mesmo
 * lugar dos outros testes. */
module.exports = {
  forbidden: [
    {
      name: 'adr-0003-domain-puro',
      severity: 'error',
      comment:
        'ADR-0003: src/domain não importa application, infrastructure nem interfaces. ' +
        'Defina uma porta (interface) no domínio e implemente fora.',
      from: { path: '^src/domain' },
      to: { path: '^src/(application|infrastructure|interfaces)' },
    },
    {
      name: 'adr-0003-application-sem-infra',
      severity: 'error',
      comment:
        'ADR-0003: src/application só orquestra e depende só de src/domain. ' +
        'Receba a implementação pela fábrica (src/infrastructure/config/factories.ts).',
      from: { path: '^src/application' },
      to: { path: '^src/(infrastructure|interfaces)' },
    },
    {
      name: 'adr-0004-violation-so-no-domain',
      severity: 'error',
      comment:
        'ADR-0004: só o domínio lança DomainRuleViolation. application e interfaces ' +
        'não importam a classe; quem captura é o worker (infrastructure).',
      from: { path: '^src/(application|interfaces)' },
      to: { path: '^src/domain/errors/domain-rule-violation' },
    },
  ],
  options: {
    doNotFollow: { path: 'node_modules' },
    tsPreCompilationDeps: true,
    tsConfig: { fileName: 'tsconfig.json' },
    exclude: { path: '__tests__' },
  },
};
