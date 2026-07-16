# WorldGuard ModelMesh

Use ModelMesh when a question depends on more than one model, model version, or model-to-model handoff.

## Core Rule

`GuardContract` is the unit-level check. `ModelMeshContract` is the topology-level check.

Do not report a mesh as `PASS` merely because a child `GuardContract` passed. Mesh closure must also check authority, handoff, freshness, cycles, and child evidence preservation.

## ModelMeshContract Fields

Required canonical fields:

- `mesh_id`
- `schema_version`
- `run_id`
- `nodes`
- `edges`
- `snapshots`
- `provider_availability`: optional per-Guard availability override
- `semantic_coverage`: a `SemanticCoverageContract`; expected node ids default to every current mesh node

## SemanticCoverageContract Fields

- `profile`: `bounded` by default or explicit `predictive`
- `expected_model_node_ids`
- `excluded_model_nodes`: explicit reason, closed disposition, and non-critical/non-contributing object only
- `expected_semantic_child_ids`
- `scenario_ids`
- `holdout_scenario_ids`
- `state_ids`
- `transition_ids`
- `branch_ids`
- `perturbation_ids`
- `intervention_ids`
- `counterfactual_ids`
- `horizon`: explicit `start`, `end`, and step count
- `timepoint_ids`: target-owned representative checkpoints; these are required observations, not a demand to enumerate every raw point
- `minimum_timepoint_count` and `minimum_timepoint_coverage`: optional stricter target floors; they cannot weaken the native square-root floor or maximum-gap gate
- `time_strata`: optional target-authored additional phase-to-timepoint mapping; WorldGuard always derives its native early/middle/late positions from numeric, prefixed-numeric, or ISO time values, and caller labels cannot replace those three gates
- `per_model_node`: optional target-owned overrides when expected model nodes genuinely have different horizons or axes; without an override the shared policy applies independently to every expected node

The current mesh inventory defines the denominator. `expected_model_node_ids`
asserts that the caller accounted for that inventory and cannot remove a
discovered node. A valid exclusion remains in the discovered/declared/excluded
reconciliation receipt but contributes to neither execution nor covered claim
scope. WorldGuard reports which effective nodes were executed, skipped,
missing, or locally bounded. Predictive fields are not credited merely
because they exist: native EventGuard/CausalGuard outputs must demonstrate the
corresponding scenario, state, transition, branch, perturbation, intervention,
counterfactual, holdout, representative timepoint count/ratio, native phase-stratified execution, and per-model-node depth. A 1,000-step horizon with only two observed points is a predictive gap; enough points concentrated in one phase are also a gap; and a rich aggregate cannot hide one shallow expected model node.

When a node exposes variables or signals, each `(node, variable-or-signal)` pair
is its own temporal child universe over the same horizon. Every child uses its
own observations and must satisfy the native square-root count floor plus
early/middle/late coverage. WorldGuard sends that effective floor to SkillGuard
as a content-addressed per-object receipt; a fixed SkillGuard ratio must not
replace it. The native examples are 32 representative points for 1,000 steps
and 100 for 10,000 steps, unless a target declares a stricter floor. Meeting
the count and early/middle/late phases is still insufficient when one
normalized gap exceeds the native maximum-gap bound.

## ModelNode Fields

- `model_id`
- `model_version`
- `model_kind`
- `authority`
- `freshness_status`: `current`, `stale`, or `unknown`
- `contract`: optional embedded `GuardContract`

## ModelEdge Fields

- `edge_id`
- `source_model_id`
- `target_model_id`
- `relation`
- `output_refs`
- `allowed_use`
- `forbidden_use`
- `read_only`
- `requires_current_source`

If `allowed_use` is non-empty, the output refs consumed by the edge must stay inside it. Output outside that list is a handoff boundary violation.

Allowed relation values:

- `parent_child`
- `depends_on`
- `refines`
- `replaces`
- `conflicts_with`
- `consumes_output_of`
- `same_world_version`
- `supersedes`

## WorldStateSnapshot Fields

- `snapshot_id`
- `model_ids`
- `status`
- `notes`

Snapshots are optional metadata for version/state context. They do not replace node freshness or edge handoff checks.

## MeshReport Fields

- `status`
- `structural_status`
- `semantic_status`: `PASS`, `FAIL`, `GAP`, `BOUNDARY_ONLY`, or `NOT_RUN`
- `provider_status`: `AVAILABLE`, `UNAVAILABLE`, `MIXED`, or `NOT_REQUIRED`
- `rollout_status`
- `node_reports`
- `semantic_receipts`
- `findings`
- `aggregate_ledger`
- `scope_limits`
- `depth_receipt`

The aggregate ledger must include child Guard ledgers and mesh-level ledger entries.
The legacy `status` is a conservative projection. Structural `PASS` cannot
become aggregate `PASS` when semantic execution did not run, a required
provider was unavailable, or an executor reported a gap or boundary.

Each semantic receipt must preserve the executor id, Guard owner, input fields,
output fields, supported semantic subset, unsupported boundary, consumed
inputs, findings, and skipped reason. The depth receipt binds those child
receipts to the mesh fingerprint and explicit claim boundary.

The depth receipt also preserves the coverage fingerprint, structured claim
atoms, derived/declared/missing Guards, expected/executed/skipped nodes and
children, discovered/declared/excluded node reconciliation, per-variable/signal
temporal results, quantitative coverage, predictive gaps, and
`predictive_claim_licensed`. Bounded semantic `PASS` does not imply predictive
readiness. Semantic execution is always required, and a missing contract on any
expected node is a `GAP`. The retired `closure_profile` field and
`--closure-profile` selector are rejected rather than used to skip semantics.

## Non-Goals

WorldGuard core ModelMesh does not own domain concepts such as chapter, scene, paragraph, literature item, quest, level, or task arc. Upper-layer adapters may translate those concepts into model nodes, edges, and claims.
