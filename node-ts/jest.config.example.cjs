// Dois projetos, dois sufixos. Um arquivo fora do padrão de nome simplesmente não roda
// (enforcement por exclusão).
const base = {
  testEnvironment: 'node',
  transform: { '^.+\\.ts$': ['ts-jest', { tsconfig: 'tsconfig.json' }] },
  moduleFileExtensions: ['ts', 'js', 'json'],
};
module.exports = {
  projects: [
    { ...base, displayName: 'unit', testRegex: '.*\\.unit\\.test\\.ts$' },
    { ...base, displayName: 'int', testRegex: '.*\\.int\\.test\\.ts$' },
  ],
};
