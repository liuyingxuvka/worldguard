"""WorldGuard public runtime API."""

from .contracts import (
    ClaimAtom,
    GuardContract,
    GuardPurposeContractBinding,
    claim_predictive_intent,
    derive_required_guards,
)
from .kernel import run_worldguard
from .mesh import ModelMeshContract, MeshReport, SemanticCoverageContract, run_model_mesh
from .reports import GuardResult, GuardedReport
from .semantic import (
    EXECUTOR_REGISTRY,
    NativeDepthReceipt,
    ProviderStatus,
    SemanticBinding,
    SemanticExecutionReceipt,
    SemanticStatus,
)
from .status import GuardStatus

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "GuardContract",
    "GuardPurposeContractBinding",
    "ClaimAtom",
    "GuardResult",
    "GuardStatus",
    "GuardedReport",
    "MeshReport",
    "ModelMeshContract",
    "SemanticCoverageContract",
    "NativeDepthReceipt",
    "ProviderStatus",
    "SemanticBinding",
    "SemanticExecutionReceipt",
    "SemanticStatus",
    "EXECUTOR_REGISTRY",
    "run_model_mesh",
    "run_worldguard",
    "claim_predictive_intent",
    "derive_required_guards",
]
