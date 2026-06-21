# WorldGuard

WorldGuard is a model-first guard framework for checking whether a world claim is supported by an explicit model, contradicted by it, missing required inputs, or outside the current Guard boundary.

This repository is now organized as a runnable MVP:

- `worldguard/` contains the installable Python runtime.
- `tests/` contains contract, ledger, Guard, Kernel, and example replay checks.
- `examples/fuel_cell/` contains a toy fixture copied from the accepted repair-v5 evidence.
- `docs/` contains productization and FlowGuard notes.
- `openspec/` contains the change record for this productization pass.
- `skills/worldguard/` contains the repository copy of the local Codex skill installed at `C:\Users\liu_y\.codex\skills\worldguard`.

The fuel-cell material is only a toy fixture. It does not validate real fuel-cell physics, law, safety, compliance, deployment readiness, market truth, or strategy.

## Quick Check

```powershell
python -m pip install -e .
python -m pytest
python -m worldguard.examples.fuel_cell --check
python -m worldguard.cli check --example fuel_cell
```

If your Python user scripts directory is on `PATH`, the console command `worldguard check --example fuel_cell` is also available.

## Core Rules

- Every claim must be tied to a structured `GuardContract`.
- `PASS`, `FAIL`, `GAP`, and `BOUNDARY_EXCEEDED` must not be collapsed.
- Non-pass results must carry missing slots, errors, boundary traces, or counterexamples.
- Kernel handoff is read-only: downstream Guards may read upstream results but may not repair or relabel them.
- Aggregate ledgers must preserve child Guard evidence.
