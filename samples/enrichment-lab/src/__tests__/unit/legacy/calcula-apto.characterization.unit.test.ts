import { faker } from '@faker-js/faker';
import { calculaApto, PESOS } from '../../../../legacy/calcula-apto';

/**
 * Characterization test: congela o comportamento ATUAL do legado com dados aleatórios
 * de semente fixa.
 * O snapshot em __snapshots__/ é o baseline aprovado por um humano (`npm run
 * baseline`). Mudou? É mudança
 * de comportamento — explique no PR. `npm test` roda com --ci: sem baseline ele FALHA e
 * não grava nada.
 *
 * Reprodutibilidade: a semente fixa vale para a versão do Faker do lockfile (`npm ci`).
 * A doc do Faker avisa que uma versão nova pode gerar valores diferentes para a mesma
 * semente — atualizar o Faker é mudança explícita, com baseline revisto por humano.
 *
 * O segundo bloco não é aleatório: são casos escolhidos à mão nos cortes do legado
 * (37 e 62), no multiplicador de PJ, nos descontos e no bônus de UF, com o rótulo
 * OBSERVADO em 2026-09-09 como oráculo. Ele não precisa de baseline; se um corte
 * mudar, o nome do caso diz qual.
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

  it('congela os cortes: 37 e 62, PJ x1,15, provedor -6, hotmail/bol -3, AM/RR +2,5', () => {
    const todos: Record<string, unknown> = {
      'cadastro.nome': 'x',
      'cadastro.canalEntrada': 'x',
      'contato.email': 'c@exemplo.test',
      'contato.telefone': 'x',
      'endereco.cep': 'x',
      'endereco.cidade': 'x',
      'endereco.uf': 'SP',
    };
    const sem = (...chaves: string[]) => {
      const c = { ...todos };
      for (const k of chaves) delete c[k];
      return c;
    };
    const casos: [
      string,
      Record<string, unknown>,
      'F' | 'J',
      string | undefined,
      string,
    ][] = [
      ['todos os campos, PF (63)', todos, 'F', undefined, 'APTO'],
      [
        'sem uf, PF (61): abaixo do corte de 62',
        sem('endereco.uf'),
        'F',
        undefined,
        'REVISAR',
      ],
      [
        '54 pontos, PF',
        sem('contato.telefone', 'endereco.uf'),
        'F',
        undefined,
        'REVISAR',
      ],
      [
        'os mesmos 54, PJ (54 x 1,15 = 62,1)',
        sem('contato.telefone', 'endereco.uf'),
        'J',
        undefined,
        'APTO',
      ],
      [
        '37 exato, PF: no corte',
        sem('contato.email', 'endereco.cep', 'endereco.cidade', 'endereco.uf'),
        'F',
        undefined,
        'REVISAR',
      ],
      [
        '36, PF: abaixo do corte de 37',
        sem('contato.email', 'contato.telefone', 'endereco.cep'),
        'F',
        undefined,
        'INAPTO',
      ],
      [
        '63 com e-mail hotmail (-3)',
        { ...todos, 'contato.email': 'a@hotmail.com' },
        'F',
        undefined,
        'REVISAR',
      ],
      ['63 com origem provedor (-6)', todos, 'F', 'provedor:birô', 'REVISAR'],
      ['63 com origem cliente:app (sem desconto)', todos, 'F', 'cliente:app', 'APTO'],
      [
        '59 com uf AM (+2,5 = 61,5)',
        { ...sem('endereco.cidade'), 'endereco.uf': 'AM' },
        'F',
        undefined,
        'REVISAR',
      ],
      [
        '54, PJ e provedor: multiplica antes de subtrair (62,1 - 6)',
        sem('contato.telefone', 'endereco.uf'),
        'J',
        'provedor:birô',
        'REVISAR',
      ],
      ['vazio', {}, 'F', undefined, 'INAPTO'],
      [
        'string vazia e null nao contam',
        {
          'cadastro.nome': null,
          'cadastro.canalEntrada': '',
          'contato.email': 'c@exemplo.test',
        },
        'F',
        undefined,
        'INAPTO',
      ],
    ];
    for (const [nome, campos, tipo, origem, esperado] of casos) {
      expect({ nome, saida: calculaApto(campos, tipo, origem) }).toEqual({
        nome,
        saida: esperado,
      });
    }
  });
});
