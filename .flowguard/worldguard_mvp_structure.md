# WorldGuard MVP FlowGuard Structure Review

Route: `code_structure_recommendation`

## Existing Model Preflight

- Model search paths: `WorldGuard_TECHNICAL_SPEC.md`, `docs/Atomic_Acceptance_Matrix.md`, `docs/productization_audit.md`, `openspec/changes/productize-worldguard-mvp`.
- Existing executable implementation: none found.
- Existing owner evidence: the technical specification owns behavior semantics; the atomic acceptance matrix records code/test/package gaps.
- Reuse decision: `extend_existing` by implementing the specification as a new product package, not by creating a parallel semantic model.
- Duplicate boundary risk: route-local WG-13 repair evidence must not become the core runtime owner.

## FunctionBlock Ownership

| FunctionBlock | Target module | Owns |
|---|---|---|
| Contract normalization | `worldguard.contracts` | `GuardContract`, claim/world/input/dependency/output fields, target_guard alias handling |
| Status semantics | `worldguard.status` | `GuardStatus`, aggregate priority |
| Ledger accounting | `worldguard.ledgers` | `LedgerEntry`, ledger channels, read-only ledger defaults |
| Result/report validation | `worldguard.reports` | `GuardResult`, non-pass evidence validation, `GuardedReport` |
| Guard dispatch and aggregation | `worldguard.kernel` | target Guard selection, read-only handoff, child result aggregation |
| Per-Guard checks | `worldguard.guards.*` | local PASS/FAIL/GAP/BOUNDARY checks and ledgers |
| CLI and example replay | `worldguard.cli`, `worldguard.examples.fuel_cell` | file loading, example checks, JSON output |
| Codex skill integration | local `worldguard` skill | contract-first prompt workflow and helper script |

## Validation Boundaries

- Contract boundary: `tests/test_contracts.py`.
- Ledger boundary: `tests/test_ledgers.py`.
- Per-Guard boundaries: `tests/guards/test_status_matrix.py`.
- Kernel boundary: `tests/test_kernel_handoff.py`.
- Example replay boundary: `tests/test_fuel_cell_demo.py`.
- Skill boundary: local and repository skill validation plus helper script output.

## Claim Boundary

This model supports an MVP claim only: structured contract/result/ledger behavior, minimal Guard semantics, Kernel preservation, optional toy example replay, packaging, and local skill installation. It does not support claims about complete formal solvers or real-world fuel-cell validity.
