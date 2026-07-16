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
- Did structural, semantic, provider, and rollout status remain distinct?
- Did every required semantic child run through a declared typed binding?
- Does every invoked Guard have a declared prevention purpose and unsupported boundary?
- Did the source-discovered finite Guard-owned failure inventory exactly match the declared inventory, with one native good per Guard, one native bad per failure class, and an exact status/code oracle reaction?
- Were required Guards derived from structured claim atoms rather than accepted from the caller's target list alone?
- Did every expected semantic-rollout node supply a contract, and does every skipped node/child have a typed reason and coverage impact?
- Were all current mesh nodes discovered before applying the caller expected list, and do discovered = declared + closed exclusions with exclusions contributing to neither execution nor claim scope?
- For predictive work, did both normal and holdout scenarios execute across a non-degenerate horizon with the effective square-root representative timepoint floor, required coverage ratio, native early/middle/late coverage, acceptable maximum normalized time gap, states, transitions, branches, perturbations, interventions, and counterfactuals for every expected model node rather than only in aggregate?
- For every exposed variable or signal, did its own temporal child universe independently meet the native dynamic count and early/middle/late floors, and is that per-object floor bound into the SkillGuard receipt without a conflicting fixed ratio?
- Does the native depth receipt list executed and skipped children, provider
  states, claim/route coverage, quantitative coverage, mesh/coverage fingerprints, predictive gaps, license decision, findings, and the aggregate claim boundary?
- Are any old, stale, replaced, or superseded models still being used without disposition?

## Status Rules

- Any hard contradiction, forbidden handoff, dependency cycle, or unknown required node/edge error can make the mesh `FAIL`.
- Any unresolved missing node, missing target, missing source, stale required source, or missing model field can make the mesh `GAP`.
- Any authority overreach or unsupported semantic can make the mesh `BOUNDARY_EXCEEDED`.
- Only when all child reports and mesh findings are pass-compatible may the mesh be `PASS`.
- Structural-only work must remain `BOUNDARY_ONLY`/`NOT_RUN` for semantic
  closure; it cannot be described as simulated or semantically validated.
- Provider-unavailable and unevaluable semantic cases fail closed even when
  every required input field is present.
- A connected Guard whose purpose, finite failure inventory, good/bad
  cardinality, or native reaction oracle is missing or stale cannot support
  closure. In particular, a partially defined SCM is `GAP`, not `PASS`.
- One event, one or two convenient timepoints, enough points concentrated in only one phase, a rich aggregate with one shallow child, one equation, or one convenient scenario may pass a
  local bounded check, but cannot license prediction. Predictive closure needs
  `predictive_claim_licensed: true` on the current target receipt.
- Static repository regressions prove engine health only; missing or stale
  per-target receipt evidence remains `NOT_RUN`/`GAP`.

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
- component statuses, semantic receipts, and the native depth receipt;
- missing fields and stale evidence, if any.

Do not copy adapter-specific terms into the core closure report unless they appear only as opaque labels supplied by an upstream adapter.
