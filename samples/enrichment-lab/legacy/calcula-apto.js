// calcula-apto.js — 2015. Pontuação de "aptidão" do cadastro, usada quando o evento não
// diz se o cliente está apto.
// Ninguém explica os pesos nem os cortes (37 e 62). Antes de qualquer refactor, o
// characterization test em
// src/__tests__/unit/legacy/ congela o que isto faz hoje — o que faz, não o que
// deveria.
var PESOS = {
  'cadastro.nome': 17,
  'cadastro.canalEntrada': 13,
  'contato.email': 9,
  'contato.telefone': 7,
  'endereco.cep': 11,
  'endereco.cidade': 4,
  'endereco.uf': 2,
};

function calculaApto(campos, tipoPessoa, origem) {
  var pontos = 0;
  var i;
  for (i in PESOS) {
    if (campos[i] !== undefined && campos[i] !== null && campos[i] !== '') {
      pontos = pontos + PESOS[i];
    }
  }
  if (tipoPessoa == 'J') {
    pontos = pontos * 1.15;
  }
  if (origem && origem.indexOf('provedor:') === 0) {
    pontos = pontos - 6;
  }
  if (campos['contato.email'] && /@(hotmail|bol)\./.test(campos['contato.email'])) {
    pontos = pontos - 3;
  }
  if (campos['endereco.uf'] == 'AM' || campos['endereco.uf'] == 'RR') {
    pontos = pontos + 2.5;
  }
  if (pontos >= 62) return 'APTO';
  if (pontos >= 37) return 'REVISAR';
  return 'INAPTO';
}

module.exports = { calculaApto: calculaApto, PESOS: PESOS };
