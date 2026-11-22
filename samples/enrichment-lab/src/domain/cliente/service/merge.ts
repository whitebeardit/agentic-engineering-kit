import type { Unidade } from '../cliente.entity';
import { ehProvedor, type EventoIngestao } from '../interfaces/evento-ingestao';
import { achatar, type Caminho } from '../unidades';

export interface ResultadoMerge {
  unidades: Map<Caminho, Unidade>;
  changed: boolean;
  /** ING-08: só a anotação mudou (valor igual, origem passou a ser o cliente). */
  reanotado: boolean;
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
 * anotação);
 * - ING-08: valor idêntico vindo do cliente sobre unidade escrita por provedor passa
 * a anotação para o cliente (`reanotado`), sem contar como mudança.
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
  let reanotado = false;
  for (const [caminho, valor] of entrada) {
    const atual = unidades.get(caminho);
    if (atual) {
      const maisNovo = instante(evento.updatedAt) > instante(atual.instante);
      if (igual(atual.valor, valor)) {
        if (!provedor && ehProvedor(atual.origem)) {
          unidades.set(caminho, {
            valor: atual.valor,
            instante: maisNovo ? evento.updatedAt : atual.instante,
            origem: evento.origin,
          });
          reanotado = true;
        }
        continue;
      }
      const podeSobrescrever = maisNovo && (!provedor || ehProvedor(atual.origem));
      if (!podeSobrescrever) continue;
    }
    unidades.set(caminho, { valor, instante: evento.updatedAt, origem: evento.origin });
    changed = true;
  }
  return { unidades, changed, reanotado };
}
