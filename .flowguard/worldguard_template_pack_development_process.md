# WorldGuard Template-Pack DevelopmentProcessFlow

Route: `development_process_flow`

## Modes

| Mode | Status | Reason / delegate |
|---|---|---|
| `plan_detailing` | not needed | OpenSpec proposal/design/spec/tasks and verification contract already provide structured rows. |
| `strategy_selection` | not needed | Existing ownership and hard semantic boundaries select one direct additive child route; no equivalent competing execution route remains. |
| `agent_workflow` | not needed | Work is local and deterministic with no external side effect; tool order is frozen below. |
| `execution_freshness` | active | Source, derived SkillGuard contracts, target projection, and focused/affected receipts must stay identity-bound. The earlier full-suite receipt is historical after this extension and is not rerun. |

## SpecWorkPackage

- provider: `openspec@1.6.0`
- work package: `add-worldguard-template-pack-builder`
- behavior plane: `development_process`
- provider owns product behavior: `false`
- product owners: `worldguard.contracts`, `worldguard.guard_model_contract`, `worldguard.mesh`, and the additive `worldguard.template_packs` construction child
- reconciliation authority: `openspec/changes/add-worldguard-template-pack-builder/verification-contract.yaml`

| Provider task group | FlowGuard obligation | Primary validation owner |
|---|---|---|
| 1.1 | reuse existing owners; no parallel semantics | `owner.worldguard.template-pack-preflight` |
| 1.2 | 0/1/many, stale, conflict, validator failure | `owner.worldguard.template-pack-flow-model` |
| 1.3 | field/process/freshness accounting | preflight + verification-contract review |
| 2.1–2.5 | manifest, selection, composition, slots, validators, built-ins | `owner.worldguard.template-pack-focused-tests` |
| 3.1–3.3 | positive/counterexample/parity coverage | `owner.worldguard.template-pack-focused-tests` |
| 4.1–4.2 | skill/contract authority and deterministic compile | `owner.worldguard.skillguard-contract` |
| 5.1 | affected focused closure | exact focused owners, once each |
| 5.2 | stable integration snapshot | `owner.worldguard.template-pack-full-suite`, exactly once |
| 5.3 | OpenSpec receipt consumption/reporting | receipt consumer; it never reruns an owner |
| 6.1 | extend existing model/field/process ownership for neutral projection | `owner.worldguard.template-pack-preflight` + `owner.worldguard.template-pack-flow-model` |
| 6.2–6.3 | exact target projection, native identity, and focused regressions | `owner.worldguard.template-pack-focused-tests` |
| 6.4–6.5 | bundled runtime, native check, current contract trio, read-only central compile | `owner.worldguard.template-pack-native-check` + `owner.worldguard.skillguard-contract` |
| 6.6 | scoped evidence/report and strict provider validation | OpenSpec consumer; no second full-suite owner |

## Artifact And Invalidation Map

| Component | Owner | Directly invalidates |
|---|---|---|
| OpenSpec proposal/design/spec/verification contract | OpenSpec work package | preflight/model/implementation plan consumers only |
| `worldguard/template_packs.py` | WorldGuard template child | focused template tests, bundle parity, final full suite |
| bundled `template_packs.py` | WorldGuard skill runtime projection | bundle parity, SkillGuard compile/check, final full suite |
| template FlowGuard model | FlowGuard model owner | FlowGuard model receipt only |
| field lifecycle record | FieldLifecycleMesh | field review and plan mapping only |
| WorldGuard SKILL/reference | WorldGuard skill owner | skill validation and SkillGuard compile/check |
| SkillGuard contract-source | WorldGuard declared-check owner | compiled contract and check manifest projection |
| compiled contract/check manifest | SkillGuard compiler | contract currentness check; never target semantic meaning |
| `tasks.md`, verification report, owner receipts, logs, caches | evidence output owners | no source owner; never invalidates or relaunches a producer |

Unknown or ambiguous source mapping blocks instead of broadening to run-all. The one full-suite owner runs only after every governed source and tool identity is stable. A timeout or interruption is non-reusable until zero descendants is confirmed.

For the projection extension, changes to `worldguard/template_packs.py`, its bundled mirror, focused tests, native check, reference, and already-owned contract surfaces invalidate the earlier full-suite receipt. The parent instruction explicitly forbids executing a second full-suite owner, so this continuation makes only focused/affected and cross-contract claims. It must report the full-suite owner as skipped/stale for the extension, not reuse the prior receipt or silently broaden confidence.

## Claim Boundary

This continuation can establish that the target-owned neutral projection is modeled, implemented, focused/affected-tested, bundle-synchronized, current-contract compiled, and accepted by the read-only central interchange compiler for one frozen source snapshot. The earlier snapshot had one full-suite pass, but that receipt is not current for the projection edits and no second full suite is claimed. Nothing here proves that a template-created world claim is true, semantically PASS, predictive, installed, released, archived, or safe beyond the existing WorldGuard native receipt and SkillGuard closure boundaries.
