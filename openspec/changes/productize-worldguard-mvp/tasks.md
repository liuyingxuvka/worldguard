## 1. OpenSpec And FlowGuard Setup

- [x] 1.1 Create OpenSpec proposal, design, specs, and implementation checklist for the productized WorldGuard MVP.
- [x] 1.2 Record FlowGuard structure, field lifecycle, and development freshness notes without touching FlowPilot process debt.

## 2. Package Skeleton And Contracts

- [x] 2.1 Add `pyproject.toml`, `.gitignore`, `README.md`, and package skeleton.
- [x] 2.2 Implement `worldguard.status`, `worldguard.ledgers`, `worldguard.contracts`, and `worldguard.reports`.
- [x] 2.3 Add contract and ledger tests for canonical fields, aliases, read-only ledgers, and non-pass evidence.

## 3. Guards And Kernel

- [x] 3.1 Implement seven Guard runner modules behind the common `run(contract)` interface.
- [x] 3.2 Implement Kernel dispatch, read-only handoff, aggregation, and report serialization.
- [x] 3.3 Add per-Guard fixture tests covering PASS, FAIL, GAP, and BOUNDARY_EXCEEDED.
- [x] 3.4 Add Kernel handoff and aggregate ledger tests.

## 4. Examples, CLI, And Productization

- [x] 4.1 Copy current fuel-cell v5 fixture material into `examples/fuel_cell/` without deleting historical evidence.
- [x] 4.2 Implement `worldguard.examples.fuel_cell --check` and `worldguard.cli check`.
- [x] 4.3 Add fuel-cell replay tests and package-data coverage.
- [x] 4.4 Add public documentation and packaging exclusions for route-local evidence.

## 5. Codex Skill Installation

- [x] 5.1 Create local `C:\Users\liu_y\.codex\skills\worldguard` with `SKILL.md`, references, `agents/openai.yaml`, and helper script.
- [x] 5.2 Validate skill metadata and run the helper script against the installed package.

## 6. Validation, Install, And Local Git Sync

- [x] 6.1 Run the WorldGuard test suite and CLI/example checks.
- [x] 6.2 Install the package locally in editable mode and verify the installed import/version.
- [x] 6.3 Initialize local Git if needed, ensure ignored evidence is not committed, and create a local commit for productized files.
- [x] 6.4 Run final completion audit against the user objective and OpenSpec tasks.
