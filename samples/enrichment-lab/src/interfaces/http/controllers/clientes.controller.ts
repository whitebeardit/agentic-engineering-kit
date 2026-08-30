import type { Request, Response } from 'express';
import type { ConsultarCliente } from '../../../application/consultar-cliente';

export function consultarCliente(consultar: ConsultarCliente) {
  return async (req: Request, res: Response): Promise<void> => {
    const cliente = await consultar.executar(req.params.documento as string);
    const etag = `"v${cliente.versao}"`;
    res.set('ETag', etag);
    if (req.get('If-None-Match') === etag) {
      res.status(304).end();
      return;
    }
    res.status(200).json(cliente);
  };
}
