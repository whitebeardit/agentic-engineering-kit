// Roda os arquivos de teste na ordem inversa da padrão. Serve para expor teste que só passa
// porque outro arquivo rodou antes (dependência de ordem). Uso: npm run test:reverso
const Sequencer = require('@jest/test-sequencer').default;

module.exports = class SequenciadorReverso extends Sequencer {
  sort(tests) {
    return super.sort(tests).reverse();
  }
};
