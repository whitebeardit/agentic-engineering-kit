# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Plan/Checks)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-002 - Assert every value the criterion names, not a subset of them.
- signal: `weak_test` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: 001-merge-por-unidade
- evidence: .specs/features/001-merge-por-unidade/verification.md Findings 1 (C5, ruleId; mutação M4) (tests) (+2 more)
- last seen: 2026-11-22T18:40:58Z

### L-003 - Assert both sides of every numeric boundary a criterion fixes, on each operand of the comparison.
- signal: `weak_test` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: 001-merge-por-unidade
- evidence: .specs/features/001-merge-por-unidade/verification.md Findings 2 (C5, fronteira N-1; mutação M3) (tests)
- last seen: 2026-11-22T18:40:58Z

### L-004 - Give every confirmed assumption in the spec a test that fails when the assumption is reversed.
- signal: `weak_test` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: 001-merge-por-unidade
- evidence: .specs/features/001-merge-por-unidade/verification.md Findings 3 (C5, apto fora do limiar; mutação M11) (tests)
- last seen: 2026-11-22T18:40:58Z

### L-005 - When two criteria decide by different attributes of the same unit, write the criterion for the case where they disagree.
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `spec` · harmful: 0
- features: 001-merge-por-unidade
- evidence: .specs/features/001-merge-por-unidade/verification.md Findings 6 (ING-04 com ING-06; exemplo próprio) (spec)
- last seen: 2026-11-22T18:40:58Z

### L-006 - Test the excluded case of every condition a criterion restricts to one origin or role.
- signal: `weak_test` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: 001-merge-por-unidade
- evidence: .specs/features/001-merge-por-unidade/verification.md Findings 7 (C8; mutação A5) (tests)
- last seen: 2026-11-22T18:40:58Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
