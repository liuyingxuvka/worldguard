# WorldGuard Contracts

## GuardContract

Required canonical fields:

- `contract_id`
- `schema_version`
- `run_id`
- `claim.claim_id`
- `claim.text`
- `claim.target_guards`
- `claim.requested_semantics`
- `world_model.model_id`
- `world_model.model_version`
- `world_model.entities`
- `world_model.relations`
- `world_model.assumptions`
- `world_model.scope_limits`
- `inputs.events`
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

`claim.target_guard` is only a compatibility input alias. Normalize it to `claim.target_guards`.

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
