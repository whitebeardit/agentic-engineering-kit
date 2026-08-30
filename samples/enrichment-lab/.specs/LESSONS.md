# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Editing docs by exact-string replacement after prettier reformats them silently no-ops; assert every replacement and run prettier before editing, or the task closes in two commits.

- signal: `spec_deviation` · recurrence: 1 feature(s) · scope: `docs` · harmful: 0
- features: 001-merge-por-unidade
- evidence: .specs/features/001-merge-por-unidade/validation.md (Verifier, nota 1: T6 em dois commits) (docs)
- last seen: 2026-08-30T16:54:41Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
