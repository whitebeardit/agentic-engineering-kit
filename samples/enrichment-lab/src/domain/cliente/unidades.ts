/** Unidade de merge = campo folha, endereçado por caminho com ponto ("contato.email").
 * Arrays seriam atômicos. */
import type { DadosCadastro } from './interfaces/evento-ingestao';

export type Caminho = string;

export function achatar(dados: DadosCadastro): Map<Caminho, unknown> {
  const saida = new Map<Caminho, unknown>();
  const visitar = (valor: unknown, prefixo: string): void => {
    if (valor !== null && typeof valor === 'object' && !Array.isArray(valor)) {
      for (const [k, v] of Object.entries(valor as Record<string, unknown>)) {
        visitar(v, prefixo ? `${prefixo}.${k}` : k);
      }
      return;
    }
    if (valor !== undefined) saida.set(prefixo, valor);
  };
  visitar(dados, '');
  return saida;
}

export function aninhar(unidades: Map<Caminho, unknown>): Record<string, unknown> {
  const raiz: Record<string, unknown> = {};
  for (const [caminho, valor] of unidades) {
    const partes = caminho.split('.');
    let atual = raiz;
    for (let i = 0; i < partes.length - 1; i++) {
      const parte = partes[i] as string;
      atual[parte] ??= {};
      atual = atual[parte] as Record<string, unknown>;
    }
    atual[partes[partes.length - 1] as string] = valor;
  }
  return raiz;
}
