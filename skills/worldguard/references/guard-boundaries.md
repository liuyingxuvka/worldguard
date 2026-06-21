# Guard Boundaries

## EventGuard

Owns event, timepoint, fluent persistence, initiation, termination, clipping, and exclusive fluent conflicts.

Outputs `BOUNDARY_EXCEEDED` for continuous numeric dynamics, physical equations, causality, norms, or resource enablement.

## AgentGuard

Owns BDI-style belief, desire, intention, capability, and intention conflict checks.

Outputs `BOUNDARY_EXCEEDED` for payoff equilibrium, causal effects, resource tokens, or deontic permission.

## SpaceGuard

Owns qualitative RCC8 spatial relations and consistency.

Outputs `BOUNDARY_EXCEEDED` for metric distance, continuous geometry, sensor fusion, or dynamics.

## ResourceGuard

Owns Colored Petri Net resources, places, tokens, transitions, capacity, and enablement.

Outputs `BOUNDARY_EXCEEDED` for norms, permission, real physics, market price, or causality.

## CausalGuard

Owns SCM variables, structural equations, graph consistency, and do/counterfactual queries.

Outputs `BOUNDARY_EXCEEDED` for temporal story-only evidence, norms, resources, or game payoff claims.

## ConflictGuard

Owns players, states, actions, policies, probabilities, payoffs, and game-strategy contradictions.

Outputs `BOUNDARY_EXCEEDED` for deontic obligation, permission, physical resource enablement, or SCM causality.

## NormGuard

Owns obligation, permission, forbidden action, violation, and norm conflict checks.

Outputs `BOUNDARY_EXCEEDED` for physical enablement, resource token availability, payoff optimality, or causal effect.
