from __future__ import annotations

import argparse
import sys

from .contracts import GuardContract
from .examples.fuel_cell import run_check as run_fuel_cell_check
from .io import dump_json, load_mapping
from .kernel import run_worldguard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="worldguard")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--contract", default="")
    check.add_argument("--example", choices=["fuel_cell"], default="")

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
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
