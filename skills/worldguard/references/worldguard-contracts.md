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

`claim.target_guard` is only a compatibility input alias. Normalize it to `claim.target_guards`.

`claim.target_guards` is an execution declaration, not the authority for what
must be checked. WorldGuard maps structured atom semantics to their owning
Guards and compares the derived set with the declared set. Missing derived
routes fail closed. Legacy claims without atoms remain runnable for bounded
compatibility, but cannot use their own target list as proof of predictive
completeness.

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
