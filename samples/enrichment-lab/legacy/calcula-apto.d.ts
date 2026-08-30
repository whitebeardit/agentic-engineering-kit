/** Fronteira tipada do legado: o .js não é type-checked (rampa); este arquivo é o
 * contrato que o TypeScript enxerga. */
export type Aptidao = 'APTO' | 'REVISAR' | 'INAPTO';
export function calculaApto(
  campos: Record<string, unknown>,
  tipoPessoa: 'F' | 'J',
  origem?: string,
): Aptidao;
export const PESOS: Record<string, number>;
