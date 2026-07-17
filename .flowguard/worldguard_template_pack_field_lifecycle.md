# WorldGuard Template-Pack Field Lifecycle

Route: `field_lifecycle_mesh`

Boundary: WorldGuard-owned template manifest, selection, composition, slot, validator, instance-receipt, and target-owned SkillGuard-neutral projection fields introduced by `add-worldguard-template-pack-builder`. No field has an ordinary UI reader, so no UI Flow Structure admission row is required.

## Parent Groups

| Parent group | Owner | Readers | Writers | Lifecycle |
|---|---|---|---|---|
| `template_pack_manifest` | `worldguard.template_packs` | registry, selector, composer | WorldGuard pack authors/builders | new |
| `template_selection` | `worldguard.template_packs` | builder, receipt | selector only | new per build |
| `template_instance_receipt` | `worldguard.template_packs` | caller, tests, SkillGuard declared check | native builder only | immutable per build |
| `skillguard_target_template_projection` | `worldguard.template_packs` | central neutral compiler, native check | WorldGuard projection adapter only | immutable per request/native identity |
| `skillguard_template_catalog_spec` | `worldguard.template_packs` | central neutral compiler | WorldGuard projection adapter only | unsealed target specification; central digest is not target-owned |
| `skillguard_applicability_results` | `worldguard.template_packs` | central neutral compiler/selector | WorldGuard projection adapter from native selection only | exactly one row per native family manifest |

## Leaf Inventory

| Field id | Owner | Readers | Writers | Behavior projection / disposition |
|---|---|---|---|---|
| `manifest.schema_version` | `worldguard.template_packs` | registry validator | manifest builder | exact current schema; unknown/old blocks |
| `manifest.pack_id` | WorldGuard pack author | selector, receipt | manifest builder | stable pack identity |
| `manifest.pack_version` | WorldGuard pack author | registry, receipt | manifest builder | explicit content version |
| `manifest.contract_kind` | `worldguard.template_packs` | base lookup, composition, validator | manifest builder | `guard_contract` or `model_mesh_contract`; mismatch blocks |
| `manifest.is_base` | `worldguard.template_packs` | base lookup, selector | manifest builder | exactly one base per kind |
| `manifest.required_fact_ids` | WorldGuard pack author | selector | manifest builder | explicit applicability conjuncts; does not derive Guard semantics |
| `manifest.excluded_fact_ids` | WorldGuard pack author | selector | manifest builder | explicit negative applicability |
| `manifest.fragments[]` | WorldGuard pack author | composer | manifest builder | reusable scaffold only |
| `fragment.fragment_id` | WorldGuard pack author | ownership diagnostics | fragment builder | stable fragment identity |
| `fragment.owned_field_ids` | WorldGuard pack author | manifest validator, composer | fragment builder | exact equality with discovered payload leaves |
| `fragment.payload` | WorldGuard pack author | composer, slot resolver | fragment builder | canonical JSON-like scaffold |
| `manifest.native_validator_ids` | WorldGuard runtime | registry, validator runner | manifest builder | every id resolves in WorldGuard registry; no SkillGuard semantic id |
| `manifest.claim_boundary` | WorldGuard pack author | receipt, docs | manifest builder | construction-only boundary |
| `manifest.manifest_fingerprint` | `worldguard.template_packs` | registry, selection, receipt | canonical manifest builder | content hash; mismatch is stale |
| `selection.contract_kind` | caller request | selector, receipt | build request | selects only the contract family |
| `selection.fact_ids` | existing WorldGuard/caller context | selector, receipt | build request | normalized explicit facts; never inferred by template scoring |
| `selection.candidate_pack_ids` | selector | builder, diagnostics | selector | exact sorted 0/1/many set |
| `selection.outcome` | selector | builder, receipt | selector | `base_template`, `selected`, or `ambiguous` |
| `selection.selection_fingerprint` | `worldguard.template_packs` | builder, receipt | selector | binds registry, facts, candidates, and outcome |
| `slot.$slot` | WorldGuard pack author | slot resolver | fragment payload | task-local placeholder; never supplies its own value |
| `build.slot_bindings` | caller/AI task workflow | slot resolver, receipt | caller | task identity/evidence values; missing or unused blocks |
| `receipt.registry_fingerprint` | `worldguard.template_packs` | receipt consumer | builder | exact admitted registry identity |
| `receipt.pack_fingerprints` | `worldguard.template_packs` | receipt consumer | builder | exact base/selected pack identities |
| `receipt.binding_fingerprint` | `worldguard.template_packs` | receipt consumer | builder | exact task slot values |
| `receipt.output_fingerprint` | `worldguard.template_packs` | native validator, receipt consumer | builder | exact resolved contract dictionary |
| `receipt.validator_receipts` | WorldGuard native validator registry | receipt consumer | native validators | construction validation only |
| `receipt.instance_fingerprint` | `worldguard.template_packs` | caller, tests, SkillGuard check | builder | final content identity; any governed change stales it |

## Neutral Projection Leaf Inventory

The projection boundary is intentionally closed. The rows below enumerate every emitted field; `catalog_digest` and `manifest_digest` are absent because central SkillGuard owns neutral sealing after it validates this target-owned specification.

| Field ids | Owner | Readers | Writers | Behavior projection / disposition |
|---|---|---|---|---|
| `projection.schema_version` | `worldguard.template_packs` | target validator, central compiler | projection adapter | exact `skillguard.target_template_projection.v1`; old/unknown blocks |
| `projection.target_id`, `projection.native_owner_id`, `projection.family_id`, `projection.route_id` | `worldguard.template_packs` | target validator, central native-route receipt | projection adapter | exact target/owner/family/route identities; wrong route blocks |
| `projection.request_fingerprint` | `worldguard.template_packs` | central receipt/compiler | projection adapter | `sha256:` identity over current registry, selection, route, kind, and facts |
| `projection.catalog` | `worldguard.template_packs` | central catalog validator | projection adapter | exact unsealed catalog object; no alternate catalog path |
| `projection.applicability_results` | `worldguard.template_packs` | central applicability validator/selector | projection adapter | exact native inventory once each; no vocabulary inference |
| `projection.claim_boundary` | `worldguard.template_packs` | central receipts, reports | projection adapter | target semantics stay with WorldGuard |
| `catalog.schema_version`, `catalog.catalog_id`, `catalog.revision` | `worldguard.template_packs` | central catalog validator | projection adapter | exact catalog schema/id and current registry-derived revision |
| `catalog.native_owner_id`, `catalog.family_id`, `catalog.base_template_id` | `worldguard.template_packs` | central route/catalog validators | projection adapter | one family per contract kind and one current native base |
| `catalog.templates` | `worldguard.template_packs` | central catalog validator/selector | projection adapter | one unsealed manifest per current native family manifest |
| `catalog.harvest_policy.required`, `catalog.harvest_policy.allowed_dispositions` | `worldguard.template_packs` | central harvest review | projection adapter | review required; dispositions limited to `reused`, `created`, `not_harvestable` |
| `catalog.claim_boundary` | `worldguard.template_packs` | central receipts, reports | projection adapter | neutral catalog only; no semantic or release claim |
| `template.schema_version`, `template.template_id`, `template.revision`, `template.template_kind` | `worldguard.template_packs` | central manifest validator | projection adapter | exact one-to-one native manifest identity and base/profile kind |
| `template.native_owner_id`, `template.family_id`, `template.route_ids` | `worldguard.template_packs` | central route/catalog validators | projection adapter | exact native owner/family and sole current template route |
| `template.applicability_predicate_ids`, `template.forbidden_condition_ids` | `worldguard.template_packs` | central applicability validator | projection adapter from native required/excluded facts | neutral ids describe exact native predicates; they do not derive facts |
| `template.dependencies`, `template.compatible_with`, `template.conflicts_with`, `template.dominates_template_ids` | `worldguard.template_packs` | central catalog/selector | projection adapter from native base/candidate policy | candidate depends on/accepts base; peer candidates conflict; no dominance fallback |
| `template.composable`, `template.composition_order`, `template.is_validated_base` | `worldguard.template_packs` | central selector | projection adapter | mirrors native base-before-candidate construction and ambiguity blocking |
| `template.field_ownership[]` | `worldguard.template_packs` | central composition validator | projection adapter from fragment ownership | non-empty unique exact native leaf paths |
| `template.parameter_schema.type`, `template.parameter_schema.properties`, `template.parameter_schema.required`, `template.parameter_schema.additionalProperties` | `worldguard.template_packs` | central schema validator, builder consumer | projection adapter from explicit target slot-type map | closed JSON object; unknown slot type blocks instead of being guessed |
| `template.artifacts[].artifact_id`, `template.artifacts[].path_template`, `template.artifacts[].content_template_hash` | `worldguard.template_packs` | central manifest/instance checks | projection adapter | portable generated path; content hash binds native manifest fingerprint |
| `template.builder.builder_id`, `template.builder.entrypoint`, `template.builder.content_hash` | `worldguard.template_packs` | central instance checks | projection adapter | portable native builder entrypoint and implementation fingerprint |
| `template.validators[].validator_id`, `template.validators[].check_id`, `template.validators[].evidence_domain`, `template.validators[].content_hash` | WorldGuard native validator registry | central manifest/check supervision | projection adapter | exact native validator/check/domain and implementation fingerprint |
| `template.prompt_fragments[].fragment_id`, `template.prompt_fragments[].content_hash` | `worldguard.template_packs` | central manifest validator | projection adapter | empty for current non-prompt packs; no generated prompt authority |
| `template.protected_failure_ids[]` | `worldguard.template_packs` | central fixture validator | projection adapter | target-owned projection integrity failures only |
| `template.fixtures.known_good_ids`, `template.fixtures.known_bad_by_failure`, `template.fixtures.ambiguity_ids`, `template.fixtures.stale_ids` | `worldguard.template_packs` | native check, central fixture validator | projection adapter | exact target-owned regression ids; bad keys equal protected failures |
| `template.claim_boundary` | WorldGuard pack author | central receipts, reports | projection adapter | construction/projection integrity only |
| `applicability[].template_id`, `applicability[].eligible` | `worldguard.template_packs` | central applicability validator/selector | projection adapter from current native selector | one row per catalog member; boolean equals native match/base outcome |
| `applicability[].predicate_evidence_ids`, `applicability[].forbidden_clearance_evidence_ids`, `applicability[].reasons` | `worldguard.template_packs` | central applicability validator | projection adapter from exact fact-set membership and native outcome | eligible rows carry native evidence; rejected rows carry explicit reasons |

## Existing Field Disposition

- `guard_purpose_declarations`, `guard_purpose_contract`, `selected_failure_ids`, and native proof fields remain owned by `worldguard.guard_model_contract`; templates only carry caller-authored declarations through explicit slots.
- `claim.target_guards` and claim-derived Guard routes remain owned by `worldguard.contracts`; template applicability facts cannot shrink the derived set.
- `semantic_coverage` remains owned by `worldguard.mesh`; ModelMesh templates scaffold its fields but do not decide adequacy or predictive license.
- SkillGuard `native_check_ids`, owner receipts, and closure fields remain target-neutral supervision fields and never become template semantics.
- Central SkillGuard `catalog_digest`, `manifest_digest`, native-route receipt hashes, and applicability receipt hashes are downstream neutral seals. WorldGuard neither accepts them as native applicability input nor emits them in the target projection.

## Handoffs

- Manifest/selection/composition projections go to the executable `.flowguard/worldguard_template_pack_builder.py` model.
- Canonical instance dictionaries go to existing `GuardContract.from_dict` or `ModelMeshContract.from_dict` and task-purpose proof.
- Focused cases go to `tests/test_template_packs.py`; malformed combinations cover stale, unknown-validator, ambiguous, ownership-conflict, missing-slot, and unused-slot families.
- Neutral projection cases in `tests/test_template_packs.py` cover good central shape, unknown root, exact native candidate equality, wrong route, and stale native registry identity.
- Development freshness and verification owners go to `.flowguard/worldguard_template_pack_development_process.md` and the OpenSpec verification contract.
