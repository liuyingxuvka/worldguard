## Design

WorldGuard readiness is modeled as:

`Claim model + mesh contract + skill contract + installed package -> executable check result`

The Guard proof path is modeled as:

`Family native-oracle catalog -> AI declares task-model-instance purpose -> prove selected good/bad cases -> freeze exact declaration -> construct formal Guard candidate -> verify exact binding -> unit/semantic proof`

The fix is deliberately small. The package keeps the existing `worldguard.cli:main` implementation and exposes it through `worldguard.__main__`. This avoids a second CLI path.

Skill readiness is checked through the existing SkillGuard contract scripts. The contract text must state that duplicate SkillGuard-owned execution paths are invalid, because the route checker enforces that as the anti-bypass boundary.

`GuardContract.for_guard` remains the sole child-candidate constructor, but it
must consume an explicit declaration already present on the parent task
contract. It may not synthesize the declaration from `GUARD_MODEL_PURPOSES`.
The declaration identifies the parent task, exact child candidate, selected
Guard, model instance, plain-language prevention purpose, unsupported boundary,
and a non-empty one-or-many selected set from the WorldGuard-owned native
failure/oracle catalog. It also binds one task-local known-good and exactly one
task-local known-bad for every selected failure.

The family inventory continues to exhaust literal runtime failure codes so the
catalog cannot silently drift. That inventory is regression evidence and an
extension point, not a production declaration. A task may select any meaningful
one-or-many subset; a new failure kind requires a real WorldGuard-native code,
oracle, and family regression before it may be declared.

`run_worldguard` and `execute_semantic` reuse one WorldGuard-owned verifier;
SkillGuard only fingerprints and supervises that native check. The verifier
derives the current family catalog and the task-local declaration independently
from the constructor, rejects family-only fallback, and verifies declaration
and proof fingerprints so a broken constructor or a copied fixture cannot
approve itself.

## Validation

- Run package tests.
- Run `python -m worldguard --help`.
- Run fuel-cell example and model-mesh example.
- Reinstall editable package and verify import path plus metadata version.
- Re-run SkillGuard route checks on source and installed skill copies.
- Run focused missing/stale/order/universe-shrink candidate regressions and the
  executable FlowGuard candidate-order hazard model.
- Add one-failure and multi-failure task declarations plus missing, empty,
  wrong-Guard, unknown-oracle, incomplete-proof, and family-only regressions.
