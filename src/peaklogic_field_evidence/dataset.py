from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable

PROOF_POINT_LABELS = (
    "location_context",
    "product_identification",
    "substrate_context",
    "critical_attachment",
    "process_before_cover",
    "finished_detail",
    "finished_context",
    "unsupported",
)
DATASET_SPLITS = ("train", "validation", "test", "unassigned")


@dataclass(frozen=True)
class DatasetRecord:
    record_id: str
    media_path: str
    media_type: str
    label: str
    split: str = "unassigned"
    source_media_path: str | None = None
    source_timestamp_seconds: float | None = None
    provenance: str = "user_provided_or_staged"
    rights_basis: str = "owned_or_authorized"
    consent_status: str = "not_applicable_or_confirmed"
    job_reference: str | None = None
    notes: str = ""

    def validate(self) -> None:
        if self.label not in PROOF_POINT_LABELS:
            raise ValueError(f"Unsupported proof-point label: {self.label}")
        if self.split not in DATASET_SPLITS:
            raise ValueError(f"Unsupported dataset split: {self.split}")
        if self.media_type not in {"photo", "video_frame"}:
            raise ValueError(f"Unsupported media type: {self.media_type}")
        if not self.record_id.strip():
            raise ValueError("record_id is required")
        if not self.media_path.strip():
            raise ValueError("media_path is required")

    def to_dict(self) -> dict:
        self.validate()
        return asdict(self)


def write_manifest(records: Iterable[DatasetRecord], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            record.validate()
            if record.record_id in seen:
                raise ValueError(f"Duplicate record_id: {record.record_id}")
            seen.add(record.record_id)
            fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    return path


def read_manifest(path: str | Path) -> list[DatasetRecord]:
    records: list[DatasetRecord] = []
    seen: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            raw = json.loads(line)
            record = DatasetRecord(**raw)
            record.validate()
            if record.record_id in seen:
                raise ValueError(f"Duplicate record_id on line {line_number}: {record.record_id}")
            seen.add(record.record_id)
            records.append(record)
    return records
