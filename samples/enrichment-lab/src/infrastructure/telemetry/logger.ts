/** Logger JSON de 30 linhas: uma linha por evento, sempre com trace_id e cid. Nunca um
 * documento inteiro. */
export type Nivel = 'debug' | 'info' | 'warn' | 'error';
const ordem: Record<Nivel, number> = { debug: 10, info: 20, warn: 30, error: 40 };

export interface Contexto {
  trace_id?: string;
  cid?: string;
  [chave: string]: unknown;
}

export class Logger {
  constructor(
    private readonly nivelMinimo: Nivel = 'info',
    private readonly escrever: (linha: string) => void = (l) =>
      process.stdout.write(`${l}\n`),
  ) {}

  private emitir(nivel: Nivel, msg: string, ctx: Contexto): void {
    if (ordem[nivel] < ordem[this.nivelMinimo]) return;
    this.escrever(JSON.stringify({ ts: new Date().toISOString(), nivel, msg, ...ctx }));
  }
  debug(msg: string, ctx: Contexto = {}): void {
    this.emitir('debug', msg, ctx);
  }
  info(msg: string, ctx: Contexto = {}): void {
    this.emitir('info', msg, ctx);
  }
  warn(msg: string, ctx: Contexto = {}): void {
    this.emitir('warn', msg, ctx);
  }
  error(msg: string, ctx: Contexto = {}): void {
    this.emitir('error', msg, ctx);
  }
}
