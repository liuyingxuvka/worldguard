# WorldGuard ModelMesh Model-Test Alignment

Route: `model_test_alignment`

## Model Obligations

| Obligation id | Owner code contract | Required test evidence |
|---|---|---|
| `mesh_load_contract` | `worldguard.mesh.ModelMeshContract.from_dict` | loads nodes, edges, snapshots |
| `mesh_preserve_child_reports` | `worldguard.mesh.run_model_mesh` | child `GAP` preserved; ledgers aggregate |
| `mesh_authority_boundary` | `worldguard.mesh.run_model_mesh` | excluded semantic returns `BOUNDARY_EXCEEDED` |
| `mesh_forbidden_handoff` | `worldguard.mesh.run_model_mesh` | forbidden output returns `FAIL` |
| `mesh_allowed_handoff_boundary` | `worldguard.mesh.run_model_mesh` | output outside non-empty `allowed_use` returns `BOUNDARY_EXCEEDED` |
| `mesh_stale_source` | `worldguard.mesh.run_model_mesh` | stale current-required source returns `GAP` |
| `mesh_cycle_detection` | `worldguard.mesh.run_model_mesh` | dependency cycle returns `FAIL` |
| `mesh_cli_json` | `worldguard.cli.main` | `mesh-check --mesh` emits report JSON |
| `mesh_skill_sync` | `skills/worldguard` + installed copy | repository/installed hash and helper command checks |

## Alignment Expectations

- Tests must exercise the public dataclass/dict/CLI surfaces, not only internal helpers.
- Mesh tests must not count single-contract happy paths as mesh closure proof.
- Existing `python -m pytest` remains the broad regression command.
- Existing fuel-cell example remains a unit/runtime compatibility check, not mesh proof.

## Current Evidence

- `python -m pytest -q`: 24 passed.
- `openspec validate add-worldguard-model-mesh-core --strict`: valid.
- `python -m worldguard.examples.fuel_cell --check`: `ok=true`; expected aggregate status remains `FAIL`; claim statuses remain `PASS,PASS,FAIL`.
- `python -m worldguard.cli mesh-check --mesh examples\model_mesh\basic_mesh.yaml`: status `PASS`; findings empty.
- `python <codex-home>\skills\worldguard\scripts\run_worldguard_check.py --example fuel_cell`: `ok=true`.
- `python <codex-home>\skills\worldguard\scripts\run_worldguard_check.py --mesh examples\model_mesh\basic_mesh.yaml`: status `PASS`; findings empty.
- Repository/installed skill sync: `SKILL.md`, helper script, and six reference files have matching SHA256 hashes.
- Public API import: `worldguard.__version__ == 0.1.0`; `ModelMeshContract`, `MeshReport`, and `run_model_mesh` import from `worldguard`.
