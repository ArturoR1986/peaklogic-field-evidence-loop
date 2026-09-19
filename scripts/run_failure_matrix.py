from __future__ import annotations

import argparse
import json
from pathlib import Path

from peaklogic_field_evidence.failure_matrix import run_failure_matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()

    results = run_failure_matrix()
    payload = {
        "passed": sum(1 for r in results if r.passed),
        "total": len(results),
        "all_passed": all(r.passed for r in results),
        "cases": [r.to_dict() for r in results],
        "evidence_note": (
            "These are deterministic failure-handling mechanics tests. They are not "
            "representative vision-performance evidence."
        ),
    }
    rendered = json.dumps(payload, indent=2)
    print(rendered)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
