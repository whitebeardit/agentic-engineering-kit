import type { Unidade } from '../cliente.entity';
import { ehProvedor, type EventoIngestao } from '../interfaces/evento-ingestao';
import { achatar, type Caminho } from '../unidades';

export interface ResultadoMerge {
  unidades: Map<Caminho, Unidade>;
  changed: boolean;
}

const igual = (a: unknown, b: unknown): boolean =>
  JSON.stringify(a) === JSON.stringify(b);
const instante = (iso: string): number => Date.parse(iso);

/**
 * RN-ENR-004 (ING-02/03/04/06) — merge por unidade folha. Função pura: não grava, não
 * decide versão.
 * - ausente → entra, mesmo de evento mais antigo;
 * - presente → só se o evento é estritamente mais novo; empate mantém;
 * - origem provedor só preenche lacuna ou sobrescreve unidade escrita por provedor;
 * - `apto` é a unidade "apto"; valor idêntico não conta como mudança (nem renova a
 * anotação).
 */
export function mesclar(
  atuais: Map<Caminho, Unidade>,
  evento: EventoIngestao,
): ResultadoMerge {
  const unidades = new Map(atuais);
  const entrada = achatar(evento.data);
  if (evento.apto !== undefined) entrada.set('apto', evento.apto);
  const provedor = ehProvedor(evento.origin);
  let changed = false;
  for (const [caminho, valor] of entrada) {
    const atual = unidades.get(caminho);
    if (atual) {
      const maisNovo = instante(evento.updatedAt) > instante(atual.instante);
      const podeSobrescrever = maisNovo && (!provedor || ehProvedor(atual.origem));
      if (!podeSobrescrever || igual(atual.valor, valor)) continue;
    }
    unidades.set(caminho, { valor, instante: evento.updatedAt, origem: evento.origin });
    changed = true;
  }
  return { unidades, changed };
}
