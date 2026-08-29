# 001 — Cancelamento parcial · tasks

Uma task = um repo = um PR. Sessão nova por task; plan mode; commit atômico; PR draft com intenção + prova + risco.

- [~] T1 `orders-sample` — contrato: `OrderItemCancelled` v1 · Verify: record do evento existe e é aditivo (VERIFICADO); publicação no catálogo AsyncAPI **PENDENTE** (o exemplo não tem catálogo)
- [x] T2 `orders-sample` — `docs/regras/pedidos.md#RN-ORD-012` + testes `RN_ORD_012_*` pelo `test-designer` (sessão própria; um teste por cláusula, escritos uma vez) · Verify: `dotnet test --filter RN_ORD_012` → 5 falhas esperadas
- [x] T3 `orders-sample` — `Order.CancelItem` + specification + handler · Verify: `dotnet test` → verde, incluindo `ArchitectureTests`
- [ ] T4 `erp-mono` — consumidor atrás de `estoque.libera-por-evento` · Verify: characterization de reserva inalterado + cenário novo
- [ ] T5 — registrar no vault: repos tocados, ordem, decisões, evidência, lições

**Verificação (verifier ≠ autor)**: 2026-08-27 · T2–T3 PASS, T1 parcial (output em `docs/evidencia/2026-08-27-dotnet-test.txt`)
