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
- `node_reports`
- `findings`
- `aggregate_ledger`
- `scope_limits`

The aggregate ledger must include child Guard ledgers and mesh-level ledger entries.

## Non-Goals

WorldGuard core ModelMesh does not own domain concepts such as chapter, scene, paragraph, literature item, quest, level, or task arc. Upper-layer adapters may translate those concepts into model nodes, edges, and claims.
