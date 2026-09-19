from __future__ import annotations

import argparse
import json
from pathlib import Path

from peaklogic_field_evidence.dataset_audit import audit_manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit a dataset manifest for split leakage, rights, provenance, and grouping gaps."
    )
    parser.add_argument("manifest")
    parser.add_argument("--output")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when any leakage, unresolved rights/provenance/consent, unassigned record, duplicate path, or missing group context remains.",
    )
    args = parser.parse_args()

    report = audit_manifest(args.manifest)
    rendered = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    print(rendered)

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")

    return 1 if args.strict and not report.strict_ok else 0


if __name__ == "__main__":
    raise SystemExit(main())
