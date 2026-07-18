## 1. Topology Contract

- [x] 1.1 Add the exact seven-row internal Guard route contract with bounded prediction semantics.
- [x] 1.2 Add a target-native checker for one public entry, exact runtime registries, terminal statuses, and bundled-runtime parity.

## 2. Skill and Model

- [x] 2.1 Update WorldGuard skill/reference guidance to distinguish one public entry from seven complete internal routes.
- [x] 2.2 Extend the portable FlowGuard model with the seven prediction/response/validation/terminal child flows.
- [x] 2.3 Add focused positive and negative topology tests.
- [x] 2.4 Rebind the existing claim-derived FlowGuard alignment directly to the current `execution_depth.py` authority and reject the retired path.

## 3. Maintenance Contract

- [x] 3.1 Add a WorldGuard topology obligation and target-native check to the SkillGuard author contract.
- [x] 3.2 Recompile SkillGuard source and generated contracts after source freeze.

## 4. Verification

- [x] 4.1 Run the topology checker, target-native Guard checks, FlowGuard checks, and OpenSpec strict validation.
- [x] 4.2 Run the full WorldGuard test suite and root/bundled runtime parity checks.
- [x] 4.3 Confirm no child skill/console, compatibility path, installation, global routing, Git publication, release, or FlowPilot change occurred.

## Verification Boundary

The current authoritative SkillGuard `check-skill` passes without requiring a
public maintenance section. The public skill remains free of SkillGuard
maintenance dependencies; installation, release, and publication evidence stay
outside this source-change receipt.
