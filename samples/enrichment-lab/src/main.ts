import { criarServicos } from './infrastructure/config/factories';
import { criarApp } from './interfaces/http/server';

// Ordem de boot: env → serviços → http → worker (o serviço real segue a mesma ordem,
// com telemetria antes).
const s = criarServicos();
const app = criarApp(s);
app.listen(s.env.port, () => s.log.info('http no ar', { port: s.env.port }));
setInterval(() => {
  s.worker
    .processarPendentes()
    .catch((e: unknown) => s.log.error('worker falhou', { erro: String(e) }));
}, 250).unref();
