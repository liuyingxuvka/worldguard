# Handoff Contracts

Handoff contracts define how one model node may consume another model node's output.

## Required Fields

- `edge_id`
- `source_model_id`
- `target_model_id`
- `relation`
- `output_refs`
- `allowed_use`
- `forbidden_use`
- `read_only`
- `requires_current_source`

## Rules

- Handoffs are read-only.
- Downstream nodes may not mutate upstream reports, fill upstream gaps, delete upstream counterexamples, or relabel upstream statuses.
- If `requires_current_source` is true and the source node is stale or unknown, return `GAP`.
- If any `output_refs` item is listed in `forbidden_use`, return `FAIL`.
- If `allowed_use` is non-empty and any `output_refs` item is outside it, return `BOUNDARY_EXCEEDED`.
- If a source or target node id is missing, return `GAP`.
- Dependency cycles return `FAIL`.

## Relation Meanings

- `parent_child`: source is a parent or child model boundary.
- `depends_on`: target depends on source evidence.
- `refines`: target narrows or deepens source.
- `replaces`: target replaces source; old source use needs disposition.
- `conflicts_with`: source and target expose incompatible claims.
- `consumes_output_of`: target consumes named source outputs.
- `same_world_version`: source and target belong to the same state/version.
- `supersedes`: source is newer and supersedes target or target's prior evidence.

## Forbidden Shortcuts

- Do not let a child `PASS` become parent `PASS` without mesh closure.
- Do not let a downstream `PASS` repair upstream `GAP`.
- Do not treat stale evidence as current evidence without an explicit compatibility rule.
