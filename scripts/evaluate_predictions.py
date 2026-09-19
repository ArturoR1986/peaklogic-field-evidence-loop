from __future__ import annotations

import argparse
import json
from pathlib import Path

from peaklogic_field_evidence.dataset import PROOF_POINT_LABELS
from peaklogic_field_evidence.evaluation import classification_metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate truth/prediction JSONL without external ML metric dependencies."
    )
    parser.add_argument("predictions", help="JSONL with truth and prediction fields")
    args = parser.parse_args()

    truth, pred = [], []
    with Path(args.predictions).open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            try:
                truth.append(row["truth"])
                pred.append(row["prediction"])
            except KeyError as exc:
                raise ValueError(f"missing {exc.args[0]} on line {line_number}") from exc

    result = classification_metrics(truth, pred, labels=PROOF_POINT_LABELS)
    payload = {
        "count": len(truth),
        "accuracy": result.accuracy,
        "macro_f1": result.macro_f1,
        "labels": result.labels,
        "confusion_matrix": result.confusion_matrix,
        "per_class": {
            label: {
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1": metrics.f1,
                "support": metrics.support,
            }
            for label, metrics in result.per_class.items()
        },
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
