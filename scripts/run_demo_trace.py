from __future__ import annotations

import argparse
import json

from peaklogic_field_evidence.demo import run_trace_demo


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", default="outputs/agentic_trace_demo.jsonl")
    args = parser.parse_args()
    print(json.dumps(run_trace_demo(args.trace), indent=2))


if __name__ == "__main__":
    main()
