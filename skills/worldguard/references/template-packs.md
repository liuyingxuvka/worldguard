# WorldGuard Validating Template Packs

Use this construction layer before manually assembling a new `GuardContract` or `ModelMeshContract`. It reduces repeated shape errors without becoming a Guard router or semantic executor.

## Fixed boundary

- WorldGuard owns every pack, applicability fact, field fragment, validator binding, and receipt meaning.
- SkillGuard may supervise the declared WorldGuard check but never selects a pack or interprets Guard semantics.
- A template does not derive required Guards, choose a task purpose or failure id, create native good/bad evidence, execute the claim, or license prediction.
- `build_calibration_task_purpose_declaration` remains tests/examples-only. A real task supplies its own declaration.

## Selection

Call `builtin_template_registry().select(contract_kind, fact_ids)` before building:

- `base_template`: zero candidates matched; use the unique base scaffold and preserve that bounded outcome.
- `selected`: exactly one candidate matched; compose it after the base scaffold.
- `ambiguous`: several candidates matched; show every candidate id and block. Do not use order, scores, filenames, or AI preference to choose.
- `no_match`: no candidate and no base exist; block with `TEMPLATE_NO_MATCH_AND_BASE_MISSING`.

For a Guard-specific child, pass one exact fact such as `guard:EventGuard` only after WorldGuard/caller context selected that Guard. For a ModelMesh coverage scaffold, pass `coverage:bounded` or `coverage:predictive`. Passing mutually matching facts is deliberately ambiguous.

## Built-in packs

| Contract kind | Base slots | Candidate fact and added slot |
|---|---|---|
| `guard_contract` | `contract_id`, `run_id`, `claim_id`, `claim_text`, `target_guards`, `requested_semantics`, `claim_atoms`, `model_id`, `model_version`, `guard_purpose_declarations` | `guard:EventGuard` → `event_inputs`; `AgentGuard` → `agent_inputs`; `SpaceGuard` → `space_inputs`; `ResourceGuard` → `resource_inputs`; `CausalGuard` → `causal_inputs`; `ConflictGuard` → `conflict_inputs`; `NormGuard` → `norm_inputs` |
| `model_mesh_contract` | `mesh_id`, `run_id`, `nodes`, `expected_model_node_ids` | `coverage:bounded` or `coverage:predictive` adds only the explicit coverage profile |

The Guard base intentionally does not invent `inputs`; a no-match base can be structurally valid yet later evaluate to `GAP`. Guard candidates add only the appropriate input slot. The caller still writes all task-local purpose declarations and evidence.

## Build

Use:

```python
from worldguard import GUARD_CONTRACT_KIND, build_template_instance, builtin_template_registry

instance = build_template_instance(
    builtin_template_registry(),
    contract_kind=GUARD_CONTRACT_KIND,
    fact_ids=["guard:EventGuard"],
    slot_bindings={
        "contract_id": task_contract_id,
        "run_id": run_id,
        "claim_id": claim_id,
        "claim_text": claim_text,
        "target_guards": ["EventGuard"],
        "requested_semantics": ["event"],
        "claim_atoms": claim_atoms,
        "model_id": model_id,
        "model_version": model_version,
        "guard_purpose_declarations": task_owned_declarations,
        "event_inputs": task_owned_events,
    },
)
```

Supply every discovered slot exactly once. Missing slots block with `TEMPLATE_SLOT_MISSING`; extra bindings block with `TEMPLATE_BINDING_UNUSED`. Callers cannot overlay arbitrary fields after composition because that would bypass field ownership and identity.

## Composition and freshness

Each fragment's `owned_field_ids` must exactly equal its payload leaves. Equal fields and ancestor/descendant overlaps block with `TEMPLATE_FIELD_OWNERSHIP_CONFLICT`; there is no last-writer-wins route. The manifest fingerprint covers its schema, applicability, fragments, validators, and claim boundary. A changed manifest or nested fragment with an old fingerprint is stale and rejected.

## Native validation and receipt

Guard instances run canonical GuardContract shape validation plus the existing claim-derived task-purpose proof. ModelMesh instances run canonical mesh validation plus the same proof for embedded Guard contracts. Unknown validator ids block; no fallback validator is selected.

Retain the receipt's registry, selection, pack, composition, binding, output, validator, and final instance fingerprints. Its claim boundary is construction integrity only. Continue through `run_worldguard` or `run_model_mesh`, target-native depth evaluation where required, and the current SkillGuard declared-check closure before making a broader conclusion.

## Target-owned neutral SkillGuard projection

When SkillGuard needs a neutral catalog for the template route, WorldGuard—not SkillGuard—must author it from the current native registry:

```python
from worldguard import (
    GUARD_CONTRACT_KIND,
    build_skillguard_target_template_projection,
    builtin_template_registry,
)

registry = builtin_template_registry()
projection = build_skillguard_target_template_projection(
    registry,
    contract_kind=GUARD_CONTRACT_KIND,
    fact_ids=["guard:EventGuard"],
    native_registry_fingerprint=registry.registry_fingerprint,
)
```

The adapter validates the current registry, calls its native selector and each manifest's native applicability predicate, and emits one row for every manifest in the requested contract-kind family. A GuardContract projection therefore includes its one base plus all seven current Guard candidates; a ModelMeshContract projection includes its one base plus both coverage candidates. The eligible booleans equal the current native selection candidate set. A many-match request keeps every matching candidate eligible so the neutral central selector blocks on the WorldGuard-authored conflicts; it never ranks words or chooses a different winner.

The root fields are closed and exact: `schema_version`, `target_id`, `native_owner_id`, `family_id`, `route_id`, `request_fingerprint`, `catalog`, `applicability_results`, and `claim_boundary`. The target emits unsealed `skillguard.target_template_projection.v1`, `skillguard.template_catalog.v1`, and `skillguard.template_manifest.v1` specifications. It intentionally omits `catalog_digest` and `manifest_digest`; current central SkillGuard validates and seals those neutral identities downstream.

Every artifact content-template hash binds the native manifest fingerprint. Builder and validator content hashes bind their current WorldGuard implementation source. The request fingerprint binds the exact registry, native selection, contract kind, route, and normalized facts. Unknown root fields, a route other than `worldguard.template_pack_builder`, incomplete/duplicate candidate accounting, missing explicit parameter types, or a stale caller-supplied registry fingerprint block before projection.

This projection is interchange plumbing, not a new semantic contract. SkillGuard may validate exact neutral fields, seal digests, and supervise the existing native check; it may not infer applicability, add a template, change eligibility, choose a Guard, or reinterpret a WorldGuard result.
