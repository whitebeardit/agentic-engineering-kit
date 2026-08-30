import type { Request, Response } from 'express';
import type { IngerirEventoHandler } from '../../../application/ingerir-evento.handler';
import { validarEvento } from '../../../infrastructure/contracts/validador-evento';

export function publicarEvento(ingerir: IngerirEventoHandler) {
  return async (req: Request, res: Response): Promise<void> => {
    const evento = validarEvento(req.body); // 400 se fora do schema 2.1
    const aceito = await ingerir.executar(evento, res.locals.cid as string);
    res.status(202).json(aceito);
  };
}
