@AGENTS.md

# Só para o Claude Code
- Plugins esperados: `kit@whitebeard-kit` e `tlc@whitebeard-kit` (`claude plugin marketplace add git@github.com:whitebeardit/agentic-engineering-kit.git` → `claude plugin install kit@whitebeard-kit`). O hook SessionStart avisa se o tlc estiver ausente ou desatualizado.
- Nomes no plugin: skills `/kit:card-intake`, `/kit:run-and-test`, `/kit:regras-de-negocio`; agentes `kit:impact-analyzer`, `kit:legacy-navigator`, `kit:test-designer`, `kit:code-reviewer` (ou `kit:dotnet-reviewer`), `kit:contract-reviewer`, `kit:trace-finder`, `kit:telemetry-cost-auditor`, `kit:alert-auditor`; spec-driven `/tlc:tlc-spec-driven`. Instalação standalone (`apply.sh --standalone`) usa os nomes sem prefixo.
- O Verifier do tlc roda sozinho após a última task — não há outro verificador. `kit:test-designer` só em tier alto ou legado.
- Plan mode em tudo que toca ≥ 3 arquivos; `/clear` entre tarefas; `/context` < 10 %.
- Hooks de enforcement (protect-paths, guard-bash, format) vêm de `.claude/settings.json` deste repo, não do plugin.
