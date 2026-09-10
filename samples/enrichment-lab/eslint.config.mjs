import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';
import globals from 'globals';

export default tseslint.config(
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**'] },
  {
    files: ['**/*.{js,mjs,cjs}'],
    ...js.configs.recommended,
    languageOptions: { globals: globals.node },
    rules: {
      'max-len': ['error', { code: 88, ignoreUrls: true, ignoreStrings: true }],
    },
  },
  {
    files: ['src/**/*.ts', 'legacy/**/*.d.ts'],
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommendedTypeChecked,
      prettier,
    ],
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': 'error',
      eqeqeq: 'error',
      // 88 colunas, comentários inclusive (o prettier não os quebra); imports e
      // strings ficam de fora.
      'max-len': [
        'error',
        {
          code: 88,
          ignoreUrls: true,
          ignoreStrings: true,
          ignoreTemplateLiterals: true,
          ignorePattern: '^\\s*import ',
        },
      ],
    },
  },
  {
    // Adaptadores em memória implementam portas assíncronas sem esperar nada: o `async`
    // é a assinatura da porta.
    files: ['src/infrastructure/memory/**/*.ts', 'src/__tests__/**/*.ts'],
    rules: { '@typescript-eslint/require-await': 'off' },
  },
  {
    files: ['src/__tests__/**/*.ts'],
    rules: {
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-unsafe-call': 'off',
    },
  },
  {
    // Rampa: o legado nasce em `warn`, uma regra por vez sobe para `error`. Cada linha
    // tem dono e data —
    // a severidade se ajusta AQUI, nunca com eslint-disable dentro do arquivo.
    files: ['legacy/**/*.js'],
    languageOptions: { sourceType: 'commonjs', globals: globals.node },
    rules: {
      // dono: tech lead do laboratório (papel, não nome — o kit não leva nomes)
      'no-var': 'warn', // desde 2026-08-30 · vira error em 2026-10-01
      'prefer-const': 'warn', // desde 2026-08-30 · vira error em 2026-10-01
      eqeqeq: 'warn', // desde 2026-08-30 · vira error em 2026-11-02
      'no-redeclare': 'error', // subiu em 2026-08-30: zero ocorrências
      'no-undef': 'error', // sempre foi error: código que referencia o que não existe
    },
  },
);
