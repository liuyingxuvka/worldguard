import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--example", choices=["fuel_cell"], default="")
    parser.add_argument("--contract", default="")
    args = parser.parse_args()

    try:
        if args.example == "fuel_cell":
            from worldguard.examples.fuel_cell import run_check

            result = run_check()
        elif args.contract:
            from worldguard.contracts import GuardContract
            from worldguard.io import load_mapping
            from worldguard.kernel import run_worldguard

            result = run_worldguard(GuardContract.from_dict(load_mapping(args.contract))).to_dict()
        else:
            parser.error("provide --example fuel_cell or --contract <path>")
            return 2
    except Exception as exc:  # pragma: no cover - helper script surface
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
