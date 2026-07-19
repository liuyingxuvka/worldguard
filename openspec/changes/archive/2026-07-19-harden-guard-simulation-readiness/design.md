## Design

WorldGuard readiness is modeled as:

`Claim model + mesh contract + skill contract + installed package -> executable check result`

The Guard proof path is modeled as:

`Family native-oracle catalog -> AI declares task-model-instance purpose -> prove selected good/bad cases -> freeze exact declaration -> construct formal Guard candidate -> verify exact binding -> unit/semantic proof`

The fix is deliberately small. The package keeps the existing `worldguard.cli:main` implementation and exposes it through `worldguard.__main__`. This avoids a second CLI path.

Author readiness is checked through the existing SkillGuard contract scripts.
Those contracts and receipts remain under the maintainer source only. Installed
readiness is a separate target-owned consumer check: one
`consumer-release.json` binds the exact source projection and installed file
inventory, every declared byte hash must match, and the installed tree must
contain zero `.skillguard` paths. Missing or drifting current authority blocks;
there is no source-reader fallback, installed author-control reader, alias, or
alternate success route.

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

Each Guard now reads exactly one current input location: events from
`inputs.events`, agent records from `inputs.beliefs`, spatial relations from
`inputs.spatial_relations`, resources from `inputs.resources`, causal data from
`inputs.causal_model`, conflict data from `inputs.game_model`, norms and facts
from `inputs.norms` and `inputs.facts`, and predictive observations from
`inputs.variable_observations`. Known former locations are rejected while
loading the contract. Upgrade AI must rewrite old files directly; normal
runtime has no old reader, source priority, or alternate route.

Template selection also has one terminal rule: exactly one current candidate
may compose with the shared base fragment. Zero candidates block with
`TEMPLATE_SELECTION_NO_MATCH`; multiple candidates block as ambiguous. The
base fragment is never independently eligible.

Validation uses two independent BehaviorCommitmentLedger shards. The current
input shard binds only current-input code, its semantic model, and its focused
tests. The template-selection shard binds only template code, its executable
FlowGuard model, documentation, and focused tests. Each shard writes one
immutable receipt over its exact inputs. The parent aggregation launches no
test process and passes only when both current shard receipts replay exactly.

SkillGuard check dependencies mean receipt consumption, not desired order.
WorldGuard check owners that merely run later in the release process have no
`depends_on_check_ids` edge. A check invalidates only from its compiler-owned
component selectors, exact target-input roles, genuine upstream receipt
consumption, toolchain, or environment. Template checks cover only template
obligations; topology obligations remain with the topology owner.

The release process is one linear path:

`affected checks -> freeze all identities -> one foreground final full owner -> parent aggregation -> SkillGuard read-only replay -> official OpenSpec strict validation -> archive -> one commit/push/tag/Release -> read-only identity audit`

Task checkboxes, progress reports, receipts, and GitHub publication state are
outputs of this process. They are not source freshness inputs and do not cause
the final owner to rerun.

OpenSpec owns only its proposal, design, specification, task validation, and
archive lifecycle. The WorldGuard release gate keeps a target-owned immutable
reference to the SkillGuard aggregation, but OpenSpec does not import that
receipt, register SkillGuard as a provider, use a portable adapter, or execute
and resume a validation owner.

## Validation

- Run package tests.
- Run `python -m worldguard --help`.
- Run fuel-cell example and model-mesh example.
- Reinstall editable package and verify import path plus metadata version.
- Re-run SkillGuard author checks on the source and independently verify the
  target-owned installed consumer manifest and clean projection.
- Run focused missing/stale/order/universe-shrink candidate regressions and the
  executable FlowGuard candidate-order hazard model.
- Add one-failure and multi-failure task declarations plus missing, empty,
  wrong-Guard, unknown-oracle, incomplete-proof, and family-only regressions.
- Add retired-path and no-template-candidate regressions proving that normal
  runtime cannot succeed through an old field or base-template route.
- Prove the two BCL shards invalidate independently and that parent aggregation
  consumes their current receipts without executing tests.
- Prove the WorldGuard SkillGuard plan is affected-only before the final gate,
  then execute exactly one frozen foreground full owner and replay its receipt.
- Archive before publication; after publication, verify local commit, remote
  branch, annotated tag, GitHub Release, source version, editable package, and
  installed consumer identities without rerunning validation.
