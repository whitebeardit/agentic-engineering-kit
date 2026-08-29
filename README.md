# Whitebeard · Agentic Engineering Kit

Como a Whitebeard desenvolve software com agentes de IA — e como implanta e ensina isso em clientes.
É o lado executável do roteiro em 7 fases (vault: `30-Areas/Whitebeard/agentes-ia/processo-engenharia-com-agentes.md`;
página: https://claude.ai/code/artifact/e53c902f-b3b0-4334-b3f8-cc52c73f26bb).

## Três usos, um kit

| Uso | Como |
|---|---|
| **Operação própria** | Whitebeard aplica o kit nos seus repos; toda lição vira template aqui, não em um repo só |
| **Serviço (implantação)** | `apply.sh` em cada repo do cliente + fases 0→3 do roteiro em 8 semanas; fases 4→6 como advisory recorrente |
| **Formação (capacitação)** | Cada fase tem checklist e critério de saída; o time do cliente executa, a Whitebeard revisa — transferência de know-how é o entregável |

## Princípios (o kit existe para impor estes, não para descrevê-los)

1. IA é amplificador: fundação (VCS, testes, lotes pequenos) antes do agente.
2. Contexto mínimo e concreto: `CLAUDE.md` com comandos, custos e gotchas — nunca prosa de arquitetura.
3. Enforcement mecânico > texto: o que importa é hook, analyzer ou CI.
4. Spec antes do código; gate humano entre "o quê" e "como".
5. Autor ≠ verificador; evidência ou zero.
6. Cada erro do agente vira artefato (linha, teste, regra, hook).
7. Segurança na borda: least agency, segredos fora do contexto, conteúdo externo = input não confiável.

## Mapa

```
apply.sh                          copia os templates para um repo (não sobrescreve o que existe)
templates/
  CLAUDE.root.md                  workspace pai: tabela de serviços, etiqueta, Never, ordem padrão
  CLAUDE.service.md               por repo: comandos, custos, gotchas, pronto = exit 0
  .claude/settings.json           allowlist + deny + hooks
  .claude/hooks/                  protect-paths · guard-bash · dotnet-format
  .claude/rules/                  contracts.md · legacy.md (ativam por caminho)
  .claude/agents/                 impact-analyzer · legacy-navigator · verifier · dotnet-reviewer · contract-reviewer
  .claude/skills/                 jira-intake · run-and-test · regras-de-negocio
dotnet/
  Directory.Build.props           analyzers com rampa para legado
  nuget.config                    feed por repo (não herda o global da máquina)
  .editorconfig                   severidade no editorconfig, nunca NoWarn no csproj
  ArchitectureTests.example.cs    regra de camada como teste (mensagem escrita para o agente)
samples/orders-sample/           exemplo .NET compilado e testado (ver abaixo)
tools/gen-ebook.py                gera o e-book a partir dos arquivos reais do exemplo
docs/
  definition-of-ready.md          o card só entra se…
  spec-template/                  requirements (EARS) · design · tasks (com Verify)
  adr/0000-template.md            MADR curto
  fases-checklist.md              critérios de saída das 7 fases
```

## Início rápido (fase 1 em um repo)

```bash
git clone <este kit> ~/DEV/WHITEBEARD/agentic-engineering-kit
~/DEV/WHITEBEARD/agentic-engineering-kit/apply.sh /caminho/do/repo --dotnet
cd /caminho/do/repo && claude          # /init, depois pode o CLAUDE.md com a pergunta "remover isto faria o agente errar?"
```

Depois: preencha a tabela de serviços no `CLAUDE.md` raiz do workspace, rode `/context` (carga < 10 %), tente editar `.env`
(tem de ser bloqueado pelo hook, não por pedido).

## Exemplo real: `samples/orders-sample`

Serviço de Pedidos em .NET 10 (Domain / Application / Infrastructure + `Erp.Legacy`) com o kit aplicado e preenchido:
regra RN-ORD-012 no agregado + specification, `docs/regras/pedidos.md`, ADR-0003/0004 impostos por ArchUnitNET,
characterization test (Verify + Bogus, baseline aprovado por humano), spec 001 em 3 arquivos, `nuget.config` isolado.
Compilado e testado em 27-08-2026: build limpo, 9/9 verdes. O e-book "Engenharia com Agentes em .NET" é gerado a partir
destes arquivos por `tools/gen-ebook.py` → `~/DEV/paperclip/ebook/engenharia-com-agentes-dotnet.html`
(artifact: https://claude.ai/code/artifact/2746fde4-f60e-4189-bc26-8203a1758373). Mudou o código → regera → republica no mesmo artifact.

```bash
cd samples/orders-sample && dotnet test Orders.slnx     # ≈ 9 s
```

## Manutenção do kit

- Muda-se aqui primeiro; os repos recebem por `apply.sh`/PR. Nenhuma regra vive só num repo.
- Todo template tem dono e data de revisão (trimestral, e a cada modelo novo: remova um componente e veja o que ainda é load-bearing).
- Lição de cliente → issue neste repo → template. Sem nome de cliente nos templates.
