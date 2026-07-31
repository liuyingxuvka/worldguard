# WorldGuard Field Lifecycle Review

Route: `field_lifecycle_mesh`

## Field Boundary

Boundary: public runtime dataclass/dict fields, fixture fields, CLI payload fields, and Codex skill prompt contract fields introduced for the WorldGuard MVP.

## Contract Fields

| Field id | Owner | Readers | Writers | Lifecycle | Projection |
|---|---|---|---|---|---|
| `contract_id` | `worldguard.contracts` | Kernel, tests, CLI | contract loader | new | behavior-bearing identity |
| `schema_version` | `worldguard.contracts` | validators, tests | contract loader | current-only | exact schema validation; retired shapes fail visibly |
| `run_id` | `worldguard.contracts` | ledgers, reports | contract loader | new | traceability |
| `claim.claim_id` | `worldguard.contracts` | all Guards, ledgers | contract loader | new | behavior-bearing |
| `claim.text` | `worldguard.contracts` | all Guards | contract loader | new | behavior-bearing |
| `claim.target_guards` | `worldguard.contracts` | Kernel, mesh coverage audit | contract loader | preserved | declared dispatch routes; not the coverage authority |
| `claim.target_guard` | none in normal runtime | upgrade AI only | no product writer | retired and rejected | old files must be migrated directly to `target_guards` before normal use |
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

## Task-Local Prediction And Revision Fields

| Field id | Owner | Readers | Writers | Lifecycle | Projection |
|---|---|---|---|---|---|
| `task_id` / `purpose` | `worldguard.task_local_world_revision` | prediction freezer, candidate evaluator, fact handoff | current task author | required current | binds every receipt to one finite question instead of an AI self-report |
| `coverage_universe_*` / `coverage_ids` | independent task coverage inventory | prediction freezer, comparisons, native-depth binding | independent coverage owner | required current | fingerprint is recomputed and ids must exactly equal declared expectation ids |
| `assumptions` / `unknowns` | current task author | prediction and claim-boundary reviewers | current task author | required non-empty | makes the model boundary explicit without recording an understanding level |
| `predecessor_iteration_fingerprint` | task-local revision owner | later iteration evaluator | prior terminal receipt owner | `root` at iteration zero, content hash later | preserves exact lineage |
| `prior_gap_ids` / `prior_gap_fingerprints` | task-local revision owner | gap transition evaluator | prior terminal receipt owner | empty at iteration zero; exact ids plus bound fingerprint later | replaces caller-authored progress and transition maps |
| `observation_evidence_fingerprint` | observation provider | comparison and revalidation | canonical observation hasher | required current | binds ids, source, sequence, values, relations, and external inputs |
| `observation_content_fingerprint` | comparison owner | holdout independence check | canonical content hasher | derived current | detects renamed original/holdout content aliases |
| `native_depth_receipt` | WorldGuard native-depth owner | candidate evaluator | task-local depth binder | exact `worldguard.native_depth.v2` only | binds task, candidate, coverage, seven-category gaps, quantitative coverage, and predictive license |
| `required_revalidation_ids` | task-local revision owner | candidate evaluator | current candidate plan | exactly original plus real holdout | rejects renamed or extra pseudo-checks |
| `semantic_receipt` / `empirical_comparison` | WorldGuard semantic and empirical owners | candidate evaluator | typed binding helpers | current content-addressed | replaces a bare `PASS` string |
| `terminal_reason` | task-local revision owner | caller and fact handoff | deterministic evaluator | derived only | only this owner can emit `model_closed_for_task` |

## SkillGuard Execution Authority Fields

| Field id | Owner | Readers | Writers | Lifecycle | Projection |
|---|---|---|---|---|---|
| `author_skillguard_authority_current` | WorldGuard maintainer source | author validation and release-readiness audit | current author compiler | true only when the exact author contract trio and retirement receipt are current in the source | keeps maintenance authority out of the consumer |
| `former_author_skillguard_authority_absent` | WorldGuard expanded retirement inventory | author validation and release-readiness audit | expanded former-author residual audit | false while any retired checker, policy, mutable report, evidence, ledger, run, cache, or fallback remains | blocks residual author authority without adding a reader |
| `installed_consumer_projection_current` | target-owned `consumer-release.json` | release-readiness audit and installed use | transactional consumer installer | true only when source projection, manifest, and installed bytes have one exact inventory and identity | provides one current installed authority rather than source/installed alternates |
| `installed_consumer_author_control_absent` | target-owned consumer boundary | release-readiness audit | transactional consumer installer | true only when the installed tree contains zero `.skillguard` paths | prevents author contracts or receipts from becoming consumer runtime |
| `receipt_only_verification` | WorldGuard OpenSpec verification contract | OpenSpec verifier, SkillGuard parent receipt consumer | frozen execution-ownership plan | true only for exact current terminal-success receipt consumption without owner execution or `--resume` | prevents a validation consumer from becoming a second executor |
| `evidence_context` | WorldGuard native-depth projection | native predictive closure, SkillGuard depth evaluator | current target-owned evaluator | exact discriminated object `{domain, identity}`; release validation uses only `release_gate` and never probes an alternate identity | binds the evidence domain and its exact identity without parallel top-level fields or fallback |
| `release_gate_binding` | exact target-owned WorldGuard release input | WorldGuard native bridge and release closure | release owner writes one version, gate, target, and execution-owner binding into the mesh input before supervision | current only when the schema, WorldGuard version, gate id, and declared check owner match exactly; retired production-shaped fields are rejected | ties release evidence to the real release gate without mislabeling validation as a scheduled production run |
| `exact_single_mesh_input` | WorldGuard native bridge | claim-derived coverage model, SkillGuard target-input fingerprinting | current target request | exactly one mesh-bearing JSON input per formal depth execution; extras and alternates fail closed | prevents a rich aggregate or unrelated extra input from widening the licensed claim |
| `fixture_calibration_isolated` | WorldGuard target-native calibration protocol | claim-derived coverage model, SkillGuard release-gate consumer | positive and shallow fixture checks | true only while calibration observations remain outside release closure | preserves calibration value without permitting calibration-as-release evidence |
| `native_minimum_timepoint_count` | WorldGuard temporal-depth policy | per-node/per-variable assessment, native floor receipt, SkillGuard bridge | `ceil(sqrt(horizon_steps))`, bounded by the horizon and raised only by stricter target policy | replaces the weaker logarithmic default | prevents a very long horizon from passing with a token handful of points |
| `max_normalized_timepoint_gap` | WorldGuard temporal-depth assessment | predictive license, per-object receipt, diagnostics | exact sorted observed coordinates plus horizon boundaries | current per run and per model-node/variable child | blocks count-complete samples that leave a large unobserved temporal hole |
| `allowed_max_normalized_timepoint_gap` | WorldGuard temporal-depth policy | predictive license and receipt consumer | `min(0.5, 2.5 / max(observed_count - 1, 1))` | current target-native policy | lets a complete three-point early/middle/late short horizon pass while tightening quickly for larger samples and preventing clustered sampling |
| `native_obligation_evidence` | WorldGuard native depth receipt | native closure, SkillGuard exact-evidence consumer, report | exact semantic-child inputs/outputs, per-node/per-variable temporal rows, scenario/holdout portfolio, predictive axes, native policy, and claim routes | current per run; every observation is content-addressed | prevents counts, names, or a whole-receipt digest from substituting for exact per-obligation proof |
| `portable_native_runtime_bound` | installed WorldGuard target runtime | semantic rollout and target-native checks | transactional consumer installer | true only when every `runtime/worldguard` source is present in the exact consumer manifest and used by the installed entrypoint | blocks an editable checkout or author-control tree from replacing the consumer evaluator |

## Old Field Disposition

- `claim.target_guard`: rejected in normal runtime. Upgrade AI must rewrite old files directly to `claim.target_guards` before activation.
- `claim.target_guards`: current execution declaration. Structured semantics own required-route derivation; missing semantic structure or derived routes fails closed.
- Root `evidence/` fixture paths: preserved as historical input sources, copied into `examples/fuel_cell/` for productized use, and excluded from Git/package core surface.
- Former optional task fields, `remaining_predictive_gap_ids`, caller-authored transition maps, and boolean progress fields: rejected in normal runtime; no compatibility reader or migration fallback exists.
- Fact activation `model_closed_for_task`: retired. Current activation emits only `task_local_revalidation_required` to the same task owner.

## Handoffs

- Field projections feed `tests/test_contracts.py`, `tests/test_kernel_handoff.py`, and the Codex skill prompt contract.
- Retired public fields may be read only inside a bounded transactional upgrade that rewrites them directly to the current schema and removes all residuals before activation.
