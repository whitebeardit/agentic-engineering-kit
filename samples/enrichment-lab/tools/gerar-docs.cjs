#!/usr/bin/env node
// Casa GERADO: o que dá para gerar não se escreve. Este script escreve os três
// inventários de docs/generated/ a partir do código e dos contratos, com saída
// determinística (ordenada, sem data/hora). `--check` regenera em memória e falha
// se o que está no disco divergir — é o gate: gerado desatualizado reprova.
//   deps.md      ← src/ pelo dependency-cruiser (mesmo config do teste de arquitetura)
//   endpoints.md ← src/contracts/service.yaml (OpenAPI)
//   eventos.md   ← src/contracts/asyncapi.yaml (AsyncAPI)
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const yaml = require('js-yaml');

const RAIZ = path.resolve(__dirname, '..');
const SAIDA = path.join(RAIZ, 'docs', 'generated');
const check = process.argv.includes('--check');

const cabecalho = (fonte) =>
  `<!-- gerado por tools/gerar-docs.cjs a partir de ${fonte} — não edite à mão; ` +
  `rode \`npm run generate\` -->\n\n`;

function camada(arquivo) {
  const m = /^src\/([^/]+)\//.exec(arquivo);
  if (m) return m[1];
  if (arquivo.startsWith('legacy/')) return 'legacy';
  return 'outros';
}

function gerarDeps() {
  const bin = path.join(RAIZ, 'node_modules', '.bin', 'depcruise');
  const json = execFileSync(
    bin,
    ['src', '--config', '.dependency-cruiser.cjs', '--output-type', 'json'],
    { cwd: RAIZ, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 },
  );
  const modulos = JSON.parse(json).modules;
  const porCamada = new Map();
  const arestas = new Set();
  for (const m of modulos) {
    const c = camada(m.source);
    if (!porCamada.has(c)) porCamada.set(c, new Set());
    porCamada.get(c).add(m.source);
    for (const d of m.dependencies) {
      if (!d.resolved.startsWith('src/') && !d.resolved.startsWith('legacy/')) continue;
      const cd = camada(d.resolved);
      if (cd !== c) arestas.add(`${m.source} → ${d.resolved}`);
    }
  }
  let out = cabecalho('src/ (dependency-cruiser, .dependency-cruiser.cjs)');
  out += '# Grafo de dependências\n\n## Módulos por camada\n\n';
  for (const c of [...porCamada.keys()].sort()) {
    const lista = [...porCamada.get(c)].sort();
    out += `### ${c} (${lista.length})\n\n`;
    for (const f of lista) out += `- \`${f}\`\n`;
    out += '\n';
  }
  const lista = [...arestas].sort();
  out += `## Arestas entre camadas (${lista.length})\n\n`;
  out += 'Uma linha por importação que cruza camada; a direção permitida é a dos ADRs ';
  out += '(`.dependency-cruiser.cjs`).\n\n';
  for (const a of lista) out += `- \`${a}\`\n`;
  return out;
}

function gerarEndpoints() {
  const doc = yaml.load(fs.readFileSync(path.join(RAIZ, 'src/contracts/service.yaml'), 'utf8'));
  const linhas = [];
  for (const [rota, ops] of Object.entries(doc.paths ?? {})) {
    for (const [metodo, op] of Object.entries(ops)) {
      if (typeof op !== 'object' || !op.responses) continue;
      const codigos = Object.keys(op.responses).sort().join(', ');
      linhas.push(`| ${metodo.toUpperCase()} | \`${rota}\` | \`${op.operationId ?? '—'}\` | ${codigos} |`);
    }
  }
  linhas.sort();
  let out = cabecalho('src/contracts/service.yaml (OpenAPI)');
  out += `# Inventário de endpoints — ${doc.info?.title ?? ''} ${doc.info?.version ?? ''}\n\n`;
  out += '| Método | Path | operationId | Respostas |\n|---|---|---|---|\n';
  out += linhas.join('\n') + '\n\n';
  out += 'Rota fora deste inventário responde 404 (validador de request); `/health` é ';
  out += 'registrado antes do validador e não faz parte do contrato.\n';
  return out;
}

function gerarEventos() {
  const doc = yaml.load(fs.readFileSync(path.join(RAIZ, 'src/contracts/asyncapi.yaml'), 'utf8'));
  const canais = doc.channels ?? {};
  const mensagens = doc.components?.messages ?? {};
  const linhas = [];
  for (const [nomeOp, op] of Object.entries(doc.operations ?? {})) {
    const canalRef = op.channel?.$ref?.split('/').pop();
    const canal = canais[canalRef] ?? {};
    for (const [nomeMsg, ref] of Object.entries(canal.messages ?? {})) {
      const msg = mensagens[ref.$ref?.split('/').pop()] ?? {};
      const req = (msg.payload?.required ?? []).join(', ');
      linhas.push(
        `| \`${canal.address ?? canalRef}\` | ${op.action} (\`${nomeOp}\`) | ` +
          `${msg.name ?? nomeMsg} — ${(msg.title ?? '').trim()} | ${req} |`,
      );
    }
  }
  linhas.sort();
  let out = cabecalho('src/contracts/asyncapi.yaml (AsyncAPI)');
  out += `# Inventário de eventos — ${doc.info?.title ?? ''} ${doc.info?.version ?? ''}\n\n`;
  out += '| Canal | Operação | Mensagem | Campos obrigatórios |\n|---|---|---|---|\n';
  out += linhas.join('\n') + '\n';
  return out;
}

const arquivos = {
  'deps.md': gerarDeps,
  'endpoints.md': gerarEndpoints,
  'eventos.md': gerarEventos,
};

let divergentes = 0;
fs.mkdirSync(SAIDA, { recursive: true });
for (const [nome, gerar] of Object.entries(arquivos)) {
  const alvo = path.join(SAIDA, nome);
  const novo = gerar();
  if (check) {
    const atual = fs.existsSync(alvo) ? fs.readFileSync(alvo, 'utf8') : '';
    if (atual !== novo) {
      divergentes += 1;
      process.stderr.write(
        `gerar-docs --check: docs/generated/${nome} desatualizado\n`,
      );
    }
  } else {
    fs.writeFileSync(alvo, novo);
    process.stdout.write(`gerar-docs: docs/generated/${nome}\n`);
  }
}
if (check) {
  if (divergentes) {
    process.stderr.write(
      'gerar-docs --check: rode `npm run generate` e commite docs/generated/\n',
    );
    process.exit(1);
  }
  process.stdout.write('gerar-docs --check: docs/generated/ em dia\n');
}
