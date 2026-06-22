# WorldGuard ModelMesh Field Lifecycle Review

Route: `field_lifecycle_mesh`

## Field Boundary

Boundary: new runtime dataclass/dict fields, CLI payload fields, reference prompt fields, and test fixture fields introduced for generic WorldGuard ModelMesh core.

## Parent Groups

| Group id | Boundary | Owner |
|---|---|---|
| `mesh_contract` | top-level mesh identity and topology | `worldguard.mesh` |
| `mesh_node` | model node identity, version, authority, freshness, optional unit contract | `worldguard.mesh` |
| `mesh_authority` | owned/excluded semantics and scope limits | `worldguard.mesh` |
| `mesh_edge` | model relationship and handoff contract | `worldguard.mesh` |
| `mesh_snapshot` | optional state/version metadata | `worldguard.mesh` |
| `mesh_report` | mesh status, child reports, findings, aggregate ledger | `worldguard.mesh` |

## Behavior-Bearing Fields

| Field id | Owner | Readers | Writers | Lifecycle | Projection |
|---|---|---|---|---|---|
| `mesh_id` | `worldguard.mesh` | CLI, tests, report | mesh loader | new | mesh identity |
| `schema_version` | `worldguard.mesh` | CLI, tests | mesh loader | new | compatibility |
| `run_id` | `worldguard.mesh` | ledgers, report | mesh loader | new | traceability |
| `nodes.*.model_id` | `worldguard.mesh` | edge checks, reports | mesh loader | new | node identity |
| `nodes.*.model_version` | `worldguard.mesh` | reports, freshness checks | mesh loader | new | version evidence |
| `nodes.*.model_kind` | `worldguard.mesh` | reports | mesh loader | new | model classification |
| `nodes.*.authority.owns` | `worldguard.mesh` | authority check | mesh loader | new | owned semantics |
| `nodes.*.authority.excludes` | `worldguard.mesh` | authority check | mesh loader | new | boundary evidence |
| `nodes.*.authority.scope_limits` | `worldguard.mesh` | reports | mesh loader | new | claim boundary |
| `nodes.*.freshness_status` | `worldguard.mesh` | edge freshness check | mesh loader | new | stale/current gate |
| `nodes.*.contract` | `worldguard.mesh`, `worldguard.contracts` | kernel | mesh loader | new | optional unit Guard execution |
| `edges.*.edge_id` | `worldguard.mesh` | reports, tests | mesh loader | new | edge identity |
| `edges.*.source_model_id` | `worldguard.mesh` | edge checks | mesh loader | new | source lookup |
| `edges.*.target_model_id` | `worldguard.mesh` | edge checks | mesh loader | new | target lookup |
| `edges.*.relation` | `worldguard.mesh` | cycle and handoff checks | mesh loader | new | topology relation |
| `edges.*.output_refs` | `worldguard.mesh` | handoff checks | mesh loader | new | consumed output refs |
| `edges.*.allowed_use` | `worldguard.mesh` | handoff checks | mesh loader | new | permitted output use |
| `edges.*.forbidden_use` | `worldguard.mesh` | handoff checks | mesh loader | new | forbidden output use |
| `edges.*.read_only` | `worldguard.mesh` | handoff checks | mesh loader | new | mutation guard |
| `edges.*.requires_current_source` | `worldguard.mesh` | freshness check | mesh loader | new | stale-source gate |
| `snapshots.*.snapshot_id` | `worldguard.mesh` | reports | mesh loader | new | optional state identity |
| `findings.*` | `worldguard.mesh` | CLI, tests | mesh runner | new | non-pass evidence |
| `node_reports.*` | `worldguard.mesh` | CLI, tests | mesh runner | new | child report preservation |
| `aggregate_ledger` | `worldguard.mesh` | CLI, tests | mesh runner | new | ledger preservation |

## Old Field Disposition

- No existing `GuardContract` fields are removed or renamed.
- Existing `dependencies.upstream_results` remains the unit-kernel handoff field; ModelMesh edges are a separate topology layer.
- No domain adapter fields are accepted in the core mesh schema as canonical behavior fields.

## Contract Exhaustion Handoff

Missing, empty, wrong-type, unknown relation, missing source node, missing target node, stale source, forbidden output, mutable edge, duplicate node id, and dependency cycle cases must be covered by runtime checks and tests before broad confidence.
