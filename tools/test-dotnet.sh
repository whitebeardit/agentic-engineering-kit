#!/usr/bin/env bash
# Prova o perfil .NET no exemplo samples/orders-sample: restore bloqueado pelo lockfile, formatação conferida (#28), build,
# testes, e a rampa por projeto — o legado com o conjunto Minimum e o domínio com o Recommended (issues #25 e #26).
# Até a v0.5.6 nada conferia a formatação: o hook dotnet-format.sh é melhor esforço e sai 0 quando falha.
# Até a v0.5.3 os pacotes de teste flutuavam ("*", "2.*"), não havia lockfile nem global.json, e o AnalysisLevel composto
# (latest-Recommended) anulava o AnalysisMode=Minimum do legado sem nenhum teste acusar.
# Uso: bash tools/test-dotnet.sh [--sem-testes]   (exit 0 = tudo ok; precisa do SDK do global.json)
set -uo pipefail
KIT=$(cd "$(dirname "$0")/.." && pwd); S="$KIT/samples/orders-sample"
ok=0; fail=0; passa() { ok=$((ok+1)); }; falha() { fail=$((fail+1)); echo "  ✗ $1"; }
cd "$S"
dotnet restore Orders.slnx --locked-mode >/tmp/test-dotnet-restore.log 2>&1 && passa || { falha "restore --locked-mode (lockfile ausente ou desatualizado)"; tail -5 /tmp/test-dotnet-restore.log; }
dotnet format Orders.slnx --verify-no-changes --no-restore -v:quiet >/tmp/test-dotnet-format.log 2>&1 && passa || { falha "#28: formatação (dotnet format --verify-no-changes)"; tail -5 /tmp/test-dotnet-format.log; }
if [ "${1:-}" != "--sem-testes" ]; then
  dotnet build Orders.slnx --no-restore -v:quiet >/tmp/test-dotnet-build.log 2>&1 && passa || { falha "build"; tail -15 /tmp/test-dotnet-build.log; }
  dotnet test Orders.slnx --no-build -v:quiet >/tmp/test-dotnet-test.log 2>&1 && passa || { falha "testes"; tail -15 /tmp/test-dotnet-test.log; }
fi
# rampa: o globalconfig do analisador que cada projeto carrega
nivel() { dotnet build "$1" --no-restore -v:diag 2>/dev/null | grep -o 'AnalysisLevel_[0-9]*_[A-Za-z]*_warnaserror\.globalconfig' | sort -u | head -1; }
leg=$(nivel src/Erp.Legacy/Erp.Legacy.csproj); dom=$(nivel src/Orders.Domain/Orders.Domain.csproj)
case "$leg" in *_Minimum_*) passa;; *) falha "#25: Erp.Legacy carrega '$leg' (esperado *_Minimum_*)";; esac
case "$dom" in *_Recommended_*) passa;; *) falha "#25: Orders.Domain carrega '$dom' (esperado *_Recommended_*)";; esac
diff -q "$KIT/dotnet/Directory.Build.props" "$S/Directory.Build.props" >/dev/null && passa || falha "dotnet/Directory.Build.props diverge do exemplo"
echo "test-dotnet: $ok ok, $fail falha(s) · legado: ${leg:-?} · domínio: ${dom:-?}"
[ "$fail" -eq 0 ]
