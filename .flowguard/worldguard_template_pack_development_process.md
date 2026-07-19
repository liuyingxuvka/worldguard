# WorldGuard v0.4 DevelopmentProcessFlow

Route: `development_process_flow`

## Current Work Package

- provider: official OpenSpec
- change: `harden-guard-simulation-readiness`
- behavior plane: `development_process`
- product owners: `worldguard.contracts`,
  `worldguard.guard_model_contract`, `worldguard.mesh`, and
  `worldguard.template_packs`
- reconciliation authority:
  `openspec/changes/harden-guard-simulation-readiness/verification-contract.yaml`

The completed `add-worldguard-template-pack-builder` change is historical
context only. Its former zero-candidate base-template behavior is superseded by
the current change and is not runtime, model, or release authority.

## Modes

| Mode | Status | Reason |
|---|---|---|
| `plan_detailing` | active | OpenSpec fixes the exact requirements, tasks, and receipt-consumer boundary. |
| `strategy_selection` | resolved | Use exact affected owners, then one final frozen full owner; no run-all fallback exists. |
| `agent_workflow` | active | Preserve peer changes, serialize shared compiler/install locks, and keep the final full owner in the foreground. |
| `execution_freshness` | active | Source, toolchain, impact plan, target inputs, installation, and receipts have separate identities. |

## Linear Release Path

| Stage | Required state | Execution owner |
|---|---|---|
| 1. Requirements | current proposal, design, specs, tasks, and verification contract | OpenSpec |
| 2. Affected repair | current-only inputs, no-match template semantics, BCL shard split, exact SkillGuard ownership | target source owners |
| 3. Generated authority | governed source frozen; compiled contract and manifest regenerated once | SkillGuard compiler |
| 4. Affected validation | only changed FlowGuard models, BCL shards, package tests, and SkillGuard owners execute | exact affected owners |
| 5. Installation | clean consumer staged, activated transactionally, and checked for exact parity | WorldGuard installer |
| 6. Final freeze | source, toolchain, impact plan, environment, target inputs, installation, and router identities frozen | DevelopmentProcessFlow |
| 7. Final full | exactly one foreground full TestMesh owner reaches a terminal result | one explicit execution owner |
| 8. Consumption | zero-process aggregation, receipt-only OpenSpec verification, then archive | receipt consumers and OpenSpec |
| 9. Publication | one commit, branch push, annotated tag, and GitHub Release | release owner |
| 10. Identity audit | compare local commit, remote branch, tag, Release, version, package, and installed projection | read-only audit |

Publication never precedes archive and never starts a validation owner. A
failed publication identity check blocks the release claim; it does not edit
source, invoke `--resume`, or manufacture a second release.

## Artifact And Invalidation Map

| Component | Directly invalidates |
|---|---|
| current input runtime, semantic model, or focused tests | current-input BCL shard and mapped SkillGuard/package owners |
| template runtime, executable template model, template guidance, or focused tests | template BCL shard and mapped SkillGuard/package owners |
| WorldGuard SkillGuard contract source | compiled contract, check manifest, and mapped owner plan |
| compiler or shared validation runtime | exact affected owners; final full admission is required when declared by policy |
| installation projection | transactional install and installed-currentness only |
| OpenSpec proposal/design/spec/verification contract | planning and receipt-consumer mapping only |
| `tasks.md`, reports, receipts, logs, caches, and publication metadata | no source owner; never invalidates or relaunches a producer |

Every explicit selector must match independently. An unknown or ambiguous
mapping blocks before execution. `depends_on_check_ids` is reserved for an
owner that consumes an upstream immutable receipt; desired ordering belongs to
this process model and is not receipt identity.

## BCL Shards

- `input` binds only current-input code, its semantic model, and focused input
  tests.
- `template` binds only template code, its executable model and guidance, and
  focused template tests.
- `aggregate` starts zero tests and succeeds only when both exact shard
  receipts replay as current.

Neither shard may consume the other shard's receipt. A change in one shard
cannot broaden into both shards or a full-suite run.

## Timeout And Interruption

A timed-out or interrupted owner is non-reusable until its entire descendant
process tree is confirmed at zero. Retry uses the same declared path with a
realistic timeout; there is no alternate command, background final owner,
scheduled-task owner, or compatibility route.

## Claim Boundary

This process can prove the exact v0.4 source, affected evidence, clean installed
consumer, one frozen final parent receipt, OpenSpec archive, and publication
identity. It does not prove that a template-created world claim is factually
true, empirically accurate, universally predictive, or safe outside the exact
WorldGuard native evidence boundary.
