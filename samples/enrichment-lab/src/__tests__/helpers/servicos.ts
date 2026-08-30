import { criarServicos, type Servicos } from '../../infrastructure/config/factories';

/** Serviços com log capturado (nada no stdout do jest) e store limpo por chamada. */
export function servicosDeTeste(
  env: NodeJS.ProcessEnv = {},
): Servicos & { linhasDeLog: string[] } {
  const linhasDeLog: string[] = [];
  const s = criarServicos({ LOG_NIVEL: 'debug', ...env }, (l) => linhasDeLog.push(l));
  s.repo.limpar();
  s.fila.limpar();
  return { ...s, linhasDeLog };
}
