from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .contracts import GuardContract
from .fact_revision import (
    FactRevisionActivationRequest,
    FactRevisionTransaction,
    FactWorldSnapshot,
    activate_fact_revision,
    preview_fact_revision,
)
from .examples.fuel_cell import run_check as run_fuel_cell_check
from .io import dump_json, load_mapping
from .kernel import run_worldguard
from .mesh import ModelMeshContract, run_model_mesh
from .task_local_revision import (
    CandidateWorldModelRevision,
    ObservedWorldSnapshot,
    PredictionSnapshot,
    RevalidationRole,
    WorldModelIdentity,
    bind_semantic_rollout_receipt,
    bind_task_local_native_depth_receipt,
    bind_world_revalidation_receipt,
    compare_observed_world,
    evaluate_candidate_world_revision,
    freeze_prediction_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="worldguard")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--contract", default="")
    check.add_argument("--example", choices=["fuel_cell"], default="")
    mesh_check = subparsers.add_parser("mesh-check")
    mesh_check.add_argument("--mesh", required=True)
    task_model = subparsers.add_parser(
        "task-model",
        help="freeze, compare, and reversibly evaluate one task-local world model",
    )
    task_model_commands = task_model.add_subparsers(
        dest="task_model_command",
        required=True,
    )
    task_model_freeze = task_model_commands.add_parser(
        "freeze",
        help="freeze a prediction against the exact current task model",
    )
    task_model_freeze.add_argument("prediction")
    task_model_compare = task_model_commands.add_parser(
        "compare",
        help="compare one later real observation with a frozen prediction",
    )
    task_model_compare.add_argument("prediction")
    task_model_compare.add_argument("observation")
    task_model_depth_bind = task_model_commands.add_parser(
        "depth-bind",
        help="bind one exact native execution-depth receipt to the current task and candidate",
    )
    task_model_depth_bind.add_argument("prediction")
    task_model_depth_bind.add_argument("candidate_model")
    task_model_depth_bind.add_argument("native_depth")
    task_model_depth_bind.add_argument("--binding-id", required=True)
    task_model_revalidation_bind = task_model_commands.add_parser(
        "revalidation-bind",
        help="bind typed semantic and empirical evidence for one original or real-holdout role",
    )
    task_model_revalidation_bind.add_argument("prediction")
    task_model_revalidation_bind.add_argument("candidate_model")
    task_model_revalidation_bind.add_argument(
        "role",
        choices=[item.value for item in RevalidationRole],
    )
    task_model_revalidation_bind.add_argument("semantic_result")
    task_model_revalidation_bind.add_argument("comparison")
    task_model_revalidation_bind.add_argument("--check-id", required=True)
    task_model_revalidation_bind.add_argument("--semantic-receipt-id", required=True)
    task_model_revalidation_bind.add_argument("--semantic-status", required=True)
    task_model_revalidation_bind.add_argument("--evidence-ref", required=True)
    task_model_revision = task_model_commands.add_parser(
        "revision",
        help="accept, reject, or roll back a separate candidate task model",
    )
    task_model_revision.add_argument("revision")
    fact_revision_preview = task_model_commands.add_parser(
        "fact-revision-preview",
        help="preview a four-valued fact revision without mutating its base",
    )
    fact_revision_preview.add_argument("base")
    fact_revision_preview.add_argument("transaction")
    fact_revision_activate = task_model_commands.add_parser(
        "fact-revision-activate",
        help="activate one current preview with regression and holdout evidence",
    )
    fact_revision_activate.add_argument("base")
    fact_revision_activate.add_argument("transaction")
    fact_revision_activate.add_argument("activation")

    args = parser.parse_args(argv)
    if args.command == "check":
        if args.example == "fuel_cell":
            print(dump_json(run_fuel_cell_check()))
            return 0
        if not args.contract:
            parser.error("check requires --contract or --example fuel_cell")
        contract = GuardContract.from_dict(load_mapping(args.contract))
        print(dump_json(run_worldguard(contract).to_dict()))
        return 0
    if args.command == "mesh-check":
        mesh = ModelMeshContract.from_dict(load_mapping(args.mesh))
        print(dump_json(run_model_mesh(mesh).to_dict()))
        return 0
    if args.command == "task-model":
        if args.task_model_command == "depth-bind":
            prediction_path = Path(args.prediction)
            prediction = PredictionSnapshot.from_dict(load_mapping(prediction_path))
            candidate = WorldModelIdentity.from_dict(load_mapping(args.candidate_model))
            native_payload = load_mapping(args.native_depth)
            if "depth_receipt" in native_payload:
                depth_receipt = native_payload.get("depth_receipt")
                if not isinstance(depth_receipt, dict):
                    raise ValueError("native mesh report depth_receipt must be a mapping")
            else:
                depth_receipt = native_payload
            receipt = bind_task_local_native_depth_receipt(
                prediction,
                candidate,
                depth_receipt,
                base_dir=prediction_path.parent,
                binding_id=args.binding_id,
            )
            print(dump_json(receipt))
            return 0
        if args.task_model_command == "revalidation-bind":
            prediction = PredictionSnapshot.from_dict(load_mapping(args.prediction))
            candidate = WorldModelIdentity.from_dict(load_mapping(args.candidate_model))
            semantic = bind_semantic_rollout_receipt(
                receipt_id=args.semantic_receipt_id,
                task_id=prediction.task_id,
                role=args.role,
                candidate_model=candidate,
                semantic_status=args.semantic_status,
                source_result=load_mapping(args.semantic_result),
                evidence_ref=args.evidence_ref,
            )
            receipt = bind_world_revalidation_receipt(
                check_id=args.check_id,
                role=args.role,
                candidate_model=candidate,
                semantic_receipt=semantic,
                empirical_comparison=load_mapping(args.comparison),
            )
            print(dump_json(receipt))
            return 0
        if args.task_model_command == "fact-revision-preview":
            base = FactWorldSnapshot.from_dict(load_mapping(args.base))
            transaction = FactRevisionTransaction.from_dict(
                load_mapping(args.transaction)
            )
            preview = preview_fact_revision(base, transaction)
            print(dump_json(preview.to_dict()))
            return 0 if preview.status == "ready" else 1
        if args.task_model_command == "fact-revision-activate":
            base = FactWorldSnapshot.from_dict(load_mapping(args.base))
            transaction = FactRevisionTransaction.from_dict(
                load_mapping(args.transaction)
            )
            activation = FactRevisionActivationRequest.from_dict(
                load_mapping(args.activation)
            )
            result = activate_fact_revision(base, transaction, activation)
            print(dump_json(result.to_dict()))
            return 0 if result.receipt.activated else 1
        if args.task_model_command == "freeze":
            path = Path(args.prediction)
            prediction = PredictionSnapshot.from_dict(load_mapping(path))
            receipt = freeze_prediction_snapshot(prediction, base_dir=path.parent)
        elif args.task_model_command == "compare":
            prediction_path = Path(args.prediction)
            prediction = PredictionSnapshot.from_dict(load_mapping(prediction_path))
            observation = ObservedWorldSnapshot.from_dict(
                load_mapping(args.observation)
            )
            receipt = compare_observed_world(
                prediction,
                observation,
                base_dir=prediction_path.parent,
            )
        else:
            path = Path(args.revision)
            revision = CandidateWorldModelRevision.from_dict(load_mapping(path))
            receipt = evaluate_candidate_world_revision(
                revision,
                base_dir=path.parent,
            )
        print(dump_json(receipt))
        return 0 if receipt["status"] == "pass" else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
