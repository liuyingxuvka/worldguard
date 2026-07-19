## MODIFIED Requirements

### Requirement: Installable WorldGuard Runtime
The system SHALL provide an installable Python package named `worldguard` with contract, ledger, Guard runner, Kernel, CLI, ModelMesh, example, and test surfaces.

#### Scenario: Package import works
- **WHEN** a local environment runs `python -c "import worldguard; print(worldguard.__version__)"`
- **THEN** the command succeeds and prints a version string.

#### Scenario: Package import exposes mesh API
- **WHEN** a local environment imports `worldguard`
- **THEN** `ModelMeshContract`, `MeshReport`, and `run_model_mesh` are available from the public runtime API.

### Requirement: Read-only Kernel Handoff
The Kernel and ModelMesh runtime SHALL preserve upstream results as read-only dependencies and aggregate child ledgers without rewriting child status, missing slots, boundaries, or counterexamples.

#### Scenario: Upstream GAP cannot be repaired downstream
- **WHEN** EventGuard returns `GAP` and NormGuard depends on the missing event fact
- **THEN** the aggregate report remains non-pass and the EventGuard gap remains visible in the aggregate ledger.

#### Scenario: Mesh handoff cannot repair child gap
- **WHEN** a node-level Guard result returns `GAP` and a downstream mesh edge consumes that node
- **THEN** the mesh report remains non-pass and preserves the original child gap ledger.

## ADDED Requirements

### Requirement: Runtime CLI Checks
The runtime SHALL provide CLI entrypoints for both single-contract checks and mesh checks.

#### Scenario: Single contract CLI remains compatible
- **WHEN** `worldguard check --example fuel_cell` runs
- **THEN** the existing fuel-cell toy check still succeeds.

#### Scenario: Mesh CLI runs
- **WHEN** `worldguard mesh-check --mesh <path>` runs
- **THEN** it emits a JSON `MeshReport`.
