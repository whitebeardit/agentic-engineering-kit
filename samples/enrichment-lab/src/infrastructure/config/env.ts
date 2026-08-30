import type { Nivel } from '../telemetry/logger';

/** Fail-fast: valor inválido derruba o processo no boot, não na primeira mensagem. */
export interface Env {
  port: number;
  limiarN: number;
  logNivel: Nivel;
}

export function lerEnv(fonte: NodeJS.ProcessEnv = process.env): Env {
  const port = Number(fonte.PORT ?? 3000);
  const limiarN = Number(fonte.LIMIAR_N ?? 11);
  const logNivel = (fonte.LOG_NIVEL ?? 'info') as Nivel;
  if (!Number.isInteger(port) || port <= 0)
    throw new Error(`PORT inválida: ${fonte.PORT}`);
  if (!Number.isInteger(limiarN) || limiarN <= 0)
    throw new Error(`LIMIAR_N inválido: ${fonte.LIMIAR_N}`);
  if (!['debug', 'info', 'warn', 'error'].includes(logNivel)) {
    throw new Error(`LOG_NIVEL inválido: ${fonte.LOG_NIVEL}`);
  }
  return { port, limiarN, logNivel };
}
