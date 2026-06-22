# Closure Report

Use closure reports before claiming a multi-model WorldGuard check is complete.

## Closure Questions

- Did every required node load?
- Did every required edge connect existing nodes?
- Did each node stay inside model authority?
- Did every current-required handoff use current source evidence?
- Did downstream nodes avoid forbidden use?
- Did the mesh avoid dependency cycles?
- Were child `FAIL`, `GAP`, and `BOUNDARY_EXCEEDED` statuses preserved?
- Were child ledgers preserved in the aggregate ledger?
- Are any old, stale, replaced, or superseded models still being used without disposition?

## Status Rules

- Any hard contradiction, forbidden handoff, dependency cycle, or unknown required node/edge error can make the mesh `FAIL`.
- Any unresolved missing node, missing target, missing source, stale required source, or missing model field can make the mesh `GAP`.
- Any authority overreach or unsupported semantic can make the mesh `BOUNDARY_EXCEEDED`.
- Only when all child reports and mesh findings are pass-compatible may the mesh be `PASS`.

## Report Shape

Return:

- conclusion status;
- mesh summary;
- node report summary;
- handoff findings;
- authority findings;
- freshness findings;
- cycle findings;
- child and mesh ledger evidence;
- missing fields and stale evidence, if any.

Do not copy adapter-specific terms into the core closure report unless they appear only as opaque labels supplied by an upstream adapter.
