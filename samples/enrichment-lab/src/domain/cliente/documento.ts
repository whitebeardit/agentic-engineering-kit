import { DomainRuleViolation } from '../errors/domain-rule-violation';
import type { TipoPessoa } from './interfaces/evento-ingestao';

/** RN-ENR-001 — Documento válido: dígitos verificadores de CPF (11) e CNPJ (14). Nada é
 * lido nem comprado antes disto. */
function digito(numeros: number[], pesos: number[]): number {
  const soma = numeros.reduce((acc, n, i) => acc + n * (pesos[i] as number), 0);
  const resto = soma % 11;
  return resto < 2 ? 0 : 11 - resto;
}

export function cpfValido(cpf: string): boolean {
  if (!/^[0-9]{11}$/.test(cpf) || /^(\d)\1{10}$/.test(cpf)) return false;
  const n = [...cpf].map(Number);
  const d1 = digito(n.slice(0, 9), [10, 9, 8, 7, 6, 5, 4, 3, 2]);
  const d2 = digito(n.slice(0, 10), [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]);
  return d1 === n[9] && d2 === n[10];
}

export function cnpjValido(cnpj: string): boolean {
  if (!/^[0-9]{14}$/.test(cnpj) || /^(\d)\1{13}$/.test(cnpj)) return false;
  const n = [...cnpj].map(Number);
  const d1 = digito(n.slice(0, 12), [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]);
  const d2 = digito(n.slice(0, 13), [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]);
  return d1 === n[12] && d2 === n[13];
}

export function exigirDocumentoValido(documento: string, tipoPessoa: TipoPessoa): void {
  const ok = tipoPessoa === 'F' ? cpfValido(documento) : cnpjValido(documento);
  if (!ok) throw new DomainRuleViolation('RN-ENR-001', 'descartado-documento');
}

/** LGPD: nunca logar o documento inteiro. Correlacione por eventId/cid. */
export function mascarar(documento: string): string {
  return `${'*'.repeat(Math.max(0, documento.length - 4))}${documento.slice(-4)}`;
}
