from .agent_guard import run as run_agent_guard
from .causal_guard import run as run_causal_guard
from .conflict_guard import run as run_conflict_guard
from .event_guard import run as run_event_guard
from .norm_guard import run as run_norm_guard
from .resource_guard import run as run_resource_guard
from .space_guard import run as run_space_guard

GUARD_RUNNERS = {
    "EventGuard": run_event_guard,
    "AgentGuard": run_agent_guard,
    "SpaceGuard": run_space_guard,
    "ResourceGuard": run_resource_guard,
    "CausalGuard": run_causal_guard,
    "ConflictGuard": run_conflict_guard,
    "NormGuard": run_norm_guard,
}

__all__ = ["GUARD_RUNNERS"]
