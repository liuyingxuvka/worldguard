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
| `claim.target_guards` | `worldguard.contracts` | Kernel, mesh coverage audit | contract loader | preserved | declared dispatch routes; not the coverage authority |
| `claim.target_guard` | `worldguard.contracts` | loader only | loose input alias | compatibility alias | migrated to `target_guards` |
| `claim.requested_semantics` | `worldguard.contracts` | Guards | contract loader | new | boundary checks |
| `claim.atoms.*` | `worldguard.contracts` | route derivation, native depth receipt | contract loader | new | structured claim identity, semantics, and predictive intent |
| `world_model.*` | `worldguard.contracts` | Guards, examples | contract loader | new | model inputs |
| `inputs.*` | `worldguard.contracts` | Guards | contract loader | new | model inputs |
| `dependencies.upstream_results` | `worldguard.contracts` | Kernel, downstream Guards | Kernel | new | handoff |
| `dependencies.read_only` | `worldguard.contracts` | Kernel, tests | contract loader/Kernel | new | mutation guard |
| `output_requirements.*` | `worldguard.contracts` | validators, tests | contract loader | new | result validation |
| `guard_purpose_declarations[]` | caller/AI task workflow | `GuardContract.for_guard`, task-purpose prover | explicit task-model declaration writer | new | one required declaration per selected Guard; states this model instance's purpose, boundary, and non-empty selected failures |
| `guard_purpose_contract` | `worldguard.guard_model_contract` | unit kernel, semantic verifier, native depth receipt | `GuardContract.for_guard` only, after task-local native proof and before child candidate construction | new | exact task/model Guard-candidate authority; absent on caller/base contracts and required on every formal child candidate |
| `guard_purpose_contract.family_contract_fingerprint` | `worldguard.guard_model_contract` | unit kernel, semantic verifier, SkillGuard-bundled native check | canonical family oracle catalog | new | binds the native oracle catalog as baseline provenance without turning it into the task's purpose |
| `guard_purpose_contract.protected_failure_ids` | task declaration and proof | pre-evaluation candidate verifier | explicit non-empty task-selected failure inventory | new | every selected failure must have its own task-local bad case and native proof; family-wide expansion is not inferred |
| `guard_purpose_contract.declaration_fingerprint` / `proof_receipt_fingerprint` | `worldguard.guard_model_contract` | pre-evaluation verifier, SkillGuard-bundled native check | task-local declaration and native proof | new | makes a purpose, boundary, case, oracle, identity, or proof change stale |
| `guard_purpose_contract.*_sequence` | `worldguard.guard_model_contract` | pre-evaluation candidate verifier, FlowGuard ordering model | task-purpose freezer and candidate constructor | new | proves task declaration and native proof precede candidate construction; invalid order blocks evaluation |

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

## SkillGuard Execution Authority Fields

| Field id | Owner | Readers | Writers | Lifecycle | Projection |
|---|---|---|---|---|---|
| `v2_runtime_authority_current` | WorldGuard claim-derived coverage model | native predictive closure, OpenSpec consumer | expanded V2 authority audit | false until the exact V2 trio is current in source and installation | blocks prediction when V2 is missing, stale, or accompanied by an alternate live runtime |
| `expanded_v1_retirement_clean` | WorldGuard expanded retirement inventory | native predictive closure, installation-currentness replay | expanded V1 residual audit and immutable completion receipt | false while any generic checker, policy, mutable report, evidence, ledger, run, or fallback remains | prevents a narrow two-file retirement receipt from licensing closure |
| `receipt_only_verification` | WorldGuard OpenSpec verification contract | OpenSpec verifier, SkillGuard parent receipt consumer | frozen execution-ownership plan | true only for exact current terminal-success receipt consumption without owner execution or `--resume` | prevents a validation consumer from becoming a second executor |
| `evidence_domain` | WorldGuard scheduled-production depth contract | native predictive closure, SkillGuard depth evaluator | current check snapshot and WorldGuard native bridge | `scheduled_production` for formal closure; `fixture_calibration` only for positive/shallow calibration | prevents fixture evidence from being relabeled as an actual mesh run |
| `scheduled_production_identity` | exact target-owned WorldGuard mesh input | WorldGuard native bridge, installation-currentness replay, closure | single scheduled execution owner writes the verified identity into the mesh before supervision | binds trigger, execution, installation receipt id/hash/root, and installed runtime fingerprint before execution and replays them before closure; a generic supervisor-request copy is non-authoritative | ties prediction evidence to one current installed target execution without allowing generic request metadata to impersonate native evidence |
| `exact_single_mesh_input` | WorldGuard native bridge | claim-derived coverage model, SkillGuard target-input fingerprinting | current target request | exactly one mesh-bearing JSON input per formal depth execution; extras and alternates fail closed | prevents a rich aggregate or unrelated extra input from widening the licensed claim |
| `fixture_calibration_isolated` | WorldGuard target-native calibration protocol | claim-derived coverage model, SkillGuard calibration consumer | positive and shallow fixture checks | true only while fixture observations remain outside scheduled-production closure | preserves calibration value without permitting fixture-as-production |
| `native_minimum_timepoint_count` | WorldGuard temporal-depth policy | per-node/per-variable assessment, native floor receipt, SkillGuard bridge | `ceil(sqrt(horizon_steps))`, bounded by the horizon and raised only by stricter target policy | replaces the weaker logarithmic default | prevents a very long horizon from passing with a token handful of points |
| `max_normalized_timepoint_gap` | WorldGuard temporal-depth assessment | predictive license, per-object receipt, diagnostics | exact sorted observed coordinates plus horizon boundaries | current per run and per model-node/variable child | blocks count-complete samples that leave a large unobserved temporal hole |
| `allowed_max_normalized_timepoint_gap` | WorldGuard temporal-depth policy | predictive license and receipt consumer | `min(0.5, 2.5 / max(observed_count - 1, 1))` | current target-native policy | lets a complete three-point early/middle/late short horizon pass while tightening quickly for larger samples and preventing clustered sampling |
| `native_obligation_evidence` | WorldGuard native depth receipt | native closure, SkillGuard exact-evidence consumer, report | exact semantic-child inputs/outputs, per-node/per-variable temporal rows, scenario/holdout portfolio, predictive axes, native policy, and claim routes | current per run; every observation is content-addressed | prevents counts, names, or a whole-receipt digest from substituting for exact per-obligation proof |
| `portable_native_runtime_bound` | installed WorldGuard skill runtime | semantic-rollout model, native depth/calibration bridges, SkillGuard closure replay | V2 compiler and transactional skill installation | true only when every bundled `.skillguard/runtime` Python source is present, fingerprinted, declared as a depth/calibration input, and loaded ahead of any editable checkout | blocks broad or predictive closure when an ungoverned global/source import could replace the installed native evaluator |

## Old Field Disposition

- `claim.target_guard`: accepted only as an input alias, normalized into canonical `claim.target_guards`, and never emitted as canonical output.
- `claim.target_guards`: preserved for dispatch compatibility, but claim-atom semantics now own required-route derivation; missing derived routes fail closed instead of being silently skipped.
- Root `evidence/` fixture paths: preserved as historical input sources, copied into `examples/fuel_cell/` for productized use, and excluded from Git/package core surface.

## Handoffs

- Field projections feed `tests/test_contracts.py`, `tests/test_kernel_handoff.py`, and the Codex skill prompt contract.
- Any future public API compatibility promise around old fields must add explicit migration tests before full confidence.
