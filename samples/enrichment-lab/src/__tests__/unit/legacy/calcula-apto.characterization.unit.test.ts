import { faker } from '@faker-js/faker';
import { calculaApto, PESOS } from '../../../../legacy/calcula-apto';

/**
 * Characterization test: congela o comportamento ATUAL do legado com dados aleatórios
 * de semente fixa.
 * O snapshot em __snapshots__/ é o baseline aprovado por um humano (`npm run
 * baseline`). Mudou? É mudança
 * de comportamento — explique no PR. `npm test` roda com --ci: sem baseline ele FALHA e
 * não grava nada.
 */
describe('Legado — calcula-apto (characterization)', () => {
  it('congela o comportamento atual da pontuacao de aptidao', () => {
    faker.seed(20260827);
    const caminhos = Object.keys(PESOS);
    const casos = Array.from({ length: 60 }, (_, i) => {
      const campos: Record<string, unknown> = {};
      for (const c of caminhos) {
        if (faker.datatype.boolean(0.65)) {
          campos[c] =
            c === 'contato.email'
              ? faker.helpers.arrayElement([
                  'a@hotmail.com',
                  'b@bol.com.br',
                  'c@exemplo.test',
                ])
              : c === 'endereco.uf'
                ? faker.helpers.arrayElement(['SP', 'RJ', 'AM', 'RR', 'BA'])
                : faker.string.alpha(6);
        }
      }
      const tipoPessoa = faker.helpers.arrayElement(['F', 'J'] as const);
      const origem = faker.helpers.arrayElement([
        'cliente:app',
        'provedor:birô',
        undefined,
      ]);
      return {
        caso: i + 1,
        campos,
        tipoPessoa,
        origem,
        saida: calculaApto(campos, tipoPessoa, origem),
      };
    });
    expect(casos).toMatchSnapshot();
  });
});
