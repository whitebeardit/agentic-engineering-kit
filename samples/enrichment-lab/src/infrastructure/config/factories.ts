import type { EventoIngestao } from '../../domain/cliente/interfaces/evento-ingestao';
import type { BlacklistConfig } from '../../domain/cliente/service/guardas';
import { IngerirEventoHandler } from '../../application/ingerir-evento.handler';
import { ConsultarCliente } from '../../application/consultar-cliente';
import { ClienteRepositoryMemoria } from '../memory/cliente.memoria';
import { FilaMemoria } from '../memory/fila.memory';
import { PublicadorMemoria } from '../memory/publicador.memoria';
import { EventoIngestaoWorker } from '../messaging/worker';
import { Logger } from '../telemetry/logger';
import { lerEnv, type Env } from './env';

/** Composition root: o único lugar que conhece as implementações (ADR-0003). */
export interface Servicos {
  env: Env;
  log: Logger;
  repo: ClienteRepositoryMemoria;
  fila: FilaMemoria<EventoIngestao>;
  publicador: PublicadorMemoria;
  ingerir: IngerirEventoHandler;
  consultar: ConsultarCliente;
  worker: EventoIngestaoWorker;
}

export const BLACKLIST_PADRAO: BlacklistConfig = {
  global: ['N/A', 'NAO INFORMADO', '-'],
  porCaminho: { 'contato.email': ['nao@informado.com', 'sem@email.com'] },
};

export function criarServicos(
  fonteEnv: NodeJS.ProcessEnv = process.env,
  escreverLog?: (linha: string) => void,
): Servicos {
  const env = lerEnv(fonteEnv);
  const log = new Logger(env.logNivel, escreverLog);
  const repo = new ClienteRepositoryMemoria();
  const fila = new FilaMemoria<EventoIngestao>();
  const publicador = new PublicadorMemoria();
  return {
    env,
    log,
    repo,
    fila,
    publicador,
    ingerir: new IngerirEventoHandler(fila),
    consultar: new ConsultarCliente(repo),
    worker: new EventoIngestaoWorker(
      fila,
      repo,
      BLACKLIST_PADRAO,
      publicador,
      env.limiarN,
      log,
    ),
  };
}
