from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .dataset import DATASET_SPLITS, DatasetRecord, record_group_key

FINAL_SPLITS = {"train", "validation", "test"}
UNCERTAIN_VALUES = {"", "unknown", "unverified", "pending", "unclear", "not_set", "n/a"}


def _uncertain(value: str | None) -> bool:
    return value is None or value.strip().casefold() in UNCERTAIN_VALUES


@dataclass(frozen=True)
class DatasetAuditReport:
    total_records: int
    split_counts: dict[str, int]
    label_counts: dict[str, int]
    split_label_counts: dict[str, dict[str, int]]
    leakage_groups: dict[str, tuple[str, ...]]
    unresolved_rights_record_ids: tuple[str, ...]
    unresolved_provenance_record_ids: tuple[str, ...]
    unresolved_consent_record_ids: tuple[str, ...]
    missing_group_context_record_ids: tuple[str, ...]
    duplicate_media_paths: tuple[str, ...]
    unassigned_record_ids: tuple[str, ...]
    strict_ok: bool

    def to_dict(self) -> dict:
        return asdict(self)


def audit_records(records: Iterable[DatasetRecord]) -> DatasetAuditReport:
    records = list(records)
    for record in records:
        record.validate()

    split_counts = Counter(record.split for record in records)
    for split in DATASET_SPLITS:
        split_counts.setdefault(split, 0)

    label_counts = Counter(record.label for record in records)
    split_label_counts: dict[str, Counter] = defaultdict(Counter)
    for record in records:
        split_label_counts[record.split][record.label] += 1

    group_splits: dict[str, set[str]] = defaultdict(set)
    for record in records:
        if record.split in FINAL_SPLITS:
            group_splits[record_group_key(record)].add(record.split)
    leakage_groups = {
        group: tuple(sorted(splits))
        for group, splits in sorted(group_splits.items())
        if len(splits) > 1
    }

    rights = tuple(sorted(
        record.record_id for record in records if _uncertain(record.rights_basis)
    ))
    provenance = tuple(sorted(
        record.record_id for record in records if _uncertain(record.provenance)
    ))
    consent = tuple(sorted(
        record.record_id for record in records if _uncertain(record.consent_status)
    ))

    missing_group = tuple(sorted(
        record.record_id
        for record in records
        if record.split in FINAL_SPLITS
        and not any([
            (record.group_id or "").strip(),
            (record.source_media_path or "").strip(),
            (record.job_reference or "").strip(),
        ])
    ))

    media_path_counts = Counter(record.media_path for record in records)
    duplicate_media_paths = tuple(sorted(
        path for path, count in media_path_counts.items() if count > 1
    ))
    unassigned = tuple(sorted(
        record.record_id for record in records if record.split == "unassigned"
    ))

    strict_ok = not any([
        leakage_groups,
        rights,
        provenance,
        consent,
        missing_group,
        duplicate_media_paths,
        unassigned,
    ])

    return DatasetAuditReport(
        total_records=len(records),
        split_counts=dict(sorted(split_counts.items())),
        label_counts=dict(sorted(label_counts.items())),
        split_label_counts={
            split: dict(sorted(counts.items()))
            for split, counts in sorted(split_label_counts.items())
        },
        leakage_groups=leakage_groups,
        unresolved_rights_record_ids=rights,
        unresolved_provenance_record_ids=provenance,
        unresolved_consent_record_ids=consent,
        missing_group_context_record_ids=missing_group,
        duplicate_media_paths=duplicate_media_paths,
        unassigned_record_ids=unassigned,
        strict_ok=strict_ok,
    )


def audit_manifest(path: str | Path) -> DatasetAuditReport:
    from .dataset import read_manifest

    return audit_records(read_manifest(path))
