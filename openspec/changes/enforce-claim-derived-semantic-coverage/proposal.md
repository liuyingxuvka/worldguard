## Why

WorldGuard now separates structural checks from semantic execution, but a single event or one parseable equation can still produce semantic `PASS` when the caller narrows `target_guards` or omits required mesh children. Prediction claims need claim-derived semantic coverage and explicit rollout adequacy rather than only field completeness inside the submitted subset.

## What Changes

- Decompose structured claim atoms into required Guards and semantic routes, and fail closed when caller-declared targets omit a required route.
- Require every Guard to declare the invalid claim class it prevents and its unsupported boundary; a wired but purpose-free Guard is not adequate.
- Derive a finite target-owned inventory from every literal Guard-runner and per-Guard semantic failure code, require one native good per Guard and exactly one native bad per failure class, and verify exact status/code reactions.
- Fix CausalGuard so a non-empty but partial structural-equation map remains a concrete `GAP`.
- Declare and fingerprint expected model nodes, scenarios, time horizon, branches, perturbations, and claim scope in the native depth receipt.
- Turn required contractless or skipped model nodes into visible `GAP` evidence instead of silently omitting them.
- Add predictive rollout requirements for horizon, states, transitions, interventions, counterfactuals, holdout evidence, and executed rollout semantics.
- Add a target-owned representative-timepoint floor (count plus ratio) and non-replaceable native early/middle/late strata, so a 1,000-step horizon cannot pass from one or two points or many points concentrated in one phase.
- Evaluate predictive depth per expected model node so a richly covered aggregate cannot hide one shallow child/object.
- Keep single-event and single-equation checks available as bounded local checks while preventing broad predictive licensing.
- Bind current generic SkillGuard supervision to WorldGuard's exact declared native checks; SkillGuard freezes execution identity but does not own Guard purposes, fixtures, failure classes, or oracle meaning.
- Retire the target-native `closure_profile` field and CLI selector. Current WorldGuard always executes required semantics; a caller cannot choose a structural-only path that skips them.
- Expose WorldGuard's existing native routes and checks through the current contract's top-level native bindings so the global router can see the same target-owned authority without inventing a parallel route.
- Add shallow negatives for two-of-1,000 points, caller-renamed one-phase strata, and high aggregate coverage with one shallow model node.
- Discover every semantic or predictive mesh node from the current mesh before checking the caller's expected list; treat that list as a completeness assertion rather than permission to shrink the denominator.
- Preserve explicit model-node exclusions with reasons and closed dispositions, and prevent excluded nodes from contributing semantic, predictive, or claim-scope evidence.
- Project the WorldGuard-owned per-object dynamic temporal floor into SkillGuard instead of duplicating a fixed one-percent policy.
- When a model node exposes variables or signals, build a separate temporal child universe for every variable/signal so node-level time coverage cannot hide a shallow internal series.

## Capabilities

### New Capabilities

- `claim-derived-semantic-coverage`: Claim-atom routing, expected semantic-child coverage, predictive adequacy, and quantitative native depth receipts.

### Modified Capabilities

- `semantic-rollout-status`: Semantic `PASS` is separated from broad predictive readiness and contractless/skipped required nodes remain visible in aggregate status and receipts.

## Impact

- Affected runtime: WorldGuard contracts, mesh normalization/aggregation, semantic executors, CLI serialization, and public exports.
- Affected guidance: WorldGuard skill and contract/mesh/closure references plus current generic SkillGuard declared-check bindings.
- Affected evidence: Guard-model finite exhaustion child, focused native good/bad and partial-equation tests, existing FlowGuard process model, OpenSpec verification contract, and later parent-owned full regression evidence.
- Bounded local semantic conclusions remain supported, but the former structural-only selector is rejected and has no compatibility or fallback route.
