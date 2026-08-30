@AGENTS.md

# Só para o Claude Code

- Plugins esperados: `kit@whitebeard-kit` e `tlc@whitebeard-kit` (marketplace: git@github.com:whitebeardit/agentic-engineering-kit.git). O hook SessionStart avisa se o tlc estiver ausente ou desatualizado.
- Nomes no plugin: `/kit:card-intake`, `/kit:run-and-test`, `/kit:regras-de-negocio`; agentes `kit:impact-analyzer`, `kit:legacy-navigator`, `kit:test-designer`, `kit:code-reviewer`, `kit:contract-reviewer`; spec-driven `/tlc:tlc-spec-driven`.
- O Verifier do tlc roda sozinho após a última task — não há outro verificador. `kit:test-designer` só em tier alto ou legado.
- Plan mode em tudo que toca ≥ 3 arquivos; `/clear` entre tarefas; `/context` < 10 %.
- Hooks de enforcement vêm de `.claude/settings.json` deste repo, não do plugin.
