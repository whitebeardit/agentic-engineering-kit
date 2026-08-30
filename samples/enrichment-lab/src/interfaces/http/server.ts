import { randomUUID } from 'node:crypto';
import path from 'node:path';
import express, { type NextFunction, type Request, type Response } from 'express';
import * as OpenApiValidator from 'express-openapi-validator';
import type { Servicos } from '../../infrastructure/config/factories';
import { DomainError } from '../../domain/errors/domain-error';
import { consultarCliente } from './controllers/clientes.controller';
import { publicarEvento } from './controllers/eventos.controller';

const CONTRATO = path.join(__dirname, '..', '..', 'contracts', 'service.yaml');

type Handler = (req: Request, res: Response) => Promise<void>;
const capturar =
  (h: Handler) =>
  (req: Request, res: Response, next: NextFunction): void => {
    h(req, res).catch(next);
  };

export function criarApp(s: Servicos): express.Express {
  const app = express();
  app.use(express.json({ limit: '64kb' }));
  app.use((req, res, next) => {
    res.locals.cid = req.get('x-cid') ?? randomUUID();
    next();
  });

  // Rotas operacionais ANTES do validador: não estão no contrato e não devem estar.
  app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
  });

  // Contract-first: request E response validados; rota fora do contrato → 404.
  app.use(
    OpenApiValidator.middleware({
      apiSpec: CONTRATO,
      validateRequests: true,
      validateResponses: true,
    }),
  );

  app.post('/v1/eventos', capturar(publicarEvento(s.ingerir)));
  app.get('/v1/clientes/:documento', capturar(consultarCliente(s.consultar)));

  // Handler central: erro de domínio vira o status dele; erro do validador vira o
  // status do validador.
  app.use((erro: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (erro instanceof DomainError) {
      res
        .status(erro.status)
        .json({ erro: erro.name, mensagem: erro.message, detalhes: erro.detalhes });
      return;
    }
    const e = erro as {
      status?: number;
      message?: string;
      errors?: { message: string; path?: string }[];
    };
    const status = e.status ?? 500;
    s.log.error('erro não tratado', {
      cid: res.locals.cid as string,
      status,
      erro: e.message ?? String(erro),
    });
    res.status(status).json({
      erro: status === 400 ? 'contrato' : 'interno',
      mensagem: e.message ?? 'erro interno',
      detalhes: (e.errors ?? []).map((x) => `${x.path ?? ''} ${x.message}`.trim()),
    });
  });
  return app;
}
