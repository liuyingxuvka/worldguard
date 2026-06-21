# WorldGuard Field Lifecycle Review

Route: `field_lifecycle_mesh`

## Field Boundary

Boundary: public runtime dataclass/dict fields, fixture fields, CLI payload fields, and Codex skill prompt contract fields introduced for the WorldGuard MVP.

## Contract Fields

| Field id | Owner | Readers | Writers | Lifecycle | Projection |
|---|---|---|---|---|---|
| `contract_id` | `worldguard.contracts` | Kernel, tests, CLI | contract loader | new | behavior-bearing identity |
| `schema_version` | `worldguard.contracts` | validators, tests | contract loader | new | compatibility and validation |
| `run_id` | `worldguard.contracts` | ledgers, reports | contract loader | new | traceability |
| `claim.claim_id` | `worldguard.contracts` | all Guards, ledgers | contract loader | new | behavior-bearing |
| `claim.text` | `worldguard.contracts` | all Guards | contract loader | new | behavior-bearing |
| `claim.target_guards` | `worldguard.contracts` | Kernel | contract loader | new | dispatch owner |
| `claim.target_guard` | `worldguard.contracts` | loader only | loose input alias | compatibility alias | migrated to `target_guards` |
| `claim.requested_semantics` | `worldguard.contracts` | Guards | contract loader | new | boundary checks |
| `world_model.*` | `worldguard.contracts` | Guards, examples | contract loader | new | model inputs |
| `inputs.*` | `worldguard.contracts` | Guards | contract loader | new | model inputs |
| `dependencies.upstream_results` | `worldguard.contracts` | Kernel, downstream Guards | Kernel | new | handoff |
| `dependencies.read_only` | `worldguard.contracts` | Kernel, tests | contract loader/Kernel | new | mutation guard |
| `output_requirements.*` | `worldguard.contracts` | validators, tests | contract loader | new | result validation |

## Result And Ledger Fields

| Field id | Owner | Readers | Writers | Lifecycle | Projection |
|---|---|---|---|---|---|
| `result_id` | `worldguard.reports` | Kernel, tests | Guard runners | new | traceability |
| `status` | `worldguard.reports` | Kernel, CLI, tests | Guard runners | new | aggregate behavior |
| `missing_slots` | `worldguard.reports` | tests, CLI | Guard runners | new | GAP evidence |
| `boundary_exceeded` | `worldguard.reports` | tests, CLI | Guard runners | new | BOUNDARY evidence |
| `errors` | `worldguard.reports` | tests, CLI | Guard runners | new | non-pass evidence |
| `counterexamples` | `worldguard.reports` | Kernel, tests | Guard runners | new | FAIL/GAP evidence |
| `ledgers` | `worldguard.reports` | Kernel, tests | Guard runners | new | traceability |
| `read_only_for_downstream` | `worldguard.ledgers` | Kernel, tests | ledger helpers | new | handoff invariant |

## Old Field Disposition

- `claim.target_guard`: accepted only as an input alias, normalized into canonical `claim.target_guards`, and never emitted as canonical output.
- Root `evidence/` fixture paths: preserved as historical input sources, copied into `examples/fuel_cell/` for productized use, and excluded from Git/package core surface.

## Handoffs

- Field projections feed `tests/test_contracts.py`, `tests/test_kernel_handoff.py`, and the Codex skill prompt contract.
- Any future public API compatibility promise around old fields must add explicit migration tests before full confidence.
