# WorldGuard Contracts

## Contract Layers

`GuardContract` is the unit-level check surface for one claim against one explicit model.

`ModelMeshContract` is the topology-level check surface for multiple model nodes, model edges, authority boundaries, freshness requirements, and handoff closure. It must not replace or bloat `GuardContract`.

## GuardContract

Required canonical fields:

- `contract_id`
- `schema_version`
- `run_id`
- `claim.claim_id`
- `claim.text`
- `claim.target_guards`
- `claim.requested_semantics`
- `claim.atoms[].atom_id`
- `claim.atoms[].text`
- `claim.atoms[].requested_semantics`
- `claim.atoms[].predictive_intent`
- `world_model.model_id`
- `world_model.model_version`
- `world_model.entities`
- `world_model.relations`
- `world_model.assumptions`
- `world_model.scope_limits`
- `inputs.events`
- `inputs.variable_observations` or equivalent signal/time-series observations when predictive variables or signals are exposed
- `inputs.beliefs`
- `inputs.spatial_relations`
- `inputs.resources`
- `inputs.causal_model`
- `inputs.game_model`
- `inputs.norms`
- `dependencies.upstream_results`
- `dependencies.read_only`
- `output_requirements.require_ledgers`
- `output_requirements.require_counterexample_for_non_pass`
- `output_requirements.allowed_status`
- `guard_purpose_declarations` with exactly one task-model-instance declaration
  for every Guard child that may be selected or claim-derived

`guard_purpose_contract` is a runtime-owned field on each formal per-Guard
child candidate. It is derived only from the matching explicit parent
`guard_purpose_declarations` row after the task-local good/bad proof passes; it
is never synthesized from the Guard name. It contains the current family
catalog fingerprint, exact task declaration and proof fingerprints, selected
failure ids, task/run/model/Guard identity, candidate identity, and
freeze/construction sequence. Unit and semantic verifiers reject a missing,
empty, unknown-oracle, incomplete-proof, stale, wrong-instance, or out-of-order
binding before running the Guard proof.

`claim.target_guard` is retired and rejected in normal runtime. Migrate old
files directly to `claim.target_guards` before invoking WorldGuard.

`claim.target_guards` is an execution declaration, not the authority for what
must be checked. WorldGuard maps structured atom semantics to their owning
Guards and compares the derived set with the declared set. Missing derived
routes fail closed. Claims without current `requested_semantics` or structured
atoms are rejected; the caller's target list is never used as a fallback
authority.

Likewise, `semantic_coverage.expected_model_node_ids` is a completeness
assertion over the mesh-discovered node inventory. It cannot shrink that
inventory. `excluded_model_nodes` requires a reason plus closed disposition and
is valid only for a discovered non-critical node that contributes to neither
execution coverage nor covered claim scope.

## Guard Model Adequacy Contract

Contract shape alone does not prove that a Guard model is meaningful. The
family catalog must exhaust native runtime failure codes, while each real task
child separately declares:

- the invalid claim class the Guard prevents;
- the boundary it deliberately does not license;
- exactly one task-local native good case;
- a non-empty one-or-many selection from the source-discovered Guard-owned unit
  and semantic failure codes;
- exactly one task-local native bad case for every selected failure; and
- an oracle that observes the exact expected status and single stable code.

The current declaration and executable oracle live in
`worldguard.guard_model_contract`; the human-readable ownership table is in
`guard-model-contract.md`. A changed literal Guard-owned failure code changes
the family oracle catalog and must be reconciled before a task may select it.
The family catalog never automatically becomes a real child's declared
purpose. Mesh registration and provider-lifecycle codes remain separately owned
and cannot be counted as individual-Guard coverage.

## GuardResult

Required canonical fields:

- `result_id`
- `contract_id`
- `guard`
- `status`
- `supported_claims`
- `rejected_claims`
- `missing_slots`
- `boundary_exceeded`
- `errors`
- `counterexamples`
- `ledgers`
- `assumptions_used`
- `scope_limits`
- `consumed_inputs`

For `FAIL`, `GAP`, and `BOUNDARY_EXCEEDED`, require at least one concrete evidence field: missing slots, boundary trace, errors, or counterexamples.

## LedgerEntry

Required canonical fields:

- `ledger_entry_id`
- `run_id`
- `claim_id`
- `guard`
- `channel`
- `status_impact`
- `payload`
- `source_refs`
- `read_only_for_downstream`
- `created_at_step`

Every downstream-facing ledger entry must be read-only.

## ModelMeshContract

Read `model-mesh.md` for the canonical mesh fields.

Core rule: child `GuardContract` success is not whole-mesh success. Mesh closure must also preserve child reports and validate model authority, handoffs, freshness, and cycles.

## Task-Local Prediction And Revision

`PredictionSnapshot` is the empirical task-local layer. It does not replace a
`GuardContract`, `ModelMeshContract`, semantic execution, or native predictive
depth. It freezes:

- one exact base world-model id, version, path, and SHA-256;
- one prediction sequence;
- the declared initial state and intervention;
- finite expected numeric values with absolute tolerances;
- expected relationships identified by stable ids and exact
  left/relation/right content; and
- explicit weakening conditions.

Every expected value or relationship declares one mismatch category:
`initial_state`, `transition`, `causal_relation`, `resource`, `agent`,
`observation_mapping`, or `other`. The evaluator retains that declared owner;
it does not infer an owner from a target name.

`ObservedWorldSnapshot` must name the prediction, use a strictly later sequence,
retain a non-empty source reference, and carry at least one actual finite value
or typed relationship. Missing declared expectations are mismatches; they
cannot be silently treated as unobserved success.

`CandidateWorldModelRevision` binds separate current base and candidate
artifacts. A candidate path or content hash equal to v1 is invalid because it
cannot be rolled back independently. Acceptance requires an exact declared
revalidation inventory containing both:

- `original_scenario`; and
- `real_holdout_observation`.

Each revalidation must bind the exact candidate identity and show both
WorldGuard semantic rollout and a `worldguard_observed_world_comparison_receipt`
passing. Semantic execution without a real-observation comparison is not
empirical validation.

The evaluator is read-only. A passing candidate is `accepted`; a failed
unapplied candidate is `rejected`; a failed applied candidate is `rolled_back`
only when its rollback identity exactly equals the still-current v1. These
dispositions modify no WorldGuard code, core threshold, installed skill, or
reusable default.

### Fact-level transaction

`FactWorldSnapshot` and `FactRevisionTransaction` are a subordinate form of
the same task-local revision owner. `FactSupport` records one independent
positive or negative support with stable source and evidence ids.
`StrictFactRule` derives only one declared signed consequent when every signed
antecedent has support. The resulting fact state is `true`, `false`, `both`,
or `neither`; these values are not Guard terminal statuses.

Preview is copy-based and returns the exact base/candidate fingerprints,
support and rule-chain deltas, contradiction ids, preserved-fact outcomes,
closure status, and preview fingerprint. Activation requires that fingerprint,
the exact visible contradiction set, and current `regression` plus `holdout`
evidence bound to the preview. A stale base, changed preserved fact, missing
evidence, or prior activation of the transaction remains blocked.
